"""UI CLI commands — generate marimo UI components and preview."""

from __future__ import annotations

import asyncio
import webbrowser

from rich import print as rprint
from rich.panel import Panel
from rich.syntax import Syntax

from maribox.config.resolution import resolve_config_root
from maribox.notebook.runtime import MarimoRuntime


def _get_runtime(session_id: str) -> MarimoRuntime:
    """Get runtime for a session."""
    import tomllib

    root = resolve_config_root()
    meta_path = root / "sessions" / session_id / "meta.toml"
    if not meta_path.is_file():
        rprint(f"[red]Session not found: {session_id}[/red]")
        raise SystemExit(1)
    with open(meta_path, "rb") as f:
        meta = tomllib.load(f)
    return MarimoRuntime()


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def ui_generate(session_id: str, prompt: str) -> None:
    """Generate marimo UI components as new cells.

    Uses the UI agent to create component code from a natural language description.
    """
    runtime = _get_runtime(session_id)

    rprint(f"[cyan]Generating UI components for: {prompt}[/cyan]")
    rprint("[dim]Agent will create cells with marimo UI components (mo.ui.*).[/dim]")

    # In production, this invokes the UIAgent via the orchestrator.
    # For now, generate a template cell with the prompt as a comment.
    template_code = (
        f"# UI generated from: {prompt}\n"
        "import marimo as mo\n"
        "# TODO: Add your UI components here\n"
        "# slider = mo.ui.slider(1, 100, value=50, label='Value')\n"
        "# mo.vstack([slider, mo.md(f'Selected: {slider.value}')])\n"
    )

    cell = _run(runtime.add_cell(template_code))
    rprint(Panel(
        Syntax(template_code, "python", theme="monokai"),
        title=f"[green]Generated Cell {cell.id}[/green]",
    ))


def ui_preview(session_id: str) -> None:
    """Open the marimo browser UI for the session."""
    root = resolve_config_root()
    meta_path = root / "sessions" / session_id / "meta.toml"
    if not meta_path.is_file():
        rprint(f"[red]Session not found: {session_id}[/red]")
        raise SystemExit(1)

    import tomllib

    with open(meta_path, "rb") as f:
        meta = tomllib.load(f)

    marimo_url = meta.get("marimo_url", "")
    if marimo_url:
        rprint(f"[green]Opening marimo UI: {marimo_url}[/green]")
        webbrowser.open(marimo_url)
    else:
        rprint("[yellow]No marimo URL found for this session. Is the session running?[/yellow]")
