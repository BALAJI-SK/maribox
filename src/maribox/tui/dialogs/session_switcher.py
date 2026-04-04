"""Session switcher dialog — modal overlay for switching between sessions."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from maribox.tui.message import Conversation


class SessionSwitcher(ModalScreen[str | None]):
    """Modal dialog for switching between conversation sessions."""

    DEFAULT_CSS = """
    SessionSwitcher {
        align: center middle;
    }

    #session-switcher-container {
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        width: 60;
        height: auto;
        max-height: 20;
    }

    .switcher-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
        height: 1;
    }

    .session-entry {
        height: 1;
        padding: 0 1;
        color: $text;
    }

    .session-entry:hover {
        background: $surface;
    }

    .session-entry.selected {
        background: $primary-dim;
        color: $text-emphasized;
    }

    .session-entry .entry-id {
        color: $primary;
    }

    .session-entry .entry-title {
        color: $text;
    }

    .session-entry .entry-count {
        color: $text-muted;
        dock: right;
    }

    .no-sessions {
        color: $text-muted;
        padding: 1;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
        Binding("up", "move_up", show=False),
        Binding("down", "move_down", show=False),
        Binding("k", "move_up", show=False),
        Binding("j", "move_down", show=False),
        Binding("enter", "select", show=False),
    ]

    def __init__(self, sessions: list[Conversation], **kwargs) -> None:
        self._sessions = sessions
        self._selected = 0
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="session-switcher-container"):
            yield Static("[bold cyan]Sessions[/bold cyan]", classes="switcher-title")
            if not self._sessions:
                yield Static("[dim]No sessions yet. Press Ctrl+N to create one.[/dim]", classes="no-sessions")
            else:
                for i, session in enumerate(self._sessions):
                    title = session.title or f"Session {session.id[:8]}"
                    count = f"{session.message_count} msgs"
                    selected_class = " selected" if i == self._selected else ""
                    yield Static(
                        f"  [cyan]{session.id[:8]}[/cyan]  {title}  [dim]{count}[/dim]",
                        classes=f"session-entry{selected_class}",
                    )

    def action_move_up(self) -> None:
        if self._sessions and self._selected > 0:
            self._selected -= 1
            self._refresh_selection()

    def action_move_down(self) -> None:
        if self._sessions and self._selected < len(self._sessions) - 1:
            self._selected += 1
            self._refresh_selection()

    def action_select(self) -> None:
        if self._sessions and 0 <= self._selected < len(self._sessions):
            self.dismiss(self._sessions[self._selected].id)
        else:
            self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)

    def _refresh_selection(self) -> None:
        entries = self.query(".session-entry")
        for i, entry in enumerate(entries):
            if i == self._selected:
                entry.add_class("selected")
            else:
                entry.remove_class("selected")
