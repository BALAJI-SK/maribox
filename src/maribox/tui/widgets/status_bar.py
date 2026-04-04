"""Status bar widget — bottom bar with model info, tokens, and status messages."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static
from textual.message import Message
from textual import events


class StatusBar(Horizontal):
    """Bottom status bar showing model, tokens, and status messages.

    Layout: [help hint] [status message] ............... [tokens] [model]
    """

    DEFAULT_CSS = """
    StatusBar {
        background: $background-secondary;
        height: 1;
        padding: 0 2;
        dock: bottom;
    }

    StatusBar .help-hint {
        color: $text-muted;
        text-style: bold;
        height: 1;
    }

    StatusBar .status-msg {
        color: $info;
        margin-left: 2;
        height: 1;
    }

    StatusBar .status-msg.warn {
        color: $warning;
    }

    StatusBar .status-msg.error {
        color: $error;
    }

    StatusBar .right-section {
        dock: right;
        height: 1;
    }

    StatusBar .model-name {
        color: $text-secondary;
        margin-left: 2;
        height: 1;
    }

    StatusBar .token-usage {
        color: $text-muted;
        margin-left: 2;
        height: 1;
    }
    """

    class StatusMessage(Message):
        """Message posted to update the status bar text."""

        def __init__(self, text: str, msg_type: str = "info") -> None:
            self.text = text
            self.msg_type = msg_type
            super().__init__()

    def __init__(self, model: str = "", provider: str = "", **kwargs) -> None:
        self._model = model
        self._provider = provider
        self._tokens = ""
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Static("[bold]Ctrl+?[/bold] help", classes="help-hint")
        yield Static("", classes="status-msg", id="status-msg")
        with Horizontal(classes="right-section"):
            yield Static("", classes="token-usage", id="token-usage")
            yield Static(self._model_label(), classes="model-name", id="model-name")

    def _model_label(self) -> str:
        if self._model:
            return f"● {self._model}"
        if self._provider:
            return f"● {self._provider}"
        return "● no model"

    def set_model(self, model: str, provider: str = "") -> None:
        """Update the displayed model name."""
        self._model = model
        self._provider = provider
        try:
            widget = self.query_one("#model-name", Static)
            widget.update(self._model_label())
        except Exception:
            pass

    def set_tokens(self, total: int, cost: str = "") -> None:
        """Update token usage display."""
        if total > 1000:
            token_str = f"{total / 1000:.1f}K"
        else:
            token_str = str(total) if total > 0 else ""
        if cost:
            token_str += f", ${cost}"
        try:
            widget = self.query_one("#token-usage", Static)
            widget.update(f"Context: {token_str}" if token_str else "")
        except Exception:
            pass

    def set_status(self, text: str, msg_type: str = "info") -> None:
        """Update the status message (info, warn, error)."""
        try:
            widget = self.query_one("#status-msg", Static)
            widget.remove_class("warn", "error")
            if msg_type == "warn":
                widget.add_class("warn")
            elif msg_type == "error":
                widget.add_class("error")
            widget.update(text)
        except Exception:
            pass

    def clear_status(self) -> None:
        """Clear the status message."""
        self.set_status("")
