"""Default config values for maribox."""

from __future__ import annotations

DEFAULT_CONFIG: dict[str, dict[str, object]] = {
    "maribox": {
        "version": "1",
        "default_provider": "anthropic",
        "default_model": "claude-sonnet-4-6",
        "auto_open_browser": False,
        "log_level": "info",
    },
    "sandbox": {
        "base_url": "",
        "timeout_seconds": 300,
    },
    "marimo": {
        "port_range": [7000, 7100],
        "headless": True,
    },
    "tui": {
        "theme": "dark",
        "refresh_rate_ms": 250,
        "show_agent_thoughts": True,
    },
}

DEFAULT_PROFILES: dict[str, dict[str, str]] = {
    "orchestrator": {"model": "claude-sonnet-4-6", "provider": "anthropic"},
    "notebook": {"model": "claude-sonnet-4-6", "provider": "anthropic"},
    "ui": {"model": "gemini-2.5-pro", "provider": "google"},
    "debug": {"model": "gpt-4o", "provider": "openai"},
    "session": {"model": "claude-sonnet-4-6", "provider": "anthropic"},
}
