import asyncio
import datetime
import aiohttp
import uuid
import tempfile
import shutil
from typing import Callable, List, Any, Optional, Dict
from pathlib import Path
from fastmcp import Client as FastMCPClient
from mcp.types import TextContent
from fastmcp.exceptions import ToolError
from mcp import Tool
import sky
import logging
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logging.getLogger('httpx').setLevel(logging.CRITICAL)
logging.getLogger('aiohttp').setLevel(logging.CRITICAL)
logging.getLogger('mcp.client.streamable_http').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests').setLevel(logging.CRITICAL)

from benchmax.envs.base_env import BaseEnv
from benchmax.envs.types import ToolDefinition

logger = logging.getLogger(__name__)

class RemoteSkypilotMcpEnv(BaseEnv):
    """Remote MCP Environment for managing tool execution and rollouts with a remote MCP server.
    Currently only supports running on Skypilot containers.
    """
    def __init__(
        self,
        workdir_path: str,
        num_nodes: int = 1,
        allowed_tools: Optional[List[str]] = None,
        output_parsers: Optional[Dict[str, Callable[[str], Any]]] = None,
        cluster_name: str = "benchmax-env-cluster",
        health_check_timeout: int = 300,  # 5 minutes
        health_check_interval: int = 5,  # 5 seconds
        launch_workers_on_init: bool = True,
        cloud: Optional[Any] = sky.Azure(),  # sky.Cloud instance
        cpus: str = "2+",
    ) -> None:
        """Initialize the environment with configuration and pool settings."""
        super().__init__()
        self._workdir_path = Path(workdir_path)
        self._num_nodes = num_nodes
        self._allowed_tools = allowed_tools or []
        self._output_parsers: Dict[str, Callable[[str], Any]] = output_parsers or {}
        self._cluster_name = cluster_name
        self._health_check_timeout = health_check_timeout
        self._health_check_interval = health_check_interval
        self._cloud = cloud
        self._cpus = cpus
        self._ports = ["8080"]  # MCP server port

        # Generate API token for worker authentication
        self._api_token = uuid.uuid4().hex
        
        # Generate unique cluster name with suffix
        unique_suffix = uuid.uuid4().hex[:8]
        self._full_cluster_name = f"{self._cluster_name}-{unique_suffix}"
        
        # Sync directory management
        self._sync_dir: Optional[Path] = None
        
        # Worker management
        self._client_pool: Dict[str, FastMCPClient] = {}
        self._available_workers: asyncio.Queue[str] = asyncio.Queue()
        self._rollout_to_worker: Dict[str, str] = {}
        self._worker_init_tasks: List[asyncio.Task] = []
        
        # HTTP session
        self._http_session = aiohttp.ClientSession()

        # Cached tool definitions
        self._tool_definitions: Optional[List[ToolDefinition]] = None

        # Launch workers and start initialization
        self.launch_workers_started = False
        if launch_workers_on_init:
            self.launch_workers()

    def _setup_sync_directory(self) -> Path:
        """Create temporary sync directory and copy required files."""
        # Create temporary directory
        self._sync_dir = Path(tempfile.mkdtemp(prefix="benchmax_skypilot_"))
        logger.info(f"Created sync directory: {self._sync_dir}")
        
        try:
            # Get the directory where this file is located
            current_file_dir = Path(__file__).parent  # inside remote_skypilot_mcp_server.py
            proxy_server_path = current_file_dir / "proxy_server.py"
            
            # Copy proxy_server.py
            if not proxy_server_path.exists():
                raise FileNotFoundError(f"proxy_server.py not found at {proxy_server_path}")
            
            shutil.copy2(proxy_server_path, self._sync_dir / "proxy_server.py")
            logger.debug(f"Copied proxy_server.py to sync directory")
            
            # Copy all contents from workdir_path
            if not self._workdir_path.exists():
                raise FileNotFoundError(f"Workdir path does not exist: {self._workdir_path}")
            
            if not self._workdir_path.is_dir():
                raise ValueError(f"Workdir path is not a directory: {self._workdir_path}")
            
            # Copy all contents
            for item in self._workdir_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, self._sync_dir / item.name)
                    logger.debug(f"Copied file {item.name} to sync directory")
                elif item.is_dir():
                    shutil.copytree(item, self._sync_dir / item.name)
                    logger.debug(f"Copied directory {item.name} to sync directory")
            
            # Validate required files exist
            reward_func_path = self._sync_dir / "reward_func.py"
            setup_sh_path = self._sync_dir / "setup.sh"
            mcp_config_path = self._sync_dir / "mcp_config.yaml"
            
            if not reward_func_path.exists():
                raise FileNotFoundError(f"reward_func.py not found in workdir: {self._workdir_path}")
            
            if not setup_sh_path.exists():
                raise FileNotFoundError(f"setup.sh not found in workdir: {self._workdir_path}")
            
            if not mcp_config_path.exists():
                raise FileNotFoundError(f"mcp_config.yaml not found in workdir: {self._workdir_path}")
            
            logger.info(f"Validated required files in sync directory")
            return self._sync_dir
            
        except Exception as e:
            # Clean up sync directory if setup fails
            if self._sync_dir and self._sync_dir.exists():
                shutil.rmtree(self._sync_dir, ignore_errors=True)
                self._sync_dir = None
            raise e

    def _cleanup_sync_directory(self) -> None:
        """Clean up the temporary sync directory."""
        if self._sync_dir and self._sync_dir.exists():
            try:
                shutil.rmtree(self._sync_dir)
                logger.info(f"Cleaned up sync directory: {self._sync_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up sync directory {self._sync_dir}: {e}")
            finally:
                self._sync_dir = None

    async def _init_worker(self, worker_ip: str) -> None:
        """Initialize a single worker: health check + FastMCP client + add to pool."""
        try:
            # Health check
            await self._wait_for_worker_health(worker_ip)
            
            # Initialize FastMCP client
            mcp_url = f"http://{worker_ip}:8080/mcp/"
            client = FastMCPClient(mcp_url)
            await client._connect()
            self._client_pool[worker_ip] = client
            
            # Add to available pool
            await self._available_workers.put(worker_ip)
            logger.debug(f"Worker {worker_ip} initialized and added to pool")
            
        except Exception as e:
            logger.error(f"Failed to initialize worker {worker_ip}: {e}")
            # Don't re-raise - let other workers continue

    async def _wait_for_worker_health(self, worker_ip: str) -> None:
        """Wait for worker to pass health check."""
        health_url = f"http://{worker_ip}:8080/health"
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self._health_check_timeout:
                raise TimeoutError(f"Health check timeout for worker {worker_ip}")
            
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with self._http_session.get(health_url, timeout=timeout) as response:
                    if response.status == 200:
                        logger.debug(f"Worker {worker_ip} is healthy")
                        return
                    else:
                        logger.debug(f"Worker {worker_ip} health check returned {response.status}")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.debug(f"Health check failed for {worker_ip}: {e}")

            await asyncio.sleep(self._health_check_interval)

    async def _get_available_worker(self) -> str:
        """Get an available worker, blocking until one is ready."""
        return await self._available_workers.get()

    async def _release_worker(self, worker_ip: str) -> None:
        """Return a worker to the available pool."""
        await self._available_workers.put(worker_ip)

    async def _call_worker_reset(self, worker_ip: str) -> None:
        """Call the reset endpoint on a specific worker."""
        reset_url = f"http://{worker_ip}:8080/reset"
        headers = {"Authorization": self._api_token}
        
        try:
            async with self._http_session.post(reset_url, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Reset successful for worker {worker_ip}")
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Reset failed for worker {worker_ip}: {response.status} - {error_text}")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Reset request failed for worker {worker_ip}: {e}")
        
    async def add_worker_back_once_available(self, worker_ip: str) -> None:
        """Add a worker back to the available pool once it passes health check."""
        await asyncio.sleep(1)  # brief delay before starting health checks

        try:
            await self._init_worker(worker_ip)
            logger.info(f"Worker {worker_ip} added back to available pool after reset")
        except Exception as e:
            logger.error(f"Failed to add worker {worker_ip} back to pool: {e}")
            # Don't re-raise - worker remains out of pool
    
    # Function is expected to be called at the end of compute_reward
    async def _cleanup_rollout(self, rollout_id: str) -> None:
        """Clean up rollout resources and return worker to pool."""
        if rollout_id not in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is not initialized")
        
        worker_ip = self._rollout_to_worker[rollout_id]
        logger.debug(f"Cleaning up rollout {rollout_id} on worker {worker_ip}")
        
        del self._rollout_to_worker[rollout_id]
        try:
            # Call reset endpoint
            await self._call_worker_reset(worker_ip)
        except Exception as e:
            logger.error(f"Failed to reset worker {worker_ip} for rollout {rollout_id}: {e}")

        # Disconnect the client
        client = self._client_pool.get(worker_ip)
        if client:
            await client._disconnect()
            self._client_pool.pop(worker_ip, None)

        # Start background task to add worker back once healthy
        asyncio.create_task(self.add_worker_back_once_available(worker_ip))

    def _convert_and_filter_tools(self, tools: List[Tool]) -> List[ToolDefinition]:
        """Convert Tool objects to ToolDefinition objects and filter based on allowed list."""
        tool_definitions = [
            ToolDefinition(
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema
            )
            for tool in tools
        ]
        
        if not self._allowed_tools:
            return tool_definitions
        
        return [tool for tool in tool_definitions if tool.name in self._allowed_tools]

    # ---- Public API Methods ----
    def launch_workers(self) -> None:
        """Launch SkyPilot workers synchronously with programmatically created task."""
        if self.launch_workers_started:
            raise RuntimeError("Workers have already been launched.")
        
        self.launch_workers_started = True
        
        try:
            # Setup sync directory and copy files
            sync_dir = self._setup_sync_directory()
            
            # Create the task programmatically
            task = sky.Task(
                name='fastmcp',
                setup='pip install fastmcp~=2.10.0\npip install pyyaml\nsh setup.sh',
                run='python proxy_server.py',
                workdir=str(sync_dir),
                num_nodes=self._num_nodes
            )
            
            # Set the resources
            task.set_resources(
                sky.Resources(
                    cloud=self._cloud,
                    cpus=self._cpus,
                    ports=self._ports
                )
            )
            
            # Update environment variables with API token
            task.update_envs({"API_TOKEN": self._api_token})
            
            # Launch the cluster
            _, handle = sky.launch(
                task=task, 
                cluster_name=self._full_cluster_name, 
                detach_run=True, 
                detach_setup=True, 
                retry_until_up=True
            )   
            
            if handle is None:
                raise RuntimeError("Failed to launch SkyPilot task.")
            
            worker_ips = [
                external_ip for _, external_ip in handle.stable_internal_external_ips
            ]
            logger.info(f"Launched workers with IPs: {worker_ips}")
            
            # Start background initialization for each worker
            for worker_ip in worker_ips:
                task = asyncio.create_task(self._init_worker(worker_ip))
                self._worker_init_tasks.append(task)
                
        except Exception as e:
            # Clean up sync directory if launch fails
            self._cleanup_sync_directory()
            raise e
    
    async def shutdown(self) -> None:
        """Clean up resources - stop all tasks and close clients."""
        try:
            # Cancel worker initialization tasks
            for task in self._worker_init_tasks:
                if not task.done():
                    task.cancel()
            
            if self._worker_init_tasks:
                results = await asyncio.gather(*self._worker_init_tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                        logger.error(f"Error in worker init task {i}: {result}")

            # Close FastMCP clients
            if self._client_pool:
                close_tasks = [client.close() for client in self._client_pool.values()]
                results = await asyncio.gather(*close_tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        worker_ip = list(self._client_pool.keys())[i]
                        logger.error(f"Error closing FastMCP client for {worker_ip}: {result}")

            # Close HTTP session
            await self._http_session.close()

            # Tear down SkyPilot cluster
            try:
                sky.down(cluster_name=self._full_cluster_name)
            except Exception as e:
                logger.error(f"Error tearing down SkyPilot cluster: {e}")
        
        finally:
            # Always clean up sync directory
            self._cleanup_sync_directory()

    async def list_tools(self) -> List[ToolDefinition]:
        """List available tools, using cached definitions if available."""
        if self._tool_definitions is not None:
            return self._tool_definitions

        # Get any available worker to fetch tools
        worker_ip = await self._get_available_worker()
        try:
            client = self._client_pool[worker_ip]
            tools = await client.list_tools()
            self._tool_definitions = self._convert_and_filter_tools(tools)
            return self._tool_definitions
        finally:
            await self._release_worker(worker_ip)

    async def init_rollout(self, rollout_id: str, **rollout_args) -> None:
        """Initialize resources for a new rollout - assigns a worker to the rollout."""
        if rollout_id in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is already initialized")
        
        # Get an available worker (blocks until one is ready)
        worker_ip = await self._get_available_worker()
        
        # Assign worker to rollout
        self._rollout_to_worker[rollout_id] = worker_ip
        logger.info(f"Rollout {rollout_id} assigned to worker {worker_ip}")

    async def run_tool(self, rollout_id: str, tool_name: str, **tool_args) -> Optional[str]:
        """Execute a tool in the context of a specific rollout."""
        if rollout_id not in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is not initialized. Call init_rollout() first.")
        
        worker_ip = self._rollout_to_worker[rollout_id]
        client = self._client_pool[worker_ip]
        
        try:
            content_list = (await client.call_tool(tool_name, tool_args, timeout=datetime.timedelta(seconds=30))).content
            text_content = []
            # Process content based on type
            for content in content_list:
                # Text content
                if isinstance(content, TextContent):
                    text_content.append(content.text)
                # Only process text content for now

            combined_text = "\n".join(text_content)
            # Apply output parser if available
            if tool_name in self._output_parsers and isinstance(combined_text, str):
                return self._output_parsers[tool_name](combined_text)

            return combined_text

        except ToolError as e:
            logger.error(f"[ERROR] Tool call returned error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[ERROR] Tool call failed: {str(e)}")
            return None

    async def copy_to_workspace(
        self, rollout_id: str, src_path: Path, dst_filename: Optional[str] = None
    ) -> None:
        """Copy a file to the workspace for a specific rollout."""
        if rollout_id not in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is not initialized")
        
        worker_ip = self._rollout_to_worker[rollout_id]
        upload_url = f"http://{worker_ip}:8080/upload"
        headers = {"Authorization": self._api_token}
        
        # Prepare file for upload
        filename = dst_filename or src_path.name
        
        try:
            with open(src_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=filename)
                
                async with self._http_session.post(upload_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        logger.info(f"File {src_path} uploaded as {filename} for rollout {rollout_id}")
                    else:
                        error_text = await response.text()
                        raise RuntimeError(f"Upload failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Failed to copy {src_path} to workspace for rollout {rollout_id}: {e}")
            raise

    async def copy_content_to_workspace(
        self, rollout_id: str, src_content: str | bytes, dst_filename: str, encoding: str = "utf-8"
    ) -> None:
        """Copy content (string or bytes) to the workspace for a specific rollout.

        Args:
            rollout_id: The rollout identifier.
            src_content: The content to upload (str or bytes).
            dst_filename: The filename to assign in the workspace.
            encoding: Encoding to use if src_content is str. Defaults to UTF-8.
        """
        if rollout_id not in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is not initialized")
        
        worker_ip = self._rollout_to_worker[rollout_id]
        upload_url = f"http://{worker_ip}:8080/upload"
        headers = {"Authorization": self._api_token}

        try:
            if isinstance(src_content, str):
                file_bytes = src_content.encode(encoding)
                content_type = "text/plain"
            else:
                file_bytes = src_content
                content_type = "application/octet-stream"

            data = aiohttp.FormData()
            data.add_field(
                "file",
                file_bytes,
                filename=dst_filename,
                content_type=content_type,
            )

            async with self._http_session.post(upload_url, headers=headers, data=data) as response:
                if response.status == 200:
                    logger.info(f"Content uploaded as {dst_filename} for rollout {rollout_id}")
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Upload failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Failed to upload content to workspace for rollout {rollout_id}: {e}")
            raise


    async def copy_from_workspace(
        self, rollout_id: str, src_filename: str, dst_path: Path
    ) -> None:
        """Copy a file from the workspace for a specific rollout."""
        if rollout_id not in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is not initialized")
        
        worker_ip = self._rollout_to_worker[rollout_id]
        download_url = f"http://{worker_ip}:8080/download"
        headers = {"Authorization": self._api_token}
        params = {"file_path": src_filename}
        
        try:
            async with self._http_session.get(download_url, headers=headers, params=params) as response:
                if response.status == 200:
                    # Ensure destination directory exists
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file content
                    with open(dst_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"File {src_filename} downloaded from rollout {rollout_id} to {dst_path}")
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Download failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Failed to copy {src_filename} from workspace for rollout {rollout_id}: {e}")
            raise

    async def compute_reward(
            self,
            rollout_id: str,
            completion: str,
            ground_truth: Any,
            **kwargs: Any
    ) -> Dict[str, float]:
        """Compute rewards using registered functions

        Returns dict mapping reward function names to their computed scores.
        """
        if rollout_id not in self._rollout_to_worker:
            raise ValueError(f"Rollout {rollout_id} is not initialized")
        
        worker_ip = self._rollout_to_worker[rollout_id]
        compute_reward_url = f"http://{worker_ip}:8080/compute_reward"
        headers = {
            "Authorization": self._api_token,
            "Content-Type": "application/json"
        }
        
        # Prepare request payload
        payload = {
            "completion": completion,
            "ground_truth": ground_truth,
            **kwargs
        }
        
        try:
            async with self._http_session.post(
                compute_reward_url, 
                headers=headers, 
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"Reward computed successfully for rollout {rollout_id}")
                    return result
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Reward computation failed: {response.status} - {error_text}")
        except aiohttp.ClientError as e:
            logger.error(f"Failed to compute reward for rollout {rollout_id}: {e}")
            raise RuntimeError(f"Reward computation request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error computing reward for rollout {rollout_id}: {e}")
            raise
        finally:
            await self._cleanup_rollout(rollout_id)


async def run_single_rollout(env: RemoteSkypilotMcpEnv, rollout_id: str, expression: str, expected: str, tmp_root: Path):
    """Run a complete rollout: init -> upload -> download+verify -> tool -> reward -> cleanup"""
    print(f"Starting rollout: {rollout_id}")

    # Create rollout-specific tmp dir
    rollout_tmp = tmp_root / rollout_id
    rollout_tmp.mkdir(parents=True, exist_ok=True)

    # Stage 1: Initialize rollout
    await env.init_rollout(rollout_id)
    print(f"Initialized rollout: {rollout_id}")

    # Stage 1.5a: Upload various content types
    test_contents = {
        "utf8_text.txt": f"# UTF-8 text for {rollout_id}\nExpression: {expression}\n",
        "latin1_text.txt": "Café Münster".encode("latin-1"),
        "json_data.json": '{"rollout": "%s", "value": %s}' % (rollout_id, expression),
        "binary_data.bin": b"\x00\x01\x02\x03\xFF",
        "unicode_text.txt": "你好, мир, hello 🌍",
    }

    for filename, content in test_contents.items():
        await env.copy_content_to_workspace(rollout_id, content, filename)
        print(f"Uploaded {filename} for {rollout_id}")

    # Stage 1.5b: Test file-based copy
    tmp_path = rollout_tmp / "local_file.txt"
    tmp_path.write_text(f"Temporary file for {rollout_id}, expression={expression}\n", encoding="utf-8")
    await env.copy_to_workspace(rollout_id, tmp_path, dst_filename=f"copied_{rollout_id}.txt")
    print(f"Copied file {tmp_path} to workspace for {rollout_id}")

    # Stage 1.6: Download and verify content
    for filename, original_content in test_contents.items():
        download_path = rollout_tmp / f"dl_{filename}"
        await env.copy_from_workspace(rollout_id, filename, download_path)

        downloaded_bytes = download_path.read_bytes()
        if isinstance(original_content, str):
            original_bytes = original_content.encode("utf-8")
        else:
            original_bytes = original_content

        if downloaded_bytes == original_bytes:
            print(f"Verified {filename} ✅")
        else:
            print(f"Mismatch in {filename}! ❌")

    # Verify copied file
    print(f"Verifying copied file for {rollout_id}")
    copied_dl = rollout_tmp / f"dl_copied_{rollout_id}.txt"
    await env.copy_from_workspace(rollout_id, f"copied_{rollout_id}.txt", copied_dl)
    if copied_dl.read_text(encoding="utf-8") == tmp_path.read_text(encoding="utf-8"):
        print(f"Verified copied file ✅")
    else:
        print(f"Mismatch in copied file ❌")

    # Stage 2: Run tool
    tool_result = await env.run_tool(rollout_id, "calculate", expression=expression)
    print(f"Tool result for {rollout_id}: {tool_result}")

    # Stage 3: Compute reward
    reward = await env.compute_reward(rollout_id, completion=str(tool_result), ground_truth=expected)
    print(f"Computed reward for {rollout_id}: {reward}")

    return rollout_id, reward


async def main():
    env = RemoteSkypilotMcpEnv(
        workdir_path="benchmax/envs/skypilot/workdir",
        num_nodes=2,
        cluster_name="test-cluster",
        cloud=sky.Azure(),
        cpus="2+",
    )

    tmp_root = Path("./tmp")
    tmp_root.mkdir(exist_ok=True)

    try:
        tools = await env.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")

        rollout_tasks = []
        for i in range(3):  # fewer for debugging; adjust as needed
            rollout_id = f"test-rollout-{i:03d}"
            expression = f"{i + 1} + {i + 1}"
            expected = str((i + 1) + (i + 1))
            task = run_single_rollout(env, rollout_id, expression, expected, tmp_root)
            rollout_tasks.append(task)

        print("Starting concurrent rollouts...")
        results = await asyncio.gather(*rollout_tasks, return_exceptions=True)

        print("Rollout results:")
        for result in results:
            print(result)

    finally:
        await env.shutdown()
        # Cleanup tmp dir at the very end
        shutil.rmtree(tmp_root, ignore_errors=True)
        print("Cleaned up temporary files.")



if __name__ == "__main__":
    asyncio.run(main())