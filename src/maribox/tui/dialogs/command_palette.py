"""Command palette dialog — modal overlay for running commands by name."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, Input

from maribox.tui.message import Conversation


class CommandPalette(ModalScreen[str | None]):
    """Modal dialog for selecting and running commands."""

    DEFAULT_CSS = """
    CommandPalette {
        align: center middle;
    }

    #command-palette-container {
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        width: 60;
        height: auto;
        max-height: 20;
    }

    .palette-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
        height: 1;
    }

    #command-filter {
        margin-bottom: 1;
    }

    .command-entry {
        height: 1;
        padding: 0 1;
        color: $text;
    }

    .command-entry:hover {
        background: $surface;
    }

    .command-entry.selected {
        background: $primary-dim;
        color: $text-emphasized;
    }

    .command-entry .cmd-name {
        color: $primary;
    }

    .command-entry .cmd-desc {
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("up", "move_up", show=False),
        Binding("down", "move_down", show=False),
        Binding("enter", "select", show=False),
    ]

    # Available commands: (name, description)
    COMMANDS: list[tuple[str, str]] = [
        ("new-session", "Create a new session"),
        ("list-sessions", "List all sessions"),
        ("switch-session", "Switch to a different session"),
        ("attach-session", "Attach TUI to a session"),
        ("stop-session", "Stop the current session"),
        ("snapshot", "Save snapshot of current session"),
        ("run-all-cells", "Run all notebook cells"),
        ("show-notebook", "Show notebook source"),
        ("save-notebook", "Save notebook to file"),
        ("generate-ui", "Generate marimo UI components"),
        ("debug-last", "Debug last error"),
        ("explain-cell", "Explain a cell's code"),
        ("list-agents", "List available agents"),
        ("run-agent", "Run an agent with a prompt"),
        ("compact", "Compact conversation history"),
        ("clear", "Clear conversation"),
        ("help", "Show help"),
    ]

    def __init__(self, **kwargs) -> None:
        self._selected = 0
        self._filtered: list[tuple[str, str]] = list(self.COMMANDS)
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="command-palette-container"):
            yield Static("[bold cyan]Commands[/bold cyan]", classes="palette-title")
            yield Input(placeholder="Filter commands...", id="command-filter")
            self._render_commands()

    def _render_commands(self) -> None:
        # Remove old command list if exists
        try:
            old = self.query(".command-entry")
            for widget in old:
                widget.remove()
        except Exception:
            pass

        container = self.query_one("#command-palette-container", Vertical)
        for i, (name, desc) in enumerate(self._filtered):
            selected_class = " selected" if i == self._selected else ""
            widget = Static(
                f"  [cyan]{name:<20}[/cyan] [dim]{desc}[/dim]",
                classes=f"command-entry{selected_class}",
            )
            # Mount before any help text if present
            container.mount(widget)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as the user types."""
        if event.input.id == "command-filter":
            query = event.value.lower().strip()
            if not query:
                self._filtered = list(self.COMMANDS)
            else:
                self._filtered = [
                    (name, desc)
                    for name, desc in self.COMMANDS
                    if query in name or query in desc
                ]
            self._selected = 0
            self._render_commands()

    def action_move_up(self) -> None:
        if self._filtered and self._selected > 0:
            self._selected -= 1
            self._refresh_selection()

    def action_move_down(self) -> None:
        if self._filtered and self._selected < len(self._filtered) - 1:
            self._selected += 1
            self._refresh_selection()

    def action_select(self) -> None:
        if self._filtered and 0 <= self._selected < len(self._filtered):
            self.dismiss(self._filtered[self._selected][0])
        else:
            self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)

    def _refresh_selection(self) -> None:
        entries = self.query(".command-entry")
        for i, entry in enumerate(entries):
            if i == self._selected:
                entry.add_class("selected")
            else:
                entry.remove_class("selected")
