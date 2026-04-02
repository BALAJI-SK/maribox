"""Session agent — session lifecycle management and resource monitoring."""

from __future__ import annotations

from typing import Any

from maribox.agents.base import MariboxAgent
from maribox.agents.tools.session_tools import (
    create_session_tool,
    get_session_status_tool,
    kill_session_tool,
    list_sessions_tool,
)


class SessionAgent(MariboxAgent):
    """Agent specialized in session management:
    creating sessions, switching between them, managing resources.
    """

    @property
    def name(self) -> str:
        return "session"

    @property
    def description(self) -> str:
        return "Manages session lifecycle: create, list, monitor, and kill sessions."

    def _register_tools(self) -> list[dict[str, Any]]:
        return [
            create_session_tool(),
            list_sessions_tool(),
            kill_session_tool(),
            get_session_status_tool(),
        ]

    def _system_prompt(self) -> str:
        return (
            "You are the maribox session agent. You help users manage their notebook sessions.\n\n"
            "Capabilities:\n"
            "- Create new isolated sessions with sandbox containers\n"
            "- List running sessions and their status\n"
            "- Stop or kill sessions that are no longer needed\n"
            "- Check session resource usage and health\n\n"
            "Each session runs in an isolated sandbox with its own marimo kernel. "
            "Sessions are identified by short hex IDs."
        )
