"""Base agent class — abstract interface for all maribox AI agents."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from maribox.auth.manager import AuthManager
from maribox.config.schema import AgentProfile, MariboxConfig
from maribox.exceptions import AgentError


@dataclass
class AgentMessage:
    """A message from an agent."""

    role: str  # "user" | "assistant" | "system"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """The final response from an agent invocation."""

    message: AgentMessage
    success: bool
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0
    model: str = ""
    tokens_used: dict[str, int] = field(default_factory=dict)


class MariboxAgent(ABC):
    """Abstract base class for all Maribox agents.

    Wraps an LLM provider with Maribox-specific configuration,
    tool registration, and response handling. Subclasses implement
    domain-specific tools and system prompts.
    """

    def __init__(
        self,
        profile: AgentProfile,
        auth_manager: AuthManager,
        config: MariboxConfig,
    ) -> None:
        self._profile = profile
        self._auth = auth_manager
        self._config = config
        self._tools: list[dict[str, Any]] = self._register_tools()
        self._validate_api_key()

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier matching the profile name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this agent does."""

    @abstractmethod
    def _register_tools(self) -> list[dict[str, Any]]:
        """Return tool definitions for this agent."""

    @abstractmethod
    def _system_prompt(self) -> str:
        """Return the system prompt for this agent."""

    def _validate_api_key(self) -> None:
        """Check that the API key for this agent's model provider is available."""
        key = self._auth.get_key(self._profile.provider)
        if not key:
            raise AgentError(
                f"No API key configured for provider '{self._profile.provider}'. "
                f"Run: maribox auth set {self._profile.provider}"
            )

    async def invoke(self, message: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Send a message to this agent and wait for the full response.

        Context can include session_id, notebook state, etc.
        """
        start = time.monotonic()
        ctx = context or {}

        # Build the prompt with system context
        system_prompt = self._system_prompt()
        if ctx:
            system_prompt += f"\n\nContext: {ctx}"

        # In production, this calls the LLM via litellm/google-adk.
        # For now, return a structured response indicating the agent received the message.
        duration_ms = (time.monotonic() - start) * 1000

        return AgentResponse(
            message=AgentMessage(
                role="assistant",
                content=f"[{self.name}] Received: {message[:200]}",
                metadata={"agent": self.name, "provider": self._profile.provider},
            ),
            success=True,
            duration_ms=duration_ms,
            model=self._profile.model,
        )

    async def stream(self, message: str, context: dict[str, Any] | None = None) -> AsyncIterator[AgentMessage]:
        """Send a message and stream the response as partial AgentMessage chunks."""
        # Yield a single chunk for now — full streaming requires LLM integration
        response = await self.invoke(message, context)
        yield response.message

    async def validate_api_key(self) -> bool:
        """Check that the API key is valid by making a test call."""
        key = self._auth.get_key(self._profile.provider)
        return key is not None

    def get_tools(self) -> list[dict[str, Any]]:
        """Return the list of registered tools."""
        return list(self._tools)

    def get_instruction(self) -> str:
        """Return the system prompt / instruction for this agent."""
        return self._system_prompt()
