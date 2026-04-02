"""Config file I/O — load, save, and merge TOML configuration."""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from maribox.config.defaults import DEFAULT_CONFIG, DEFAULT_PROFILES
from maribox.config.resolution import resolve_config_root
from maribox.config.schema import AgentOverride, AgentProfile, MariboxConfig, ProjectConfig
from maribox.exceptions import ConfigError


def load_config(root: Path) -> MariboxConfig:
    """Load config.toml from the config root, merged with defaults."""
    config_path = root / "config.toml"
    data: dict[str, dict[str, object]] = dict(DEFAULT_CONFIG)

    if config_path.is_file():
        try:
            with open(config_path, "rb") as f:
                user_data = tomllib.load(f)
            # Deep merge user data over defaults
            for section, values in user_data.items():
                if isinstance(values, dict) and section in data:
                    data[section].update(values)
                else:
                    data[section] = values
        except (tomllib.TOMLDecodeError, OSError) as e:
            raise ConfigError(f"Failed to load config from {config_path}: {e}") from e

    return MariboxConfig.from_toml(data)


def load_project_config(root: Path) -> ProjectConfig | None:
    """Load project.toml from the config root, if it exists."""
    project_path = root / "project.toml"
    if not project_path.is_file():
        return None
    try:
        with open(project_path, "rb") as f:
            data = tomllib.load(f)
        return ProjectConfig.from_toml(data)
    except (tomllib.TOMLDecodeError, OSError) as e:
        raise ConfigError(f"Failed to load project config from {project_path}: {e}") from e


def load_agent_profiles(root: Path) -> dict[str, AgentProfile]:
    """Load agents/profiles.toml from the config root."""
    profiles_path = root / "agents" / "profiles.toml"
    if not profiles_path.is_file():
        # Return defaults
        return {k: AgentProfile.from_toml(v) for k, v in DEFAULT_PROFILES.items()}

    try:
        with open(profiles_path, "rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        raise ConfigError(f"Failed to load agent profiles from {profiles_path}: {e}") from e

    return {k: AgentProfile.from_toml(v) for k, v in data.items() if isinstance(v, dict)}


def save_config(root: Path, config: MariboxConfig) -> None:
    """Write config.toml to the config root."""
    config_path = root / "config.toml"
    root.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_path, "wb") as f:
            tomli_w.dump(config.to_toml(), f)
    except OSError as e:
        raise ConfigError(f"Failed to save config to {config_path}: {e}") from e


def save_project_config(root: Path, config: ProjectConfig) -> None:
    """Write project.toml to the config root."""
    project_path = root / "project.toml"
    root.mkdir(parents=True, exist_ok=True)
    try:
        with open(project_path, "wb") as f:
            tomli_w.dump(config.to_toml(), f)
    except OSError as e:
        raise ConfigError(f"Failed to save project config to {project_path}: {e}") from e


def save_agent_profiles(root: Path, profiles: dict[str, AgentProfile]) -> None:
    """Write agents/profiles.toml to the config root."""
    agents_dir = root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    profiles_path = agents_dir / "profiles.toml"
    data = {k: v.to_toml() for k, v in profiles.items()}
    try:
        with open(profiles_path, "wb") as f:
            tomli_w.dump(data, f)
    except OSError as e:
        raise ConfigError(f"Failed to save agent profiles to {profiles_path}: {e}") from e


def resolve_merged_config() -> tuple[MariboxConfig, ProjectConfig | None]:
    """Load and merge global config with project-level overrides.

    Returns the merged MariboxConfig and the ProjectConfig (if any).
    """
    root = resolve_config_root()
    config = load_config(root)
    project = load_project_config(root)

    if project is not None:
        # Apply project-level provider/model overrides
        if project.provider is not None:
            config.maribox.default_provider = project.provider
        if project.model is not None:
            config.maribox.default_model = project.model

    return config, project


def init_config_dir(root: Path, scope: str = "project") -> Path:
    """Create a .maribox/ directory with defaults.

    Args:
        root: The parent directory where .maribox/ will be created (for project scope)
              or the config root itself (for global scope).
        scope: "project" to create at root/.maribox/, "global" to create at root.

    Returns:
        The created config root path.
    """
    config_root = root / ".maribox" if scope == "project" else root

    config_root.mkdir(parents=True, exist_ok=True)
    (config_root / "sessions").mkdir(exist_ok=True)
    (config_root / "agents").mkdir(exist_ok=True)

    # Write default config.toml if it doesn't exist
    config_path = config_root / "config.toml"
    if not config_path.is_file():
        save_config(config_root, MariboxConfig())

    # Write default profiles.toml if it doesn't exist
    profiles_path = config_root / "agents" / "profiles.toml"
    if not profiles_path.is_file():
        profiles = {k: AgentProfile.from_toml(v) for k, v in DEFAULT_PROFILES.items()}
        save_agent_profiles(config_root, profiles)

    # Write .gitignore in the .maribox dir
    gitignore_path = config_root / ".gitignore"
    if not gitignore_path.is_file():
        gitignore_path.write_text("keys.enc\nsessions/\n")

    return config_root


def set_config_value(key: str, value: str, root: Path | None = None, project: bool = False) -> None:
    """Update a single config key using dot-path notation.

    Args:
        key: Dot-path key (e.g. "maribox.default_provider").
        value: String value to set (parsed to appropriate type).
        root: Config root. If None, resolves automatically.
        project: If True, write to project.toml instead of config.toml.
    """
    if root is None:
        root = resolve_config_root()

    if project:
        config = load_project_config(root)
        if config is None:
            config = ProjectConfig()
        # Support limited dot-paths for project config
        parts = key.split(".")
        if parts[0] == "project" and len(parts) == 2:
            parsed_value = _parse_value(value)
            if parts[1] == "name":
                config.name = str(parsed_value)
            elif parts[1] == "provider":
                config.provider = str(parsed_value)
            elif parts[1] == "model":
                config.model = str(parsed_value)
        elif parts[0] == "agents" and len(parts) == 3:
            agent_name, field_name = parts[1], parts[2]
            if agent_name not in config.agents:
                config.agents[agent_name] = AgentOverride()
            parsed_value = _parse_value(value)
            if field_name == "model":
                config.agents[agent_name].model = str(parsed_value)
            elif field_name == "provider":
                config.agents[agent_name].provider = str(parsed_value)
        save_project_config(root, config)
    else:
        maribox_config = load_config(root)
        _set_nested(maribox_config, key, value)
        save_config(root, maribox_config)


def _set_nested(config: MariboxConfig, key: str, value: str) -> None:
    """Set a value on a MariboxConfig using dot-path notation."""
    parsed = _parse_value(value)
    parts = key.split(".", 1)
    if len(parts) != 2:
        raise ConfigError(f"Invalid config key format: {key}. Expected 'section.field'.")

    section_name, field_name = parts
    section_map: dict[str, object] = {
        "maribox": config.maribox,
        "sandbox": config.sandbox,
        "marimo": config.marimo,
        "tui": config.tui,
    }

    section = section_map.get(section_name)
    if section is None:
        raise ConfigError(f"Unknown config section: {section_name}")

    if not hasattr(section, field_name):
        raise ConfigError(f"Unknown config field: {section_name}.{field_name}")

    setattr(section, field_name, parsed)


def _parse_value(value: str) -> object:
    """Parse a string value into the appropriate Python type."""
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
