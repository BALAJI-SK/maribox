"""Maribox TUI — OpenCode-style Textual application for AI-assisted notebook development."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding

from maribox.tui.screens.chat import ChatScreen


class MariboxApp(App):
    """Maribox TUI — OpenCode-style AI coding interface.

    Layout:
    ┌──────────────────────────────────────────────────┐
    │  Messages List (left)          │ Sidebar (right)  │
    │  - User/Assistant messages     │ - Session info   │
    │  - Tool call outputs           │ - Files          │
    │  - Markdown rendering          │ - Agents         │
    ├──────────────────────────────────────────────────┤
    │  > Input area (multi-line)                       │
    │    Enter to send · \\+Enter for newline            │
    ├──────────────────────────────────────────────────┤
    │  [Ctrl+? help] [status] ... [tokens] [model]     │
    └──────────────────────────────────────────────────┘
    """

    TITLE = "maribox"
    CSS_PATH = "styles.tcss"

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+c", "quit", "Quit", show=True, priority=True),
    ]

    def __init__(
        self,
        session_id: str | None = None,
        provider: str = "",
        model: str = "",
    ) -> None:
        self._session_id = session_id
        self._provider = provider
        self._model = model
        super().__init__()

    def compose(self) -> ComposeResult:
        yield ChatScreen(
            session_id=self._session_id,
            provider=self._provider,
            model=self._model,
        )

    def on_mount(self) -> None:
        """Configure the app on mount."""
        self.dark = True
