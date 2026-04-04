"""Session management tools for agents — create, list, kill, and check sessions."""

from __future__ import annotations

from typing import Any


def create_session_tool() -> dict[str, Any]:
    """Return a tool definition for creating a new session."""
    return {
        "name": "create_session",
        "description": "Create a new isolated local notebook session.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Optional human-readable name for the session",
                },
            },
        },
    }


def list_sessions_tool() -> dict[str, Any]:
    """Return a tool definition for listing all sessions."""
    return {
        "name": "list_sessions",
        "description": "List all notebook sessions with their status.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    }


def kill_session_tool() -> dict[str, Any]:
    """Return a tool definition for killing a session."""
    return {
        "name": "kill_session",
        "description": "Force-stop a session and clean up its resources.",
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "ID of the session to kill",
                },
            },
            "required": ["session_id"],
        },
    }


def get_session_status_tool() -> dict[str, Any]:
    """Return a tool definition for checking session status."""
    return {
        "name": "get_session_status",
        "description": "Get detailed status information for a session.",
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "ID of the session to check",
                },
            },
            "required": ["session_id"],
        },
    }
