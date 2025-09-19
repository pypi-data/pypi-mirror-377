from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
import asyncio
import json
from threading import Thread
import uuid

from fastmcp import Client as FastMCPClient
from fastmcp.exceptions import ToolError
from mcp import Tool
from mcp.types import (
    CallToolRequestParams,TextContent, ImageContent, AudioContent, EmbeddedResource
)

from benchmax.envs.base_env import BaseEnv, ToolDefinition
from benchmax.envs.bounded_dict import BoundedDict

@dataclass
class ClientWorkspacePair:
    """A pair of FastMCP client and its associated workspace.
    
    The client and workspace are kept together to ensure proper lifecycle management
    and to support workspace independence from rollout IDs. This allows pre-warming
    with arbitrary workspaces and matching them to rollouts later.
    """
    client: FastMCPClient | None
    workspace: Path

class LocalMCPEnv(BaseEnv):
    """Local MCP environment implementation supporting workspace-independent client pooling.
    
    This implementation maintains a pool of pre-warmed clients, each with their own
    workspace. When a rollout needs a client, it will retrieve from the pool and
    reconfigure the workspace as needed. This allows for:
    1. Independent workspace and rollout management
    2. Pre-warming with arbitrary workspaces
    3. Efficient client reuse via pooling
    """
    def __init__(
        self,
        mcp_config: Union[Dict[str, Any], str, Path],
        allowed_tools: Optional[List[str]] = None,
        pool_size: int = 3,
        workspace_dir: Optional[Path] = None
    ) -> None:
        """Initialize the environment with configuration and pool settings."""
        # Load config from file if path provided
        if isinstance(mcp_config, (str, Path)):
            mcp_config_path = Path(mcp_config)
            if not mcp_config_path.exists() and isinstance(mcp_config, str):
                self._config = json.loads(mcp_config)
            else:
                with open(mcp_config) as f:
                    self._config = json.load(f)
        else:
            self._config = mcp_config
        self._allowed_tools = allowed_tools if allowed_tools is not None else []
        self._pool_size = pool_size
        self._output_parsers: Dict[str, Callable[[str], Any]] = {}
        self._workspace_dir = workspace_dir or Path("workspaces")
        self._workspace_dir.mkdir(parents=True, exist_ok=True)

        self._pre_warmed_pool: List[ClientWorkspacePair] = []  # Available pre-initialized pairs
        self._active_clients: BoundedDict[str, ClientWorkspacePair] = BoundedDict(10000)  # rollout_id -> pair mapping
        self._tool_definitions: Optional[List[ToolDefinition]] = None
        
        # Set up event loop in a separate thread
        self._loop = asyncio.new_event_loop()
        self._loop_thread = Thread(target=self._run_event_loop)
        self._loop_thread.daemon = True
        self._loop_thread.start()
        
        # Initialize pre-warmed pool
        self._run_async(self._init_pool())
        
        super().__init__()

    # ---- Public API Methods ----
    def shutdown(self) -> None:
        """Clean up resources and stop the event loop."""
        # Close all active clients
        for rollout_id in list(self._active_clients.keys()):
            self.cleanup_rollout(rollout_id, keep_workspace=False)
        
        # Close pre-warmed pool
        for pair in self._pre_warmed_pool:
            if pair.client:
                self._run_async(pair.client.close())
        self._pre_warmed_pool.clear()
        
        # Stop the event loop
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._loop_thread.join()
        self._loop.close()
    
    def list_tools(self) -> List[ToolDefinition]:
        """List available tools, using cached definitions if available"""
        if self._tool_definitions is not None:
            return self._tool_definitions

        # Check if there are already pre-warmed clients with tool definitions
        if self._pre_warmed_pool:
            # Use the first client in the pool to get tool definitions
            pair = self._pre_warmed_pool[0]
            try:
                assert pair.client
                tools = self._run_async(pair.client.list_tools())
                self._tool_definitions = self._convert_and_filter_tools(tools)
                return self._tool_definitions
            except Exception as e:
                print(f"[ERROR] Failed to list tools: {str(e)}")
                return []
            
        # Else, create a new client to fetch tools and then add them to the pool
        try:
            pair = self._run_async(self._create_client_workspace())
            assert pair.client
            tools = self._run_async(pair.client.list_tools())
            self._tool_definitions = self._convert_and_filter_tools(tools)
            # Add the client to the pre-warmed pool
            self._pre_warmed_pool.append(pair)
            return self._tool_definitions
        except Exception as e:
            print(f"[ERROR] Failed to list tools: {str(e)}")
            return []

    def run_tool(self, rollout_id: str, tool_name: str, **tool_args) -> Any:
        """Execute a tool in the context of a specific rollout"""
        if rollout_id not in self._active_clients:
            self.init_rollout(rollout_id)

        pair = self._active_clients[rollout_id]
        assert pair.client
        
        # Create tool request params
        params = CallToolRequestParams(
            name=tool_name,
            arguments=tool_args if tool_args else None
        )

        try:
            # Call tool and get result
            content_list = self._run_async(pair.client.call_tool(tool_name, params.arguments)).content

            # Process content based on type
            for content in content_list:
                # Text content
                if isinstance(content, TextContent):
                    result = content.text
                
                # Image content
                elif isinstance(content, ImageContent):
                    result = {
                        "type": "image",
                        "data": content.data,
                        "mimeType": content.mimeType
                    }
                
                # Audio content
                elif isinstance(content, AudioContent):
                    result = {
                        "type": "audio",
                        "data": content.data,
                        "mimeType": content.mimeType
                    }
                
                # Resource content
                elif isinstance(content, EmbeddedResource):
                    resource = content.resource
                    if isinstance(resource, TextContent):
                        result = resource.text
                    else:
                        result = None
                else:
                    result = None

                # Apply output parser if available
                if tool_name in self._output_parsers and isinstance(result, str):
                    return self._output_parsers[tool_name](result)
                return result
            
        except ToolError as e:
            print(f"[ERROR] Tool call returned error: {str(e)}")
            return None
        except Exception as e:
            print(f"[ERROR] Tool call failed: {str(e)}")
            return None

    def init_rollout(self, rollout_id: str, **rollout_args) -> None:
        """Initialize resources for a new rollout"""
        pair = self._run_async(self._get_client_workspace_pair())
        self._active_clients[rollout_id] = pair

    def cleanup_rollout(self, rollout_id: str, keep_workspace=True) -> None:
        """
        Clean up resources associated with a specific rollout.

        This method closes and releases the client associated with the given rollout ID.
        If `keep_workspace` is True, the client's workspace is preserved for potential
        post-rollout tasks such as reward computation. Otherwise, the entire client entry
        is removed from the internal registry.

        Args:
            rollout_id (str): Unique identifier for the rollout whose resources are to be cleaned up.
            keep_workspace (bool, optional): Whether to retain the workspace after closing the client.
                Defaults to True.

        Returns:
            None
        """
        if rollout_id in self._active_clients:
            pair = self._active_clients.get(rollout_id)
            if pair and pair.client:
                self._run_async(pair.client.close())
            if keep_workspace:
                # We keep the workspace for potential reuse
                # to allow reward computation or other post-rollout tasks
                self._active_clients[rollout_id].client = None
            else:
                self._active_clients.pop(rollout_id)

    def get_rollout_workspace(self, rollout_id: str, strict_check: bool = False) -> Path:
        """Get dedicated workspace path for a rollout"""
        if rollout_id in self._active_clients:
            return self._active_clients[rollout_id].workspace
        if strict_check:
            raise ValueError(f"No active client found for rollout {rollout_id}")
        else:
            return Path()
        
    def copy_to_workspace(
        self, rollout_id: str, src_path: Path, dst_filename: Optional[str] = None
    ) -> None:
        """Copy a file to the workspace for a specific rollout. If dst_filename is None, use the original filename."""
        if rollout_id not in self._active_clients:
            raise ValueError(f"No active client found for rollout {rollout_id}")
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source file {src_path} does not exist")
        
        pair = self._active_clients[rollout_id]
        dst_path = pair.workspace / (dst_filename or src_path.name)
        dst_path.write_bytes(src_path.read_bytes())

    def copy_from_workspace(
        self, rollout_id: str, src_filename: str, dst_path: Path
    ) -> None:
        """Copy a file from the workspace for a specific rollout"""
        if rollout_id not in self._active_clients:
            raise ValueError(f"No active client found for rollout {rollout_id}")
        
        pair = self._active_clients[rollout_id]
        src_path = pair.workspace / src_filename
        if not src_path.exists():
            raise FileNotFoundError(f"File {src_filename} not found in workspace {pair.workspace}")
        
        dst_path.write_bytes(src_path.read_bytes())

    # ---- Private Helper Methods ----

    def _run_event_loop(self) -> None:
        """Run the event loop in a separate thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def _run_async(self, coro):
        """Run a coroutine in the event loop thread and wait for its result."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
    
    async def _create_clients_parallel(self, count: int) -> None:
        """Create multiple clients in parallel and add them to the pool"""
        if count <= 0:
            return
            
        tasks = [self._create_client_workspace() for _ in range(count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, ClientWorkspacePair):
                self._pre_warmed_pool.append(result)
            else:
                print(f"[WARN] Failed to create client: {str(result)}")

    async def _init_pool(self) -> None:
        """Pre-warm the client pool up to the configured size in parallel"""
        needed = self._pool_size - len(self._pre_warmed_pool)
        await self._create_clients_parallel(needed)

    def _prepare_config(self, workspace: Path) -> Dict[str, Any]:
        """Create config with workspace for given rollout"""
        config = self._config.copy()
        if "mcpServers" in config:
            for server in config["mcpServers"].values():
                server["cwd"] = str(workspace)
        return config

    async def _create_client_workspace(self) -> ClientWorkspacePair:
        """Create a new FastMCP client with a unique workspace"""
        workspace = self._workspace_dir / uuid.uuid4().hex
        workspace.mkdir(parents=True, exist_ok=True)
        config = self._prepare_config(workspace)

        client = FastMCPClient(config)
        await client._connect()
        return ClientWorkspacePair(client=client, workspace=workspace)

    async def _get_client_workspace_pair(self) -> ClientWorkspacePair:
        """Get a client-workspace pair and replenish pool if needed"""
        if self._pre_warmed_pool:
            pair = self._pre_warmed_pool.pop()
            # Replenish pool asynchronously if needed
            needed = self._pool_size - len(self._pre_warmed_pool)
            if needed > 0:
                asyncio.create_task(self._create_clients_parallel(needed))
            return pair
                
        # Create new workspace and client if pool is empty
        return await self._create_client_workspace()

    def _convert_and_filter_tools(self, tools: List[Tool]) -> List[ToolDefinition]:
        """Convert Tool objects to ToolDefinition objects and filter based on allowed list."""
        # Convert Tool objects to ToolDefinition objects
        tool_definitions = [
            ToolDefinition(
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema
            )
            for tool in tools
        ]
        
        # Filter based on allowed tools if list is provided
        if not self._allowed_tools:
            return tool_definitions
        
        return [tool for tool in tool_definitions if tool.name in self._allowed_tools]
