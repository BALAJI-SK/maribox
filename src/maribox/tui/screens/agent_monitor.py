"""Agent monitor screen — real-time feed of agent activity."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, RichLog


class AgentMonitorScreen(Screen):
    """Live feed of agent messages and activity."""

    DEFAULT_CSS = """
    AgentMonitorScreen {
        layout: vertical;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("[bold]Agent Monitor[/bold]")
        yield RichLog(id="agent-log", highlight=True, markup=True)

    def on_mount(self) -> None:
        log = self.query_one("#agent-log", RichLog)
        log.write("[dim]Agent monitor started. Waiting for agent activity...[/dim]")
        log.write("[cyan]orchestrator[/cyan] — ready")
        log.write("[green]notebook[/green] — ready")
        log.write("[yellow]debug[/yellow] — ready")
        log.write("[magenta]ui[/magenta] — ready")
        log.write("[blue]session[/blue] — ready")
