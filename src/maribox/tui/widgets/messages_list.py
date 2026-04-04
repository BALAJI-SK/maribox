"""Messages list widget — scrollable container for chat messages."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from maribox.tui.message import ChatMessage
from maribox.tui.widgets.message_display import MessageWidget
from maribox.tui.widgets.welcome import WelcomeWidget


class MessagesList(VerticalScroll):
    """Scrollable list of chat messages with auto-scroll."""

    DEFAULT_CSS = """
    MessagesList {
        width: 1fr;
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
        scrollbar-size: 1 1;
    }

    MessagesList:focus {
        border: none;
    }

    #thinking-indicator {
        color: $secondary;
        padding: 1 2;
        display: none;
        height: auto;
    }

    #thinking-indicator.visible {
        display: block;
    }
    """

    def __init__(
        self,
        cwd: str = "",
        provider: str = "",
        model: str = "",
        **kwargs,
    ) -> None:
        self._cwd = cwd
        self._provider = provider
        self._model = model
        self._auto_scroll = True
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield WelcomeWidget(
            cwd=self._cwd,
            provider=self._provider,
            model=self._model,
        )
        yield Static("● Thinking...", id="thinking-indicator")

    def on_mount(self) -> None:
        self.hide_thinking()

    def show_thinking(self) -> None:
        """Show the thinking indicator."""
        indicator = self.query_one("#thinking-indicator", Static)
        indicator.add_class("visible")

    def hide_thinking(self) -> None:
        """Hide the thinking indicator."""
        indicator = self.query_one("#thinking-indicator", Static)
        indicator.remove_class("visible")

    def add_message(self, message: ChatMessage) -> MessageWidget:
        """Add a new message and auto-scroll to bottom."""
        # Remove welcome screen if it exists
        try:
            welcome = self.query_one(WelcomeWidget)
            welcome.remove()
        except Exception:
            pass

        widget = MessageWidget(message)
        # Insert before the thinking indicator
        indicator = self.query_one("#thinking-indicator", Static)
        self.mount(widget, before=indicator)

        if self._auto_scroll:
            self.call_after_refresh(self._scroll_to_bottom)
        return widget

    def _scroll_to_bottom(self) -> None:
        """Scroll the messages list to the bottom."""
        self.scroll_end(animate=False)

    def update_last_assistant(self, content: str) -> None:
        """Update the content of the last assistant message (for streaming)."""
        children = list(self.children)
        for child in reversed(children):
            if isinstance(child, MessageWidget) and child._message.is_assistant:
                child._message.content = content
                # Re-render the content
                try:
                    content_widget = child.query_one(".msg-content", Static)
                    content_widget.update(content)
                except Exception:
                    pass
                if self._auto_scroll:
                    self.call_after_refresh(self._scroll_to_bottom)
                return
