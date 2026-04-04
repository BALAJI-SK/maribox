"""MCP server — FastMCP server with all maribox tools."""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from maribox.mcp.tools import format_result, resolve_tool_context


def create_mcp_server(config_root: Path | None = None) -> FastMCP:
    """Create and configure the Maribox MCP server with all tools."""
    server = FastMCP("maribox")

    # --- Config tools (4) ---

    @server.tool()
    async def config_get(key: str) -> str:
        """Get a configuration value by dotted key path (e.g. 'maribox.default_provider')."""
        ctx = resolve_tool_context(config_root)
        parts = key.split(".")
        data = ctx.config.to_toml()
        value: object = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return f"Key not found: {key}"
            if value is None:
                return f"Key not found: {key}"
        return format_result(value)

    @server.tool()
    async def config_set(key: str, value: str) -> str:
        """Set a configuration value by dotted key path."""
        from maribox.config.io import set_config_value

        ctx = resolve_tool_context(config_root)
        parts = key.split(".")
        if len(parts) < 2:
            return "Invalid key format. Use section.field (e.g. maribox.default_provider)."
        section = parts[0]
        field_name = ".".join(parts[1:])
        set_config_value(section, field_name, value, ctx.config_root)
        return f"Set {key} = {value}"

    @server.tool()
    async def config_list() -> str:
        """List all configuration values."""
        ctx = resolve_tool_context(config_root)
        return format_result(ctx.config.to_toml())

    @server.tool()
    async def config_init() -> str:
        """Initialize a project-level Maribox configuration."""
        from maribox.config.io import init_config_dir
        from maribox.config.resolution import resolve_config_root

        root = config_root or resolve_config_root()
        init_config_dir(root, project=True)
        return f"Initialized maribox config at {root / '.maribox'}"

    # --- Auth tools (3) ---

    @server.tool()
    async def auth_login(provider: str, api_key: str) -> str:
        """Store an API key for a provider (anthropic, google, openai, glm, custom)."""
        ctx = resolve_tool_context(config_root)
        ctx.auth_manager.set_key(provider, api_key)
        return f"Key stored for {provider}"

    @server.tool()
    async def auth_logout(provider: str) -> str:
        """Remove a stored API key for a provider."""
        ctx = resolve_tool_context(config_root)
        ctx.auth_manager.revoke_key(provider)
        return f"Key revoked for {provider}"

    @server.tool()
    async def auth_status() -> str:
        """Show stored key metadata (provider, has_key, date)."""
        ctx = resolve_tool_context(config_root)
        keys = ctx.auth_manager.list_keys()
        return format_result(keys)

    # --- Session tools (5) ---

    @server.tool()
    async def session_create(name: str = "") -> str:
        """Create a new local notebook session."""
        from maribox.sandbox.session import SessionManager

        ctx = resolve_tool_context(config_root)
        mgr = SessionManager(ctx.config_root)
        info = mgr.create_session(name=name or None)
        return format_result({
            "session_id": info.id,
            "status": info.status,
            "created_at": str(info.created_at),
        })

    @server.tool()
    async def session_list() -> str:
        """List all sessions."""
        from maribox.sandbox.session import SessionManager

        ctx = resolve_tool_context(config_root)
        mgr = SessionManager(ctx.config_root)
        sessions = mgr.list_sessions()
        return format_result([{"id": s.id, "status": s.status, "name": s.name} for s in sessions])

    @server.tool()
    async def session_resume(session_id: str) -> str:
        """Resume an existing session (check status)."""
        from maribox.sandbox.session import SessionManager

        ctx = resolve_tool_context(config_root)
        mgr = SessionManager(ctx.config_root)
        info = mgr.get_session(session_id)
        if info is None:
            return f"Session not found: {session_id}"
        return format_result({"id": info.id, "status": info.status, "name": info.name})

    @server.tool()
    async def session_kill(session_id: str) -> str:
        """Kill a session and clean up its resources."""
        from maribox.sandbox.session import SessionManager

        ctx = resolve_tool_context(config_root)
        mgr = SessionManager(ctx.config_root)
        mgr.kill_session(session_id)
        return f"Session {session_id} killed."

    @server.tool()
    async def session_logs(session_id: str, tail: int = 50) -> str:
        """Get session execution logs (last N lines)."""
        ctx = resolve_tool_context(config_root)
        log_path = ctx.config_root / "sessions" / session_id / "run.log"
        if not log_path.is_file():
            return f"No logs found for session {session_id}"
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return format_result("\n".join(lines[-tail:]))

    # --- Notebook tools (5) ---

    @server.tool()
    async def notebook_list_cells(session_id: str) -> str:
        """List all cells in a session's notebook."""
        from maribox.notebook.export import import_notebook

        ctx = resolve_tool_context(config_root)
        nb_path = ctx.config_root / "sessions" / session_id / "notebook.py"
        cells = import_notebook(nb_path)
        if not cells:
            return "No cells found."
        return format_result([{"id": c.id, "name": c.name, "code_preview": c.code[:80]} for c in cells])

    @server.tool()
    async def notebook_create_cell(session_id: str, code: str, position: int = -1) -> str:
        """Create a new cell in a notebook."""
        from maribox.notebook.cell import Cell, CellId
        from maribox.notebook.export import export_notebook, import_notebook

        ctx = resolve_tool_context(config_root)
        nb_path = ctx.config_root / "sessions" / session_id / "notebook.py"
        cells = import_notebook(nb_path)
        cell_id = CellId(f"cell_{len(cells) + 1}")
        cells.append(Cell(id=cell_id, code=code))
        export_notebook(cells, nb_path)
        return f"Created cell {cell_id}"

    @server.tool()
    async def notebook_edit_cell(session_id: str, cell_id: str, code: str) -> str:
        """Edit an existing cell's code."""
        from maribox.notebook.export import export_notebook, import_notebook

        ctx = resolve_tool_context(config_root)
        nb_path = ctx.config_root / "sessions" / session_id / "notebook.py"
        cells = import_notebook(nb_path)
        found = False
        for cell in cells:
            if cell.id == cell_id:
                cell.code = code
                found = True
                break
        if not found:
            return f"Cell {cell_id} not found."
        export_notebook(cells, nb_path)
        return f"Updated cell {cell_id}"

    @server.tool()
    async def notebook_run_cell(session_id: str, cell_id: str) -> str:
        """Run a specific cell (placeholder — requires active runtime)."""
        return f"Run cell {cell_id} in session {session_id} — requires active runtime."

    @server.tool()
    async def notebook_run_all(session_id: str) -> str:
        """Run all cells in execution order (placeholder — requires active runtime)."""
        return f"Run all cells in session {session_id} — requires active runtime."

    # --- Debug tools (4) ---

    @server.tool()
    async def debug_last_error(session_id: str) -> str:
        """Get the most recent error from a session."""
        ctx = resolve_tool_context(config_root)
        nb_path = ctx.config_root / "sessions" / session_id / "notebook.py"
        if not nb_path.is_file():
            return f"No notebook found for session {session_id}"
        return "No errors found (error tracking requires active runtime)."

    @server.tool()
    async def debug_propose_fix(session_id: str, cell_id: str = "") -> str:
        """Ask the debug agent to propose a fix for an error (requires active runtime)."""
        return f"Propose fix for {cell_id or 'last error'} in session {session_id} — requires active runtime."

    @server.tool()
    async def debug_explain_cell(session_id: str, cell_id: str, depth: str = "medium") -> str:
        """Explain a cell's code in natural language."""
        from maribox.notebook.export import import_notebook

        ctx = resolve_tool_context(config_root)
        nb_path = ctx.config_root / "sessions" / session_id / "notebook.py"
        cells = import_notebook(nb_path)
        target = next((c for c in cells if c.id == cell_id), None)
        if target is None:
            return f"Cell {cell_id} not found."
        return f"Cell {cell_id} code:\n{target.code}\n\n(Explanation requires active LLM agent.)"

    @server.tool()
    async def debug_dependencies(session_id: str, cell_id: str) -> str:
        """Show the dependency graph for a cell."""
        from maribox.notebook.dag import CellDAG
        from maribox.notebook.export import import_notebook

        ctx = resolve_tool_context(config_root)
        nb_path = ctx.config_root / "sessions" / session_id / "notebook.py"
        cells = import_notebook(nb_path)
        dag = CellDAG()
        for cell in cells:
            dag.add_cell(cell)
        deps = dag.get_dependencies(cell_id)
        dependents = dag.get_dependents(cell_id)
        return format_result({
            "cell_id": cell_id,
            "depends_on": list(deps),
            "depended_by": list(dependents),
        })

    # --- Agent tools (4) ---

    @server.tool()
    async def agent_run(message: str, agent: str = "", session_id: str = "") -> str:
        """Send a message to an AI agent (requires active runtime and API key)."""
        return f"Agent '{agent or 'orchestrator'}' received: {message[:100]} — requires active LLM connection."

    @server.tool()
    async def agent_list() -> str:
        """List available agents."""
        from maribox.agents.profile import load_profiles

        profiles = load_profiles(config_root)
        return format_result({name: {"provider": p.provider, "model": p.model} for name, p in profiles.items()})

    @server.tool()
    async def ui_generate(description: str, session_id: str = "") -> str:
        """Generate a UI component from a description (requires active runtime)."""
        return f"Generate UI: {description[:100]} — requires active runtime."

    @server.tool()
    async def ui_preview(file_path: str) -> str:
        """Preview a UI component file."""
        path = Path(file_path)
        if not path.is_file():
            return f"File not found: {file_path}"
        content = path.read_text(encoding="utf-8", errors="replace")
        return format_result(content)

    return server
