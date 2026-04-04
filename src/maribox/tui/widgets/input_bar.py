"""Input bar widget — multi-line text input for sending messages."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, TextArea
from textual.message import Message
from textual import events


class InputBar(Vertical):
    """Bottom input area with prompt indicator and text area.

    Enter sends the message. \\+Enter inserts a newline.
    """

    DEFAULT_CSS = """
    InputBar {
        height: auto;
        max-height: 12;
        min-height: 5;
        background: $background-secondary;
        border-top: solid $border;
        padding: 1 2 0 2;
    }

    InputBar:focus-within {
        border-top: solid $primary;
    }

    #input-row {
        height: auto;
    }

    #input-prompt {
        color: $primary;
        text-style: bold;
        height: 1;
        width: 2;
    }

    #message-input {
        height: auto;
        max-height: 8;
        min-height: 3;
        background: $background-secondary;
        border: none;
        padding: 0;
    }

    #message-input:focus {
        border: none;
    }

    #message-input.text-area:focus {
        border: none;
    }

    #input-hint {
        color: $text-muted;
        height: 1;
        padding: 0 2;
    }
    """

    class Submitted(Message):
        """Posted when the user submits a message."""

        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-row"):
            yield Static(">", id="input-prompt")
            yield TextArea(id="message-input")
        yield Static(
            "[dim]Enter to send · \\+Enter for newline · Ctrl+K commands[/dim]",
            id="input-hint",
        )

    def on_mount(self) -> None:
        text_area = self.query_one("#message-input", TextArea)
        text_area.focus()

    def on_key(self, event: events.Key) -> None:
        """Handle key events in the input area."""
        if event.key == "enter":
            # Check if the previous character is a backslash for newline
            text_area = self.query_one("#message-input", TextArea)
            text = text_area.text
            cursor_pos = text_area.cursor_location

            # Get current line
            lines = text.split("\n")
            row = cursor_pos[0]
            if row < len(lines):
                line = lines[row]
                col = cursor_pos[1]
                if col > 0 and line[col - 1:col] == "\\":
                    # Backslash + Enter = newline (replace \ with \n)
                    event.prevent_default()
                    event.stop()
                    # Replace the backslash with a newline
                    new_line = line[:col - 1] + line[col:]
                    lines[row] = new_line
                    lines.insert(row + 1, "")
                    text_area.load_text("\n".join(lines))
                    # Move cursor to start of new line
                    text_area.move_cursor((row + 1, 0))
                    return

            # Regular Enter = send message
            event.prevent_default()
            event.stop()
            self._submit()

    def _submit(self) -> None:
        """Submit the current text as a message."""
        text_area = self.query_one("#message-input", TextArea)
        text = text_area.text.strip()
        if not text:
            return
        self.post_message(self.Submitted(text))
        text_area.load_text("")

    def focus_input(self) -> None:
        """Focus the text input."""
        text_area = self.query_one("#message-input", TextArea)
        text_area.focus()

    def set_placeholder(self, text: str) -> None:
        """Set a hint in the input hint area."""
        try:
            hint = self.query_one("#input-hint", Static)
            hint.update(f"[dim]{text}[/dim]")
        except Exception:
            pass
