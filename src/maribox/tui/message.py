"""Message data model for the TUI chat interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MessageRole(StrEnum):
    """Role of a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


@dataclass
class ToolCall:
    """A tool invocation within a message."""

    name: str
    input_text: str = ""
    output_text: str = ""
    status: str = "pending"  # pending | running | done | error
    duration_ms: float = 0.0


@dataclass
class ChatMessage:
    """A single message in the conversation."""

    id: str
    role: MessageRole
    content: str
    timestamp: str = ""
    model: str = ""
    duration_ms: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)
    tool_calls: list[ToolCall] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_user(self) -> bool:
        return self.role == MessageRole.USER

    @property
    def is_assistant(self) -> bool:
        return self.role == MessageRole.ASSISTANT

    @property
    def is_tool(self) -> bool:
        return self.role == MessageRole.TOOL

    def format_duration(self) -> str:
        """Format duration as human-readable string."""
        if self.duration_ms <= 0:
            return ""
        seconds = self.duration_ms / 1000
        if seconds < 1:
            return f"{self.duration_ms:.0f}ms"
        return f"{seconds:.1f}s"

    def format_tokens(self) -> str:
        """Format token usage as human-readable string."""
        if not self.token_usage:
            return ""
        total = self.token_usage.get("total", 0)
        if total > 1000:
            return f"{total / 1000:.1f}K"
        return str(total)


@dataclass
class Conversation:
    """A conversation thread with messages."""

    id: str
    title: str = ""
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: str = ""
    model: str = ""
    provider: str = ""

    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        if not self.title and message.is_user:
            self.title = message.content[:50] + ("..." if len(message.content) > 50 else "")

    def last_message(self) -> ChatMessage | None:
        """Return the most recent message."""
        return self.messages[-1] if self.messages else None

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def total_tokens(self) -> int:
        return sum(m.token_usage.get("total", 0) for m in self.messages)
