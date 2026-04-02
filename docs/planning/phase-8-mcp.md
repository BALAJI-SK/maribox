# Phase 8: MCP Server

## Objective

Expose all Maribox functionality as an MCP (Model Context Protocol) server so that external AI tools and IDEs can programmatically interact with Maribox sessions, notebooks, and agents. The server provides 25 tools covering the full CLI surface area, uses stdio and SSE transports for maximum compatibility, and resolves configuration and authentication internally so that MCP clients need no direct access to Maribox internals.

## Files to Create

- `src/maribox/mcp/__init__.py` — re-exports MCP server factory
- `src/maribox/mcp/server.py` — FastMCP server definition with all 25 tools
- `src/maribox/mcp/tools.py` — tool implementations (one function per CLI command)
- `src/maribox/mcp/transport.py` — stdio and SSE transport configuration

## Key Interfaces

### `server.py`

```python
from fastmcp import FastMCP

def create_mcp_server(config_root: Optional[Path] = None) -> FastMCP:
    """
    Create and configure the Maribox MCP server.

    Args:
        config_root: Override config root for testing.

    Returns:
        A configured FastMCP instance with all 25 tools registered.
    """
    server = FastMCP("maribox")

    # --- Config tools (4) ---
    @server.tool()
    async def config_get(key: str) -> str:
        """Get a configuration value by dotted key path."""
        ...

    @server.tool()
    async def config_set(key: str, value: str) -> str:
        """Set a configuration value by dotted key path."""
        ...

    @server.tool()
    async def config_list() -> str:
        """List all configuration values."""
        ...

    @server.tool()
    async def config_init() -> str:
        """Initialize a project-level Maribox configuration."""
        ...

    # --- Auth tools (3) ---
    @server.tool()
    async def auth_login(provider: str, api_key: str) -> str:
        """Store an API key for a provider."""
        ...

    @server.tool()
    async def auth_logout(provider: str) -> str:
        """Remove a stored API key for a provider."""
        ...

    @server.tool()
    async def auth_status() -> str:
        """Show stored key metadata (provider, backend, date)."""
        ...

    # --- Session tools (5) ---
    @server.tool()
    async def session_create(name: str = "") -> str:
        """Create a new sandbox session."""
        ...

    @server.tool()
    async def session_list() -> str:
        """List all sessions."""
        ...

    @server.tool()
    async def session_resume(session_id: str) -> str:
        """Resume an existing session."""
        ...

    @server.tool()
    async def session_kill(session_id: str) -> str:
        """Kill a session and its sandbox."""
        ...

    @server.tool()
    async def session_logs(session_id: str, tail: int = 50) -> str:
        """Get session execution logs."""
        ...

    # --- Notebook tools (5) ---
    @server.tool()
    async def notebook_list_cells(session_id: str) -> str:
        """List all cells in a session's notebook."""
        ...

    @server.tool()
    async def notebook_create_cell(session_id: str, code: str, position: int = -1) -> str:
        """Create a new cell in a notebook."""
        ...

    @server.tool()
    async def notebook_edit_cell(session_id: str, cell_id: str, code: str) -> str:
        """Edit an existing cell's code."""
        ...

    @server.tool()
    async def notebook_run_cell(session_id: str, cell_id: str) -> str:
        """Run a specific cell."""
        ...

    @server.tool()
    async def notebook_run_all(session_id: str) -> str:
        """Run all cells in execution order."""
        ...

    # --- Debug tools (4) ---
    @server.tool()
    async def debug_last_error(session_id: str) -> str:
        """Get the most recent error from a session."""
        ...

    @server.tool()
    async def debug_propose_fix(session_id: str, cell_id: str = "") -> str:
        """Ask the debug agent to propose a fix for an error."""
        ...

    @server.tool()
    async def debug_explain_cell(session_id: str, cell_id: str, depth: str = "medium") -> str:
        """Explain a cell's code in natural language."""
        ...

    @server.tool()
    async def debug_dependencies(session_id: str, cell_id: str) -> str:
        """Show the dependency graph for a cell."""
        ...

    # --- Agent tools (4) ---
    @server.tool()
    async def agent_run(message: str, agent: str = "", session_id: str = "") -> str:
        """Send a message to an AI agent."""
        ...

    @server.tool()
    async def agent_list() -> str:
        """List available agents."""
        ...

    @server.tool()
    async def ui_generate(description: str, session_id: str = "") -> str:
        """Generate a UI component from a description."""
        ...

    @server.tool()
    async def ui_preview(file_path: str) -> str:
        """Preview a UI component file."""
        ...

    return server
```

### `tools.py`

```python
@dataclass
class ToolContext:
    """Shared context for all tool implementations."""
    config: MariboxConfig
    config_root: Path
    auth_manager: AuthManager
    session_manager: Optional[SessionManager] = None
    sandbox_client: Optional[SandboxClient] = None

def resolve_tool_context(config_root: Optional[Path] = None) -> ToolContext:
    """
    Resolve and construct all dependencies needed by tool functions.
    This is the single entry point for MCP tool implementations to
    access Maribox internals.

    Flow:
    1. resolve_config_root() -> config_root
    2. load_config(config_root) -> MariboxConfig
    3. AuthManager(config_root) -> auth_manager
    4. SandboxClient(config.sandbox) -> sandbox_client (lazy)
    5. SessionManager(config_root, sandbox_client) -> session_manager (lazy)

    Returns a fully-populated ToolContext.
    """

async def get_or_create_session(ctx: ToolContext, session_id: Optional[str] = None) -> SessionInfo:
    """Resolve a session ID or create a new one if not specified."""

async def get_orchestrator(ctx: ToolContext) -> OrchestratorAgent:
    """Construct and return the orchestrator agent with all sub-agents."""

def format_result(data: Any) -> str:
    """
    Format a tool result as a human-readable string.
    Uses Rich Console with StringIO capture for consistent formatting.
    Returns the formatted string suitable for MCP tool responses.
    """
```

### `transport.py`

```python
import sys
import asyncio
from fastmcp import FastMCP

def run_stdio(server: FastMCP) -> None:
    """
    Run the MCP server using stdio transport.
    Reads JSON-RPC messages from stdin, writes responses to stdout.
    This is the default transport for CLI usage:
        maribox mcp serve --transport stdio
    """

def run_sse(server: FastMCP, host: str = "127.0.0.1", port: int = 8765) -> None:
    """
    Run the MCP server using Server-Sent Events (SSE) transport.
    Starts an HTTP server that exposes the MCP protocol via SSE.
    This is useful for IDE integrations and remote access:
        maribox mcp serve --transport sse --port 8765
    """

async def handle_shutdown(server: FastMCP) -> None:
    """Gracefully shut down the MCP server, cleaning up resources."""
```

## Dependencies

- **Phase 7 (CLI Commands)** must be complete: MCP tools delegate to the same underlying functions used by CLI commands. The CLI provides the tested, validated logic; the MCP layer is a thin adapter.
- Runtime packages: `fastmcp` (MCP server framework), `uvicorn` (for SSE transport), `rich` (output formatting).

## Testing Strategy

- **Unit tests for each tool function**: Call each of the 25 tools with mock `ToolContext`. Verify the tool calls the correct underlying function and returns the expected string.
- **Integration tests with FastMCP test client**: Use FastMCP's built-in test client to send JSON-RPC requests and verify responses. Test each tool end-to-end with a real `ToolContext` backed by temp directories.
- **Transport tests**: Verify `run_stdio` reads from stdin and writes to stdout. Verify `run_sse` starts an HTTP server on the specified port.
- **Error handling tests**: Call tools with invalid arguments (missing session_id, non-existent cell_id, empty api_key). Verify the MCP error response format.
- **Concurrency tests**: Send multiple tool requests simultaneously and verify no state corruption.
- **Schema validation tests**: Verify that each tool's parameter schema is correctly defined (types, required/optional, descriptions).
- **Format tests**: Verify `format_result()` produces clean string output without Rich escape codes (MCP clients expect plain text or markdown).

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| FastMCP API changes between versions | Tool registration syntax breaks | Pin FastMCP version; wrap tool registration in a helper function that can be updated in one place |
| SSE transport is not suitable for all IDEs | Some IDEs only support stdio | Support both transports; document which IDEs work with which transport |
| MCP tool responses are too large | LLM context window overflow | Truncate large responses (notebook output, logs) to a configurable max length (default: 10KB); include a "truncated" indicator |
| Concurrent MCP requests conflict with session state | Race conditions | Serialize requests per session using an async lock in `ToolContext` |
| Tool descriptions are not descriptive enough for LLMs | LLM calls wrong tools | Write detailed docstrings for each tool; include parameter examples; test with actual LLM tool selection |
| Stdio transport conflicts with process stdout | MCP messages mixed with log output | Ensure all Maribox logging goes to stderr, not stdout; MCP uses stdout exclusively |

## Acceptance Criteria

- [ ] FastMCP server is created with 25 tools, each with correct parameter schemas and descriptions
- [ ] All 25 tools return valid string responses when called with correct arguments
- [ ] `resolve_tool_context()` constructs a valid `ToolContext` from any config root
- [ ] Stdio transport reads JSON-RPC from stdin and writes responses to stdout
- [ ] SSE transport starts an HTTP server and accepts connections
- [ ] Error responses follow the MCP error format specification
- [ ] All tool responses are plain text or markdown (no Rich escape codes)
- [ ] Large outputs are truncated with a configurable limit
- [ ] `maribox mcp serve --transport stdio` starts the server correctly
- [ ] `maribox mcp serve --transport sse --port 8765` starts the SSE server
- [ ] Unit test coverage >= 80% for `mcp/` package
- [ ] Integration tests pass with FastMCP test client for all 25 tools
