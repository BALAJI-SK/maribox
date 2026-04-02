"""Notebook CLI commands."""

import asyncio
import tomllib
from pathlib import Path

from rich import print as rprint
from rich.syntax import Syntax

from maribox.config.resolution import resolve_config_root
from maribox.notebook.export import export_notebook, import_notebook
from maribox.notebook.runtime import MarimoRuntime


def _get_runtime(session_id: str) -> MarimoRuntime:
    """Get a MarimoRuntime for a session."""
    root = resolve_config_root()
    meta_path = root / "sessions" / session_id / "meta.toml"
    if not meta_path.is_file():
        rprint(f"[red]Session not found: {session_id}[/red]")
        raise SystemExit(1)
    with open(meta_path, "rb") as f:
        meta = tomllib.load(f)
    return MarimoRuntime(sandbox_url=meta.get("sandbox_url", ""))


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def notebook_show(session_id: str) -> None:
    """Pretty-print the notebook source with cell IDs."""
    runtime = _get_runtime(session_id)
    cells = _run(runtime.list_cells())
    if not cells:
        rprint("[dim]No cells in notebook.[/dim]")
        return

    # Re-import cells into a fresh runtime for display
    notebook_path = resolve_config_root() / "sessions" / session_id / "notebook.py"
    imported = import_notebook(notebook_path)
    from rich.console import Console
    for cell in imported:
        syntax = Syntax(cell.code, cell.name or cell.id, "python", theme="monokai")
        Console().print(f"[bold]{cell.name or cell.id}[/bold]")
        Console().print(syntax)


def notebook_save(session_id: str, out: str | None = None) -> None:
    """Write notebook.py to disk."""
    root = resolve_config_root()
    out_path = Path(out) if out else root / "sessions" / session_id / "notebook.py"
    runtime = _get_runtime(session_id)
    cells = _run(runtime.list_cells())
    export_notebook(cells, out_path)
    rprint(f"[green]Notebook saved to {out_path}[/green]")
