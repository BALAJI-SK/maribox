"""Dashboard screen — grid of session cards with auto-refresh."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label, Static

from maribox.tui.widgets.session_card import SessionCard


class DashboardScreen(Screen):
    """Dashboard showing all sessions as cards in a grid."""

    DEFAULT_CSS = """
    DashboardScreen {
        layout: vertical;
    }
    #dashboard-grid {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
    }
    """

    def __init__(self, session_id: str | None = None) -> None:
        super().__init__()
        self._session_id = session_id

    def compose(self) -> ComposeResult:
        yield Label("[bold]maribox Dashboard[/bold]", id="dashboard-title")
        with Container(id="dashboard-grid"):
            # Placeholder cards — in production, these come from SessionManager
            yield SessionCard(session_id="demo-1", session_name="Example Session", status="running")
            yield SessionCard(session_id="demo-2", session_name="Data Analysis", status="idle")
            yield Static("[dim]Press 'd' for dashboard, 'a' for agents, 'q' to quit[/dim]")

    def on_mount(self) -> None:
        # Auto-refresh every 5 seconds in production
        pass
