"""Session view screen — 3-pane layout for notebook editing."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, RichLog

from maribox.tui.widgets.agent_feed import AgentFeed
from maribox.tui.widgets.cell_panel import CellPanel


class SessionViewScreen(Screen):
    """3-pane session view: source left, output right, agent log bottom."""

    DEFAULT_CSS = """
    SessionViewScreen {
        layout: vertical;
    }
    .main-panes {
        layout: horizontal;
        height: 3fr;
    }
    .source-pane {
        width: 1fr;
        border: solid $primary;
    }
    .output-pane {
        width: 1fr;
        border: solid $success;
    }
    .agent-pane {
        height: 1fr;
        border: solid $accent;
    }
    """

    def __init__(self, session_id: str) -> None:
        super().__init__()
        self._session_id = session_id

    def compose(self) -> ComposeResult:
        yield Label(f"[bold]Session: {self._session_id}[/bold]")
        with Horizontal(classes="main-panes"):
            with Vertical(classes="source-pane"):
                yield CellPanel(title="Source")
            with Vertical(classes="output-pane"):
                yield RichLog(id="output-log", highlight=True, markup=True)
        with Vertical(classes="agent-pane"):
            yield AgentFeed()
