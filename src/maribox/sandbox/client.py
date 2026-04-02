"""AIO Sandbox MCP client — manages sandbox containers."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass

import httpx

from maribox.exceptions import SandboxError


@dataclass
class SandboxInfo:
    """Information about a running sandbox."""

    sandbox_id: str
    url: str


@dataclass
class ExecResult:
    """Result of code execution in a sandbox."""

    exit_code: int
    stdout: str
    stderr: str


class SandboxClient:
    """Client for interacting with AIO Sandbox containers.

    Uses httpx for async HTTP communication with the sandbox API.
    Falls back to the agent-sandbox library if no base_url is configured.
    """

    def __init__(self, base_url: str | None = None, timeout: int = 300) -> None:
        self._base_url = base_url
        self._timeout = timeout

    def _get_http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout)

    async def create_sandbox(self) -> SandboxInfo:
        """Create a new AIO Sandbox container.

        Returns sandbox ID and URL for connecting to the sandbox.
        """
        if self._base_url:
            return await self._create_via_api()
        return await self._create_via_agent_sandbox()

    async def _create_via_api(self) -> SandboxInfo:
        """Create sandbox via HTTP API."""
        assert self._base_url is not None
        async with self._get_http_client() as client:
            try:
                response = await client.post(f"{self._base_url}/sandboxes", json={})
                response.raise_for_status()
                data = response.json()
                return SandboxInfo(
                    sandbox_id=data["id"],
                    url=data.get("url", f"{self._base_url}/sandboxes/{data['id']}"),
                )
            except httpx.HTTPError as e:
                raise SandboxError(f"Failed to create sandbox: {e}") from e

    async def _create_via_agent_sandbox(self) -> SandboxInfo:
        """Create sandbox using the agent-sandbox library."""
        try:
            import agent_sandbox

            result = agent_sandbox.create()
            return SandboxInfo(
                sandbox_id=result.id if hasattr(result, "id") else str(result),
                url=result.url if hasattr(result, "url") else str(result),
            )
        except Exception as e:
            raise SandboxError(f"Failed to create sandbox via agent-sandbox: {e}") from e

    async def health_check(self, sandbox_url: str) -> bool:
        """Check if a sandbox is healthy."""
        async with self._get_http_client() as client:
            try:
                response = await client.get(f"{sandbox_url}/health")
                return response.status_code == 200
            except httpx.HTTPError:
                return False

    async def exec_code(self, sandbox_url: str, code: str) -> ExecResult:
        """Execute Python code inside a sandbox container."""
        async with self._get_http_client() as client:
            try:
                response = await client.post(
                    f"{sandbox_url}/exec",
                    json={"code": code, "language": "python"},
                )
                response.raise_for_status()
                data = response.json()
                return ExecResult(
                    exit_code=data.get("exit_code", 0),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                )
            except httpx.HTTPError as e:
                raise SandboxError(f"Code execution failed: {e}") from e

    async def install_package(self, sandbox_url: str, package: str) -> None:
        """Install a Python package in the sandbox."""
        async with self._get_http_client() as client:
            try:
                response = await client.post(
                    f"{sandbox_url}/exec",
                    json={"code": f"import subprocess; subprocess.check_call(['pip', 'install', '{package}'])"},
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise SandboxError(f"Package install failed: {e}") from e

    async def teardown(self, sandbox_url: str) -> None:
        """Gracefully shut down a sandbox."""
        async with self._get_http_client() as client:
            with contextlib.suppress(httpx.HTTPError):
                await client.delete(sandbox_url)
