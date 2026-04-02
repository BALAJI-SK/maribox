"""Tool implementations for the maribox MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from rich.console import Console

from maribox.auth.manager import AuthManager
from maribox.config.io import load_config
from maribox.config.resolution import resolve_config_root
from maribox.config.schema import MariboxConfig

MAX_RESPONSE_LENGTH = 10_000


@dataclass
class ToolContext:
    """Shared context for all tool implementations."""

    config: MariboxConfig
    config_root: Path
    auth_manager: AuthManager


def resolve_tool_context(config_root: Path | None = None) -> ToolContext:
    """Resolve and construct all dependencies needed by tool functions."""
    root = config_root or resolve_config_root()
    config = load_config(root)
    auth = AuthManager(root)
    return ToolContext(config=config, config_root=root, auth_manager=auth)


def format_result(data: Any) -> str:
    """Format a tool result as a human-readable string (plain text, no Rich codes)."""
    buf = StringIO()
    console = Console(file=buf, force_terminal=False, no_color=True)
    if isinstance(data, str):
        return _truncate(data)
    if isinstance(data, list):
        for item in data:
            console.print(str(item))
    elif isinstance(data, dict):
        for k, v in data.items():
            console.print(f"{k}: {v}")
    else:
        console.print(str(data))
    return _truncate(buf.getvalue())


def _truncate(text: str, max_length: int = MAX_RESPONSE_LENGTH) -> str:
    """Truncate text to max_length with an indicator."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "\n... [truncated]"
