"""Help dialog — modal overlay showing all key bindings."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class HelpScreen(ModalScreen[None]):
    """Modal help overlay showing key bindings."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-container {
        background: $surface;
        border: thick $primary;
        padding: 1 3;
        width: 72;
        height: auto;
        max-height: 28;
    }

    #help-container .help-title {
        color: $primary;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
        height: 1;
    }

    #help-container .key-section {
        margin-bottom: 1;
        height: auto;
    }

    #help-container .section-label {
        color: $secondary;
        text-style: bold;
        height: 1;
    }

    #help-container .key-row {
        color: $text;
        height: 1;
    }

    #help-container .key-name {
        color: $primary;
        text-style: bold;
    }

    #help-container .key-desc {
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("ctrl+question", "close", "Close", show=False),
        Binding("ctrl+h", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-container"):
            yield Static("[bold cyan]⌬ maribox — Key Bindings[/bold cyan]", classes="help-title")
            yield Static("", classes="section-label key-section")

            yield self._section("General", [
                ("Ctrl+?", "Show this help"),
                ("Ctrl+C", "Quit maribox"),
                ("Ctrl+K", "Command palette"),
                ("Ctrl+L", "Toggle sidebar"),
                ("Ctrl+S", "Session switcher"),
                ("Ctrl+O", "Model selector"),
                ("Ctrl+N", "New session"),
                ("Ctrl+T", "Cycle theme"),
            ])
            yield self._section("Chat", [
                ("Enter", "Send message"),
                ("\\+Enter", "Insert newline"),
                ("Escape", "Cancel generation"),
                ("PageUp/Down", "Scroll messages"),
            ])
            yield self._section("Navigation", [
                ("Tab", "Switch focus"),
                ("j/k or ↑/↓", "Navigate lists"),
                ("Enter", "Select item"),
            ])

    def _section(self, title: str, bindings: list[tuple[str, str]]) -> Static:
        """Build a key binding section as a Static widget."""
        lines = [f"[bold][{title}][/bold]"]
        for key, desc in bindings:
            lines.append(
                f"  [cyan]{key:<16}[/cyan] [dim]{desc}[/dim]"
            )
        return Static("\n".join(lines), classes="key-section")

    def action_close(self) -> None:
        self.dismiss(None)
