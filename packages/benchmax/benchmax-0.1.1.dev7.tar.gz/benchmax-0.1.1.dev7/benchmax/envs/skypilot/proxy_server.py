import os
import sys
import shutil
import uuid
import yaml
import asyncio
from pathlib import Path
from functools import wraps
from fastmcp import FastMCP, Client
from starlette.requests import Request
from starlette.responses import PlainTextResponse, FileResponse, JSONResponse
from starlette.datastructures import UploadFile

from reward_func import reward_functions  # your reward functions


# ---------------- Utility Functions ---------------- #
def setup_workspace(base_dir: Path) -> Path:
    """Create a unique workspace directory."""
    ws = (base_dir / uuid.uuid4().hex).resolve()
    ws.mkdir(parents=True, exist_ok=True)
    return ws


def load_config(config_path: Path, workspace: Path) -> dict:
    """Load YAML config and inject workspace paths."""
    with open(config_path, "r") as f:
        content = f.read().replace("${{ sync_workdir }}", str(Path(__file__).resolve().parent))
    config = yaml.safe_load(content)
    if "mcpServers" in config:
        for server in config["mcpServers"].values():
            server["cwd"] = str(workspace)
    return config


# ---------------- Auth Decorator ---------------- #
def require_auth(func):
    """Require API_TOKEN header."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = args[1] if len(args) == 2 else args[0]
        token = request.headers.get("Authorization")
        if token != os.getenv("API_TOKEN", "default-secret-token"):
            return PlainTextResponse("Unauthorized", status_code=401)
        return await func(*args, **kwargs)
    return wrapper


# ---------------- Proxy Server ---------------- #
class ProxyServer:
    def __init__(self, base_dir="workspace", host="0.0.0.0", port=8080):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.host = host
        self.port = port
        self.workspace: Path | None = None
        self.client: Client | None = None
        self.proxy: FastMCP | None = None
        self.config_path = Path(__file__).parent / "mcp_config.yaml"

    async def _setup(self):
        """Initialize workspace, MCP client, and proxy server."""
        self.workspace = setup_workspace(self.base_dir)
        config = load_config(self.config_path, self.workspace)

        self.client = Client(config)
        await self.client._connect()

        self.proxy = FastMCP.as_proxy(self.client, name="proxy")

        # Register endpoints
        self.proxy.custom_route("/health", methods=["GET"])(self._health)
        self.proxy.custom_route("/upload", methods=["POST"])(self._upload)
        self.proxy.custom_route("/download", methods=["GET"])(self._download)
        self.proxy.custom_route("/compute_reward", methods=["POST"])(self._compute_reward)
        self.proxy.custom_route("/reset", methods=["POST"])(self._reset)

    # ---------------- Endpoints ---------------- #
    async def _health(self, request: Request):
        return PlainTextResponse("OK")

    @require_auth
    async def _upload(self, request: Request):
        if not self.workspace:
            return PlainTextResponse("No workspace available", 500)
        form = await request.form()
        uploaded = []
        for file in form.values():
            if isinstance(file, UploadFile) and file.filename:
                dest = self.workspace / file.filename
                with open(dest, "wb") as f:
                    f.write(await file.read())
                uploaded.append(file.filename)
        if not uploaded:
            return PlainTextResponse("No files uploaded", 400)
        return PlainTextResponse(f"Uploaded: {', '.join(uploaded)}")

    @require_auth
    async def _download(self, request: Request):
        if not self.workspace:
            return PlainTextResponse("No workspace", 500)
        file_path = request.query_params.get("file_path")
        if not file_path:
            return PlainTextResponse("file_path required", 400)
        full_path = self.workspace / file_path
        if not full_path.exists() or not full_path.is_file():
            return PlainTextResponse("File not found", 404)
        return FileResponse(str(full_path), filename=full_path.name)

    @require_auth
    async def _compute_reward(self, request: Request):
        try:
            data = await request.json()
        except Exception:
            return PlainTextResponse("Invalid JSON", 400)

        completion = data.get("completion")
        ground_truth = data.get("ground_truth")
        if completion is None or ground_truth is None:
            return PlainTextResponse("completion and ground_truth required", 400)

        results = {}
        for func in reward_functions or []:
            name = getattr(func, "__name__", str(func))
            try:
                results[name] = func(completion=completion, ground_truth=ground_truth, workspace=self.workspace, mcp_client=self.client, **{
                    k: v for k, v in data.items() if k not in ("completion", "ground_truth")
                })
            except Exception as e:
                results[name] = float("nan")
                print(f"[WARN] reward {name} failed: {e}")
        return JSONResponse(results)

    @require_auth
    async def _reset(self, request: Request):
        """Reset server: clean workspace and restart process."""
        async def do_reset():
            await asyncio.sleep(0.1)
            print("[INFO] Resetting server...")
            sys.stdout.flush()
            os.execv(sys.executable, [sys.executable] + sys.argv)

        # Clean up workspace
        self.cleanup_workspace()

        asyncio.create_task(do_reset())
        return PlainTextResponse("Server reset scheduled")

    # ---------------- Public API ---------------- #
    def cleanup_workspace(self):
        if self.workspace and self.workspace.exists():
            shutil.rmtree(self.workspace)

    async def start(self):
        await self._setup()
        if self.proxy:
            await self.proxy.run_async(transport="http", host=self.host, port=self.port)


# ---------------- Main ---------------- #
if __name__ == "__main__":
    server = ProxyServer("../workspace")
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        server.cleanup_workspace()
