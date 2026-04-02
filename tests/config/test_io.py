"""Tests for config I/O."""

from __future__ import annotations

from pathlib import Path

import pytest

from maribox.config.io import (
    init_config_dir,
    load_agent_profiles,
    load_config,
    load_project_config,
    save_agent_profiles,
    save_config,
    save_project_config,
    set_config_value,
)
from maribox.config.schema import AgentProfile, MariboxConfig, ProjectConfig
from maribox.exceptions import ConfigError


class TestLoadConfig:
    def test_loads_defaults_when_no_file(self, tmp_maribox_home: Path) -> None:
        config = load_config(tmp_maribox_home)
        assert config.maribox.default_provider == "anthropic"
        assert config.sandbox.timeout_seconds == 300

    def test_loads_user_overrides(self, tmp_maribox_home: Path) -> None:
        # Write a config with overrides
        config = MariboxConfig()
        config.maribox.default_provider = "google"
        config.maribox.log_level = "debug"
        save_config(tmp_maribox_home, config)

        loaded = load_config(tmp_maribox_home)
        assert loaded.maribox.default_provider == "google"
        assert loaded.maribox.log_level == "debug"
        # Other sections should have defaults
        assert loaded.sandbox.timeout_seconds == 300


class TestSaveConfig:
    def test_creates_directory(self, tmp_path: Path) -> None:
        root = tmp_path / "new_dir"
        config = MariboxConfig()
        save_config(root, config)
        assert (root / "config.toml").is_file()

    def test_roundtrip(self, tmp_maribox_home: Path) -> None:
        original = MariboxConfig()
        original.maribox.default_provider = "openai"
        save_config(tmp_maribox_home, original)
        loaded = load_config(tmp_maribox_home)
        assert loaded.maribox.default_provider == "openai"


class TestProjectConfig:
    def test_returns_none_when_missing(self, tmp_maribox_home: Path) -> None:
        assert load_project_config(tmp_maribox_home) is None

    def test_save_and_load(self, tmp_maribox_home: Path) -> None:
        project = ProjectConfig(name="test-project", provider="google")
        save_project_config(tmp_maribox_home, project)
        loaded = load_project_config(tmp_maribox_home)
        assert loaded is not None
        assert loaded.name == "test-project"
        assert loaded.provider == "google"


class TestAgentProfiles:
    def test_loads_defaults_when_missing(self, tmp_maribox_home: Path) -> None:
        profiles = load_agent_profiles(tmp_maribox_home)
        assert "orchestrator" in profiles
        assert profiles["orchestrator"].provider == "anthropic"

    def test_save_and_load(self, tmp_maribox_home: Path) -> None:
        profiles = {"my_agent": AgentProfile(model="gpt-4o", provider="openai")}
        save_agent_profiles(tmp_maribox_home, profiles)
        loaded = load_agent_profiles(tmp_maribox_home)
        assert "my_agent" in loaded
        assert loaded["my_agent"].model == "gpt-4o"


class TestInitConfigDir:
    def test_creates_project_scope(self, tmp_path: Path) -> None:
        config_root = init_config_dir(tmp_path, scope="project")
        assert config_root == tmp_path / ".maribox"
        assert (config_root / "config.toml").is_file()
        assert (config_root / "sessions").is_dir()
        assert (config_root / "agents").is_dir()
        assert (config_root / "agents" / "profiles.toml").is_file()
        assert (config_root / ".gitignore").is_file()

    def test_creates_global_scope(self, tmp_path: Path) -> None:
        config_root = init_config_dir(tmp_path, scope="global")
        assert config_root == tmp_path
        assert (config_root / "config.toml").is_file()

    def test_idempotent(self, tmp_path: Path) -> None:
        init_config_dir(tmp_path, scope="project")
        init_config_dir(tmp_path, scope="project")  # Should not raise
        assert (tmp_path / ".maribox" / "config.toml").is_file()


class TestSetConfigValue:
    def test_set_maribox_field(self, tmp_maribox_home: Path) -> None:
        save_config(tmp_maribox_home, MariboxConfig())
        set_config_value("maribox.log_level", "debug", root=tmp_maribox_home)
        loaded = load_config(tmp_maribox_home)
        assert loaded.maribox.log_level == "debug"

    def test_set_sandbox_field(self, tmp_maribox_home: Path) -> None:
        save_config(tmp_maribox_home, MariboxConfig())
        set_config_value("sandbox.timeout_seconds", "600", root=tmp_maribox_home)
        loaded = load_config(tmp_maribox_home)
        assert loaded.sandbox.timeout_seconds == 600

    def test_set_invalid_section(self, tmp_maribox_home: Path) -> None:
        save_config(tmp_maribox_home, MariboxConfig())
        with pytest.raises(ConfigError, match="Unknown config section"):
            set_config_value("invalid.field", "value", root=tmp_maribox_home)
