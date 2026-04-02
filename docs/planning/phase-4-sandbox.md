# Phase 4: Sandbox Management

## Objective

Provide an isolated, containerized execution environment for running Marimo notebooks safely. Each sandbox is a Docker (or Podman) container with configurable resource limits, network policies, and a lifecycle managed through an async HTTP client. Sessions track sandbox state across multiple interactions, persisting metadata and notebook files to disk so that users can resume work after interruption.

## Files to Create

- `src/maribox/sandbox/__init__.py` — re-exports `SandboxClient`, `SessionManager`
- `src/maribox/sandbox/client.py` — async HTTP client for sandbox container management
- `src/maribox/sandbox/session.py` — session state tracking and persistence
- `src/maribox/commands/session.py` — CLI subcommands: `maribox session create`, `list`, `resume`, `kill`

## Key Interfaces

### `client.py`

```python
class SandboxError(Exception): ...
class SandboxTimeoutError(SandboxError): ...
class SandboxHealthError(SandboxError): ...

@dataclass
class SandboxInfo:
    container_id: str
    session_id: str
    image: str
    status: str                      # running | stopped | error
    port: int
    created_at: datetime
    memory_usage: Optional[str] = None
    cpu_usage: Optional[float] = None

class SandboxClient:
    """
    Async client for managing sandbox containers.
    Communicates with containers via HTTP (health checks, code execution).
    Uses httpx.AsyncClient for all network operations.
    """

    def __init__(self, config: SandboxSection, http_client: Optional[httpx.AsyncClient] = None): ...

    async def create_sandbox(
        self,
        session_id: str,
        image: Optional[str] = None,
        memory: Optional[str] = None,
        cpu: Optional[float] = None,
        timeout: Optional[int] = None,
    ) -> SandboxInfo:
        """
        Create and start a new sandbox container.
        Returns SandboxInfo with connection details.
        Raises SandboxError if container creation fails.
        """

    async def health_check(self, container_id: str) -> bool:
        """
        Check if a sandbox is responsive.
        Returns True if the container responds to /health within 5 seconds.
        """

    async def exec_code(
        self,
        container_id: str,
        code: str,
        timeout: Optional[float] = None,
    ) -> dict:
        """
        Execute Python code inside a sandbox container.
        Returns {"stdout": str, "stderr": str, "exit_code": int, "duration_ms": float}.
        Raises SandboxTimeoutError if execution exceeds timeout.
        """

    async def install_package(
        self,
        container_id: str,
        package: str,
        version: Optional[str] = None,
    ) -> bool:
        """
        Install a Python package inside the sandbox via pip.
        Returns True on success.
        """

    async def teardown(self, container_id: str, force: bool = False) -> None:
        """
        Stop and remove a sandbox container.
        If force=True, sends SIGKILL instead of SIGTERM.
        """

    async def list_sandboxes(self) -> List[SandboxInfo]:
        """List all Maribox-managed sandbox containers."""

    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        """Retrieve the last `tail` lines of container stdout/stderr."""

    async def __aenter__(self) -> "SandboxClient": ...
    async def __aexit__(self, *args) -> None: ...
```

### `session.py`

```python
class SessionState(Enum):
    CREATING = "creating"
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    STOPPED = "stopped"
    TEARDOWN = "teardown"

@dataclass
class SessionInfo:
    session_id: str                      # UUID4
    state: SessionState
    sandbox_info: Optional[SandboxInfo]
    created_at: datetime
    last_active: datetime
    notebook_path: Optional[Path]
    metadata: Dict[str, Any]

class SessionManager:
    """
    Manages the lifecycle of sandbox sessions.
    Each session has a directory under the config root containing:
      - meta.toml   (session metadata)
      - notebook.py (the Marimo notebook file)
      - run.log     (execution log)
    """

    def __init__(self, config_root: Path, sandbox_client: SandboxClient): ...

    async def create_session(
        self,
        name: Optional[str] = None,
        image: Optional[str] = None,
    ) -> SessionInfo:
        """
        Create a new session with a UUID4 session_id.
        Creates the session directory and meta.toml.
        Starts a sandbox container and associates it with the session.
        """

    async def resume_session(self, session_id: str) -> SessionInfo:
        """
        Resume an existing session.
        Re-creates the sandbox container if the previous one was stopped.
        Restores notebook.py and session state from meta.toml.
        """

    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieve session info by ID."""

    async def list_sessions(self) -> List[SessionInfo]:
        """List all sessions (any state)."""

    async def kill_session(self, session_id: str) -> None:
        """
        Gracefully tear down a session.
        Stops the sandbox, updates state to TEARDOWN, preserves files.
        """

    async def cleanup_idle(self, max_idle_minutes: int = 30) -> List[str]:
        """
        Find and tear down sessions idle for longer than max_idle_minutes.
        Returns list of cleaned-up session IDs.
        """

    def get_session_dir(self, session_id: str) -> Path:
        """Return the directory path for a session."""

    def _save_meta(self, session: SessionInfo) -> None:
        """Persist session metadata to meta.toml."""

    def _load_meta(self, session_id: str) -> Optional[SessionInfo]:
        """Load session metadata from meta.toml."""
```

### `commands/session.py`

```python
async def session_create(name: Optional[str] = None) -> None:
    """Create a new session, print the session ID and connection info."""

async def session_list() -> None:
    """Print a Rich table of all sessions with state, age, and sandbox status."""

async def session_resume(session_id: str) -> None:
    """Resume a session, re-attaching to its sandbox container."""

async def session_kill(session_id: str) -> None:
    """Kill a session and its sandbox."""

async def session_logs(session_id: str, tail: int = 50) -> None:
    """Print the execution log for a session."""
```

## Dependencies

- **Phase 2 (Config)** must be complete: `SandboxClient` reads `SandboxSection` for defaults (image, memory, CPU limits, timeout). `SessionManager` uses `resolve_config_root()` to locate session directories.
- **Phase 3 (Auth)** must be complete: API keys stored by `AuthManager` are injected into sandbox containers as environment variables (never written to disk or logs).
- Runtime packages: `httpx` (async HTTP client), `docker` (Docker SDK for Python, optional for direct API), `tomli_w` (meta.toml writing).

## Testing Strategy

- **Unit tests for SandboxClient**: Mock `httpx.AsyncClient`; test `create_sandbox` sends correct Docker API payload; test `exec_code` parses response dict; test `health_check` timeout behavior.
- **Unit tests for SessionManager**: Use temp directories for session storage. Test full lifecycle: create -> resume -> kill. Verify `meta.toml` is valid TOML. Verify `notebook.py` is preserved across resume.
- **Unit tests for SessionState transitions**: Assert valid transitions (CREATING -> ACTIVE -> IDLE -> TEARDOWN) and invalid ones (TEARDOWN -> ACTIVE should raise).
- **Integration tests with Docker**: Requires Docker daemon running. Test actual container creation, code execution (`print("hello")`), package installation, and teardown. Tagged with `@pytest.mark.integration`.
- **Concurrency tests**: Multiple sessions created simultaneously; verify no ID collisions, no file corruption.
- **Timeout tests**: Submit code that sleeps longer than the timeout; verify `SandboxTimeoutError`.
- **Cleanup tests**: `cleanup_idle()` correctly identifies and tears down stale sessions.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docker daemon not available | Sandbox creation fails on machines without Docker | Detect Docker availability at startup; provide a "local" runtime mode that runs code in a subprocess with resource limits as a degraded fallback |
| Container port conflicts | Multiple sandboxes cannot bind to the same port | Use port 0 (auto-assign) and read back the allocated port from Docker API |
| Sandbox escape via malicious code | Security breach | Run containers with `--security-opt=no-new-privileges`, read-only filesystem except `/tmp`, no network by default (`--network=none` unless explicitly enabled) |
| Orphaned containers after crash | Containers leak resources | On startup, scan for containers with the `maribox.session_id` label and offer to reconnect or clean up |
| Large `run.log` files fill disk | Disk space exhaustion | Rotate logs at 10MB; keep only the last 3 rotated files per session |
| `httpx.AsyncClient` connection pool exhaustion | Failed requests under high concurrency | Configure connection pool limits (max_connections=20, max_keepalive=10); use connection timeouts |

## Acceptance Criteria

- [ ] `SandboxClient.create_sandbox()` starts a Docker container with the specified image and resource limits
- [ ] `SandboxClient.exec_code()` runs Python code and returns stdout, stderr, exit code, and duration
- [ ] `SandboxClient.install_package()` installs a pip package inside the container
- [ ] `SandboxClient.teardown()` stops and removes the container
- [ ] `SandboxClient.health_check()` returns True for running containers, False otherwise
- [ ] `SessionManager.create_session()` creates a session directory with `meta.toml`, `notebook.py`, and `run.log`
- [ ] `SessionManager.resume_session()` restores a stopped session including its sandbox
- [ ] `SessionManager.kill_session()` tears down the sandbox and marks the session as STOPPED
- [ ] Session IDs are UUID4 with no collisions across 10,000 test generations
- [ ] `meta.toml` is valid TOML that round-trips through load/save
- [ ] API keys are never written to disk or logs (verified by log masking)
- [ ] Containers are labeled with `maribox.session_id` for orphan detection
- [ ] `maribox session create/list/resume/kill` CLI commands work end-to-end
- [ ] Unit test coverage >= 80% for `sandbox/` package
