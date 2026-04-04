"""Quit confirmation dialog."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class QuitDialog(ModalScreen[bool]):
    """Modal confirmation dialog for quitting."""

    DEFAULT_CSS = """
    QuitDialog {
        align: center middle;
    }

    #quit-container {
        background: $surface;
        border: thick $primary;
        padding: 1 3;
        width: 40;
        height: auto;
    }

    #quit-container .quit-text {
        color: $text;
        text-align: center;
        margin-bottom: 1;
        height: 1;
    }

    #quit-container .quit-buttons {
        height: 1;
        align: center middle;
    }

    .quit-btn {
        padding: 0 2;
        margin: 0 1;
        height: 1;
    }

    .quit-btn.yes {
        color: $error;
        text-style: bold;
    }

    .quit-btn.yes.selected {
        background: $error;
        color: $text-emphasized;
    }

    .quit-btn.no {
        color: $primary;
        text-style: bold;
    }

    .quit-btn.no.selected {
        background: $primary;
        color: $text-emphasized;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("left", "prev", show=False),
        Binding("right", "next", show=False),
        Binding("h", "prev", show=False),
        Binding("l", "next", show=False),
        Binding("tab", "next", show=False),
        Binding("enter", "confirm", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        self._selected = 1  # Default to "No"
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Vertical(id="quit-container"):
            yield Static("Are you sure you want to quit?", classes="quit-text")
            with Horizontal(classes="quit-buttons"):
                yield Static("  Yes  ", classes="quit-btn yes")
                yield Static("  No  ", classes="quit-btn no selected")

    def action_prev(self) -> None:
        self._selected = 0
        self._refresh()

    def action_next(self) -> None:
        self._selected = 1
        self._refresh()

    def action_confirm(self) -> None:
        self.dismiss(self._selected == 0)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _refresh(self) -> None:
        buttons = self.query(".quit-btn")
        for i, btn in enumerate(buttons):
            if i == self._selected:
                btn.add_class("selected")
            else:
                btn.remove_class("selected")
