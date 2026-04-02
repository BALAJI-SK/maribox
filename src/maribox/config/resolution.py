"""Config root resolution — finds the active .maribox directory."""

from __future__ import annotations

import os
from pathlib import Path

import platformdirs

from maribox.exceptions import ConfigError


def resolve_config_root() -> Path:
    """Resolve the maribox config root using 3-tier priority.

    1. MARIBOX_HOME environment variable (if set and non-empty)
    2. <project-root>/.maribox/ — walk up from cwd looking for .maribox/
    3. OS user config path via platformdirs (~/.config/maribox/ or %APPDATA%/maribox)
    """
    # Tier 1: environment variable
    env_home = os.environ.get("MARIBOX_HOME", "").strip()
    if env_home:
        path = Path(env_home)
        if not path.is_absolute():
            raise ConfigError(f"MARIBOX_HOME must be an absolute path, got: {env_home}")
        return path

    # Tier 2: walk up from cwd looking for .maribox/
    current = Path.cwd()
    while True:
        candidate = current / ".maribox"
        if candidate.is_dir():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent

    # Tier 3: OS user config path
    return Path(platformdirs.user_config_dir("maribox"))


def get_sessions_dir(root: Path) -> Path:
    """Return the sessions directory path."""
    return root / "sessions"


def get_agents_dir(root: Path) -> Path:
    """Return the agents directory path."""
    return root / "agents"
