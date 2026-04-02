"""Debug CLI commands — analyze errors, propose fixes, explain cells."""

from __future__ import annotations

import asyncio

from rich import print as rprint
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

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
    return MarimoRuntime(sandbox_url=meta.get("sandbox_url", ""))


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def debug_last(session_id: str) -> None:
    """Show the last error with stack trace and cell context."""
    runtime = _get_runtime(session_id)
    errors = _run(runtime.get_errors())

    if not errors:
        rprint("[green]No errors found in the current notebook.[/green]")
        return

    table = Table(title="Cell Errors")
    table.add_column("Cell ID", style="cyan")
    table.add_column("Status", style="red")
    table.add_column("Output")

    for cell in errors:
        outputs = cell.outputs[-1].text if cell.outputs else "No output"
        table.add_row(cell.id, cell.status, outputs[:100])

    rprint(table)

    # Show the last error in detail
    last = errors[-1]
    rprint(Panel(
        Syntax(last.code, "python", theme="monokai"),
        title=f"[red]Last Error: {last.id}[/red]",
    ))
    if last.outputs:
        for output in last.outputs:
            if output.type == "error":
                rprint(Panel(output.text, title="Error Output", border_style="red"))


def debug_fix(session_id: str, cell: str | None = None) -> None:
    """DebugAgent analyses the error and proposes a fix.

    In production, this invokes the DebugAgent via the orchestrator.
    For now, it shows the error and suggests next steps.
    """
    runtime = _get_runtime(session_id)
    errors = _run(runtime.get_errors())

    if not errors:
        rprint("[green]No errors to fix.[/green]")
        return

    target = None
    if cell:
        target = next((c for c in errors if c.id == cell), None)
        if not target:
            rprint(f"[red]Cell {cell} not found in errors. Error cells: {', '.join(c.id for c in errors)}[/red]")
            return
    else:
        target = errors[-1]

    rprint(f"[cyan]Analyzing error in cell {target.id}...[/cyan]")
    rprint(Panel(
        Syntax(target.code, "python", theme="monokai"),
        title=f"[yellow]Cell: {target.id}[/yellow]",
    ))

    if target.outputs:
        for output in target.outputs:
            rprint(Panel(output.text, title=f"[red]{output.type}[/red]", border_style="red"))

    rprint("[dim]Tip: Use `maribox debug explain --session <id> --cell <cell_id>` for detailed analysis.[/dim]")
    rprint("[dim]Or use `maribox agent run debug --prompt \"fix cell <cell_id>\" --session <id>`[/dim]")


def debug_explain(session_id: str, cell: str) -> None:
    """Explain what a cell does and its dependencies."""
    runtime = _get_runtime(session_id)
    target = _run(runtime.get_cell(cell))

    rprint(Panel(
        Syntax(target.code, "python", theme="monokai"),
        title=f"[cyan]Cell: {target.id}[/cyan]",
    ))

    rprint(f"[dim]Status: {target.status}[/dim]")
    rprint(f"[dim]Outputs: {len(target.outputs)}[/dim]")

    if target.outputs:
        for output in target.outputs:
            rprint(Panel(output.text, title=f"[green]{output.type}[/green]"))
