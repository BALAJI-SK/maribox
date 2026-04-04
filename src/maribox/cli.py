"""maribox CLI entry point."""

from __future__ import annotations

import typer
from rich import print as rprint

from maribox import __version__

app = typer.Typer(
    name="maribox",
    help="Multi-session marimo notebook orchestrator with collaborative AI agents.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    if value:
        rprint(f"maribox {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show maribox version.",
    ),
) -> None:
    """maribox — multi-session marimo notebook orchestrator."""


# --- config commands (Phase 2) ---
config_app = typer.Typer(help="Manage maribox configuration.", no_args_is_help=True)
app.add_typer(config_app, name="config")


@config_app.command("init")
def config_init(
    global_scope: bool = typer.Option(False, "--global", help="Initialize global config."),
    project_scope: bool = typer.Option(False, "--project", help="Initialize project config."),
) -> None:
    """Scaffold a .maribox/ directory with defaults."""
    from maribox.commands.config import config_init as _init
    _init(global_scope=global_scope, project_scope=project_scope)


@config_app.command("show")
def config_show() -> None:
    """Print resolved config (merged global + project, secrets redacted)."""
    from maribox.commands.config import config_show as _show
    _show()


@config_app.command("set")
def config_set(
    key: str = typer.Argument(help="Config key in dot-path notation (e.g. maribox.default_provider)."),
    value: str = typer.Argument(help="Value to set."),
    global_scope: bool = typer.Option(False, "--global", help="Set in global config."),
    project_scope: bool = typer.Option(False, "--project", help="Set in project config."),
) -> None:
    """Update a single config key."""
    from maribox.commands.config import config_set as _set
    _set(key=key, value=value, global_scope=global_scope, project_scope=project_scope)


@config_app.command("path")
def config_path() -> None:
    """Print the resolved config root."""
    from maribox.commands.config import config_path as _path
    _path()


# --- auth commands (Phase 3) ---
auth_app = typer.Typer(help="Manage API keys and providers.", no_args_is_help=True)
app.add_typer(auth_app, name="auth")


@auth_app.command("set")
def auth_set(
    provider: str = typer.Argument(
        help="Provider name: anthropic | google | openai | glm | custom.",
    ),
) -> None:
    """Store an API key for a provider (hidden prompt)."""
    from maribox.commands.auth import auth_set as _set
    _set(provider=provider)


@auth_app.command("list")
def auth_list() -> None:
    """Show masked keys and status per provider."""
    from maribox.commands.auth import auth_list as _list
    _list()


@auth_app.command("use")
def auth_use(
    provider: str = typer.Argument(help="Provider to activate."),
    model: str | None = typer.Option(None, "--model", help="Default model for this provider."),
    project: bool = typer.Option(False, "--project", help="Set for current project only."),
) -> None:
    """Set the active provider globally or for the current project."""
    from maribox.commands.auth import auth_use as _use
    _use(provider=provider, model=model, project=project)


@auth_app.command("rotate")
def auth_rotate(
    provider: str = typer.Argument(help="Provider whose key to rotate."),
) -> None:
    """Replace the API key for a provider."""
    from maribox.commands.auth import auth_rotate as _rotate
    _rotate(provider=provider)


@auth_app.command("revoke")
def auth_revoke(
    provider: str = typer.Argument(help="Provider whose key to revoke."),
) -> None:
    """Wipe the API key for a provider."""
    from maribox.commands.auth import auth_revoke as _revoke
    _revoke(provider=provider)


# --- glm command (GLM 5.1 setup) ---
@app.command("glm")
def glm(
    api_key: str | None = typer.Option(None, "--api-key", help="GLM API key."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Set as default provider."),
) -> None:
    """Configure GLM 5.1 (z.ai) as the AI provider for maribox."""
    from maribox.commands.auth import glm_setup
    glm_setup(api_key=api_key, set_default=set_default)


# --- session commands (Phase 4) ---
session_app = typer.Typer(help="Manage notebook sessions.", no_args_is_help=True)
app.add_typer(session_app, name="session")


@session_app.command("new")
def session_new(
    name: str | None = typer.Option(None, "--name", help="Session name."),
    provider: str | None = typer.Option(None, "--provider", help="AI provider."),
    model: str | None = typer.Option(None, "--model", help="AI model."),
) -> None:
    """Create a new notebook session."""
    from maribox.commands.session import session_new as _new
    _new(name=name, provider=provider, model=model)


@session_app.command("list")
def session_list() -> None:
    """Table of all sessions."""
    from maribox.commands.session import session_list as _list
    _list()


@session_app.command("attach")
def session_attach(
    session_id: str = typer.Argument(help="Session ID to attach to."),
) -> None:
    """Open the TUI attached to an existing session."""
    from maribox.commands.session import session_attach as _attach
    _attach(session_id=session_id)


@session_app.command("stop")
def session_stop(
    session_id: str = typer.Argument(help="Session ID to stop."),
) -> None:
    """Gracefully shut down a session."""
    from maribox.commands.session import session_stop as _stop
    _stop(session_id=session_id)


@session_app.command("kill")
def session_kill(
    session_id: str = typer.Argument(help="Session ID to kill."),
) -> None:
    """Force-terminate a session without cleanup."""
    from maribox.commands.session import session_kill as _kill
    _kill(session_id=session_id)


@session_app.command("snapshot")
def session_snapshot(
    session_id: str = typer.Argument(help="Session ID to snapshot."),
    out: str | None = typer.Option(None, "--out", help="Output path for snapshot archive."),
) -> None:
    """Save notebook + logs to a snapshot archive."""
    from maribox.commands.session import session_snapshot as _snapshot
    _snapshot(session_id=session_id, out=out)


@session_app.command("rm")
def session_rm(
    session_id: str = typer.Argument(help="Session ID to remove."),
) -> None:
    """Remove session directory."""
    from maribox.commands.session import session_rm as _rm
    _rm(session_id=session_id)


# --- cell commands (Phase 5) ---
cell_app = typer.Typer(help="Manage notebook cells.", no_args_is_help=True)
app.add_typer(cell_app, name="cell")


@cell_app.command("add")
def cell_add(
    session_id: str = typer.Argument(help="Session ID."),
    code: str = typer.Option(..., "--code", help="Python code for the cell."),
    after: str | None = typer.Option(None, "--after", help="Cell ID to insert after."),
) -> None:
    """Add a cell to a session's notebook."""
    from maribox.commands.cell import cell_add as _add
    _add(session_id=session_id, code=code, after=after)


@cell_app.command("run")
def cell_run(
    session_id: str = typer.Argument(help="Session ID."),
    cell: str | None = typer.Option(None, "--cell", help="Cell ID to run."),
    all_cells: bool = typer.Option(False, "--all", help="Run all cells."),
) -> None:
    """Execute a cell or all cells."""
    from maribox.commands.cell import cell_run as _run
    _run(session_id=session_id, cell=cell, all_cells=all_cells)


@cell_app.command("edit")
def cell_edit(
    session_id: str = typer.Argument(help="Session ID."),
    cell: str = typer.Option(..., "--cell", help="Cell ID to edit."),
    code: str = typer.Option(..., "--code", help="New cell source."),
) -> None:
    """Replace cell source."""
    from maribox.commands.cell import cell_edit as _edit
    _edit(session_id=session_id, cell=cell, code=code)


@cell_app.command("rm")
def cell_rm(
    session_id: str = typer.Argument(help="Session ID."),
    cell: str = typer.Option(..., "--cell", help="Cell ID to remove."),
) -> None:
    """Remove a cell from the notebook."""
    from maribox.commands.cell import cell_rm as _rm
    _rm(session_id=session_id, cell=cell)


# --- notebook commands (Phase 5) ---
notebook_app = typer.Typer(help="Notebook operations.", no_args_is_help=True)
app.add_typer(notebook_app, name="notebook")


@notebook_app.command("show")
def notebook_show(
    session_id: str = typer.Argument(help="Session ID."),
) -> None:
    """Pretty-print the notebook source with cell IDs."""
    from maribox.commands.notebook_cmds import notebook_show as _show
    _show(session_id=session_id)


@notebook_app.command("save")
def notebook_save(
    session_id: str = typer.Argument(help="Session ID."),
    out: str | None = typer.Option(None, "--out", help="Output file path."),
) -> None:
    """Write notebook.py to disk."""
    from maribox.commands.notebook_cmds import notebook_save as _save
    _save(session_id=session_id, out=out)


# --- ui commands (Phase 7) ---
ui_app = typer.Typer(help="Generate marimo UI components.", no_args_is_help=True)
app.add_typer(ui_app, name="ui")


@ui_app.command("generate")
def ui_generate(
    session_id: str = typer.Argument(help="Session ID."),
    prompt: str = typer.Option(..., "--prompt", help="Description of UI to generate."),
) -> None:
    """Generate marimo UI components as new cells."""
    from maribox.commands.ui import ui_generate as _gen
    _gen(session_id=session_id, prompt=prompt)


@ui_app.command("preview")
def ui_preview(
    session_id: str = typer.Argument(help="Session ID."),
) -> None:
    """Open the marimo browser UI for the session."""
    from maribox.commands.ui import ui_preview as _preview
    _preview(session_id=session_id)


# --- debug commands (Phase 7) ---
debug_app = typer.Typer(help="Debug notebook cells.", no_args_is_help=True)
app.add_typer(debug_app, name="debug")


@debug_app.command("last")
def debug_last(
    session_id: str = typer.Argument(help="Session ID."),
) -> None:
    """Show the last error with stack trace and cell context."""
    from maribox.commands.debug import debug_last as _last
    _last(session_id=session_id)


@debug_app.command("fix")
def debug_fix(
    session_id: str = typer.Argument(help="Session ID."),
    cell: str | None = typer.Option(None, "--cell", help="Cell ID to fix."),
) -> None:
    """DebugAgent analyses the error and proposes a fix."""
    from maribox.commands.debug import debug_fix as _fix
    _fix(session_id=session_id, cell=cell)


@debug_app.command("explain")
def debug_explain(
    session_id: str = typer.Argument(help="Session ID."),
    cell: str = typer.Option(..., "--cell", help="Cell ID to explain."),
) -> None:
    """Explain what a cell does and its dependencies."""
    from maribox.commands.debug import debug_explain as _explain
    _explain(session_id=session_id, cell=cell)


# --- agent commands (Phase 6) ---
agent_app = typer.Typer(help="Manage and run AI agents.", no_args_is_help=True)
app.add_typer(agent_app, name="agent")


@agent_app.command("list")
def agent_list() -> None:
    """List available agent roles and their model config."""
    from maribox.commands.agent import agent_list as _list
    _list()


@agent_app.command("run")
def agent_run(
    role: str = typer.Argument(help="Agent role to run."),
    prompt: str = typer.Option(..., "--prompt", help="Prompt for the agent."),
    session: str | None = typer.Option(None, "--session", help="Session ID context."),
) -> None:
    """Run a single agent role with an ad-hoc prompt."""
    from maribox.commands.agent import agent_run as _run
    _run(role=role, prompt=prompt, session=session)


# --- top-level commands ---

@app.command()
def serve(
    mcp: bool = typer.Option(False, "--mcp", help="Run as MCP server."),
    transport: str = typer.Option("stdio", "--transport", help="MCP transport: stdio | sse."),
) -> None:
    """Start maribox as an MCP server."""
    if not mcp:
        rprint("[yellow]Use --mcp flag to start the MCP server.[/yellow]")
        raise typer.Exit(1)
    from maribox.mcp import run_server
    run_server(transport=transport)


@app.command()
def tui(
    session: str | None = typer.Option(None, "--session", help="Session ID to attach to."),
) -> None:
    """Open the full Textual TUI."""
    from maribox.tui import run_tui
    run_tui(session_id=session)
