"""Cell CLI commands — manage notebook cells."""

from __future__ import annotations

import asyncio
import tomllib

from rich import print as rprint

from maribox.config.resolution import resolve_config_root
from maribox.notebook.cell import CellId
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

    sandbox_url = meta.get("sandbox_url", "")
    return MarimoRuntime(sandbox_url=sandbox_url)


def _run(coro: object) -> object:
    return asyncio.get_event_loop().run_until_complete(coro)


def cell_add(session_id: str, code: str, after: str | None = None) -> None:
    """Add a cell to a session's notebook."""
    runtime = _get_runtime(session_id)
    after_id = CellId(after) if after else None
    cell = _run(runtime.add_cell(code, after=after_id))
    rprint(f"[green]Cell added:[/green] {cell.id}")


def cell_run(session_id: str, cell: str | None = None, all_cells: bool = False) -> None:
    """Execute a cell or all cells."""
    runtime = _get_runtime(session_id)

    if all_cells:
        results = _run(runtime.run_all())
        for result in results:
            rprint(result.text)
    elif cell:
        result = _run(runtime.run_cell(CellId(cell)))
        rprint(result.text)
    else:
        rprint("[yellow]Specify --cell CELL_ID or --all[/yellow]")


def cell_edit(session_id: str, cell: str, code: str) -> None:
    """Replace cell source."""
    runtime = _get_runtime(session_id)
    updated = _run(runtime.edit_cell(CellId(cell), code))
    rprint(f"[green]Cell {cell} edited[/green] (status: {updated.status.value})")


def cell_rm(session_id: str, cell: str) -> None:
    """Remove a cell from the notebook."""
    runtime = _get_runtime(session_id)
    _run(runtime.remove_cell(CellId(cell)))
    rprint(f"[green]Cell {cell} removed[/green]")
