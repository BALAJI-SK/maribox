"""Maribox TUI — main Textual application."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from maribox.tui.screens.dashboard import DashboardScreen


class MariboxApp(App):
    """Maribox TUI — multi-session notebook orchestrator."""

    TITLE = "maribox"
    CSS_PATH = "styles.tcss"

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit", show=True),
        Binding("d", "show_dashboard", "Dashboard", show=True),
        Binding("a", "show_agents", "Agents", show=True),
    ]

    def __init__(self, session_id: str | None = None) -> None:
        super().__init__()
        self._session_id = session_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen(session_id=self._session_id))

    def action_show_dashboard(self) -> None:
        self.push_screen(DashboardScreen(session_id=self._session_id))

    def action_show_agents(self) -> None:
        from maribox.tui.screens.agent_monitor import AgentMonitorScreen

        self.push_screen(AgentMonitorScreen())
