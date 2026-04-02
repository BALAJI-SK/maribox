"""Shared test fixtures for maribox."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_maribox_home(tmp_path: Path) -> Path:
    """Create a temporary .maribox directory structure for testing."""
    home = tmp_path / ".maribox"
    home.mkdir()
    (home / "sessions").mkdir()
    (home / "agents").mkdir()
    return home


@pytest.fixture
def mock_config(tmp_maribox_home: Path) -> dict[str, object]:
    """Provide a default config dict for testing."""
    return {
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
