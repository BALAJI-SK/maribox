"""Session CLI commands — manage notebook sessions."""

from __future__ import annotations

from pathlib import Path

from rich import print as rprint
from rich.table import Table

from maribox.sandbox.session import SessionManager


def _get_manager() -> SessionManager:
    return SessionManager()


def session_new(
    name: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> None:
    """Create a new local marimo session."""
    manager = _get_manager()
    info = manager.create_session(name=name, provider=provider, model=model)
    rprint("[green]Session created![/green]")
    rprint(f"  ID: [cyan]{info.id}[/cyan]")
    rprint(f"  Name: {info.name}")
    rprint(f"  Provider: {info.provider}")
    rprint(f"  Model: {info.model}")
    rprint(f"  Status: {info.status.value}")


def session_list() -> None:
    """Table of all sessions."""
    manager = _get_manager()
    sessions = manager.list_sessions()

    if not sessions:
        rprint("[dim]No sessions found. Use 'maribox session new' to create one.[/dim]")
        return

    table = Table(title="maribox Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Created")

    status_colors = {
        "running": "[green]running[/green]",
        "idle": "[dim]idle[/dim]",
        "error": "[red]error[/red]",
        "stopped": "[gray]stopped[/gray]",
        "creating": "[yellow]creating[/yellow]",
    }

    for s in sessions:
        status = status_colors.get(s.status.value, s.status.value)
        table.add_row(s.id, s.name, status, s.provider, s.model, s.created_at[:19])

    from rich.console import Console
    Console().print(table)


def session_attach(session_id: str) -> None:
    """Open the TUI attached to an existing session."""
    manager = _get_manager()
    info = manager.get_session(session_id)
    rprint(f"[dim]TUI attach for session {info.id} ({info.name}) — requires Phase 9 TUI[/dim]")


def session_stop(session_id: str) -> None:
    """Gracefully shut down a session."""
    manager = _get_manager()
    manager.stop_session(session_id)
    rprint(f"[green]Session {session_id} stopped.[/green]")


def session_kill(session_id: str) -> None:
    """Force-terminate a session without cleanup."""
    manager = _get_manager()
    manager.kill_session(session_id)
    rprint(f"[yellow]Session {session_id} killed.[/yellow]")


def session_snapshot(session_id: str, out: str | None = None) -> None:
    """Save notebook + logs to a snapshot archive."""
    manager = _get_manager()
    out_path = Path(out) if out else None
    result = manager.snapshot_session(session_id, out_path)
    rprint(f"[green]Snapshot saved to {result}[/green]")


def session_rm(session_id: str) -> None:
    """Remove session directory."""
    manager = _get_manager()
    manager.remove_session(session_id)
    rprint(f"[green]Session {session_id} removed.[/green]")
