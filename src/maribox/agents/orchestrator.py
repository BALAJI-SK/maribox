"""Orchestrator agent — routes requests to specialized sub-agents."""

from __future__ import annotations

from typing import Any

from maribox.agents.base import AgentResponse, MariboxAgent
from maribox.auth.manager import AuthManager
from maribox.config.schema import AgentProfile, MariboxConfig

# Routing keywords -> agent name
_ROUTING_RULES: dict[str, list[str]] = {
    "notebook": ["cell", "code", "notebook", "variable", "function", "import", "class", "write", "create cell"],
    "ui": ["ui", "component", "widget", "form", "table", "chart", "layout", "button", "slider", "display"],
    "debug": ["error", "fix", "debug", "traceback", "exception", "bug", "fail", "broken", "wrong"],
    "session": ["session", "start", "stop", "kill", "snapshot", "environment"],
}


class OrchestratorAgent(MariboxAgent):
    """Top-level agent that receives user requests and delegates to sub-agents.

    Uses keyword-based routing with optional LLM fallback for ambiguous requests.
    """

    def __init__(
        self,
        sub_agents: dict[str, MariboxAgent],
        profile: AgentProfile,
        auth_manager: AuthManager,
        config: MariboxConfig,
    ) -> None:
        self._sub_agents = sub_agents
        super().__init__(profile, auth_manager, config)

    @property
    def name(self) -> str:
        return "orchestrator"

    @property
    def description(self) -> str:
        return "Routes user requests to the appropriate specialized agent."

    def _register_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "delegate_to_agent",
                "description": "Delegate a task to a specialized sub-agent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent": {"type": "string", "description": "Name of the sub-agent"},
                        "message": {"type": "string", "description": "The task to delegate"},
                    },
                    "required": ["agent", "message"],
                },
            }
        ]

    def _system_prompt(self) -> str:
        agent_list = ", ".join(self._sub_agents.keys())
        return (
            "You are the maribox orchestrator agent. Your job is to receive user requests "
            "and delegate them to the appropriate specialized agent.\n"
            f"Available agents: {agent_list}\n"
            "Analyze the user's request and route it to the best agent for the task."
        )

    def _route_request(self, message: str) -> str:
        """Analyze the user message and determine which sub-agent to delegate to."""
        lower = message.lower()
        scores: dict[str, int] = {}

        for agent_name, keywords in _ROUTING_RULES.items():
            score = sum(1 for kw in keywords if kw in lower)
            if score > 0:
                scores[agent_name] = score

        if scores:
            return max(scores, key=lambda k: scores[k])

        return "notebook"  # default

    async def invoke(self, message: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Route the message to the appropriate sub-agent and return its response."""
        agent_name = self._route_request(message)
        return await self.invoke_with_agent(agent_name, message, context)

    async def invoke_with_agent(
        self,
        agent_name: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> AgentResponse:
        """Directly invoke a specific sub-agent by name."""
        agent = self._sub_agents.get(agent_name)
        if agent is None:
            available = list(self._sub_agents.keys())
            from maribox.exceptions import AgentError

            raise AgentError(f"Unknown agent '{agent_name}'. Available: {available}")
        return await agent.invoke(message, context)

    def list_agents(self) -> list[str]:
        """Return the names of all available sub-agents."""
        return list(self._sub_agents.keys())
