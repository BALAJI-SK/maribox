"""Message display widget — renders a single chat message with styling."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from maribox.tui.message import ChatMessage, MessageRole


class MessageWidget(Vertical):
    """Widget that renders a single ChatMessage with role-appropriate styling."""

    DEFAULT_CSS = """
    MessageWidget {
        margin: 0 0 1 0;
        padding: 0 2;
        height: auto;
    }

    MessageWidget.user {
        border-left: outer $primary;
    }

    MessageWidget.assistant {
        border-left: outer $secondary;
    }

    MessageWidget.tool {
        border-left: outer $text-muted;
    }

    MessageWidget .msg-role {
        text-style: bold;
        margin-bottom: 0;
        height: 1;
    }

    MessageWidget .msg-role.user-role {
        color: $primary;
    }

    MessageWidget .msg-role.assistant-role {
        color: $secondary;
    }

    MessageWidget .msg-role.tool-role {
        color: $text-muted;
    }

    MessageWidget .msg-content {
        color: $text;
        margin-bottom: 0;
    }

    MessageWidget .msg-meta {
        color: $text-muted;
        text-style: italic;
        height: 1;
    }

    MessageWidget .tool-call {
        margin: 0 0 0 2;
        padding: 0 1;
        border-left: thin $border;
        color: $text-muted;
    }

    MessageWidget .tool-name {
        color: $accent;
        text-style: bold;
    }

    MessageWidget .tool-output {
        color: $text-muted;
        margin-top: 0;
    }
    """

    def __init__(self, message: ChatMessage, **kwargs) -> None:
        self._message = message
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        msg = self._message

        # Role label
        role_label = {
            MessageRole.USER: "You",
            MessageRole.ASSISTANT: "Assistant",
            MessageRole.TOOL: "Tool",
            MessageRole.SYSTEM: "System",
        }.get(msg.role, "Unknown")
        role_class = f"{msg.role.value}-role"

        yield Static(role_label, classes=f"msg-role {role_class}")

        # Content
        content = msg.content.strip()
        if content:
            yield Static(content, classes="msg-content", markup=True)

        # Tool calls
        for tc in msg.tool_calls:
            tool_text = f"▎ [bold accent]{tc.name}[/bold accent]"
            if tc.input_text:
                tool_text += f"\n▎ [dim]{tc.input_text[:200]}[/dim]"
            if tc.output_text:
                lines = tc.output_text.strip().splitlines()
                truncated = "\n".join(lines[:10])
                if len(lines) > 10:
                    truncated += f"\n▎ ... ({len(lines) - 10} more lines)"
                tool_text += f"\n▎ {truncated}"
            if tc.status == "running":
                tool_text += "\n▎ [italic]running...[/italic]"
            yield Static(tool_text, classes="tool-call", markup=True)

        # Meta line
        meta_parts: list[str] = []
        if msg.model:
            meta_parts.append(msg.model)
        if msg.format_duration():
            meta_parts.append(msg.format_duration())
        if msg.format_tokens():
            meta_parts.append(f"{msg.format_tokens()} tokens")
        if meta_parts:
            yield Static(" · ".join(meta_parts), classes="msg-meta", markup=False)

    def on_mount(self) -> None:
        msg = self._message
        self.add_class(msg.role.value)
