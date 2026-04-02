"""Tests for config schema."""

from __future__ import annotations

from maribox.config.schema import (
    AgentProfile,
    MariboxConfig,
    MariboxSection,
    MarimoSection,
    ProjectConfig,
)


class TestMariboxSection:
    def test_defaults(self) -> None:
        s = MariboxSection()
        assert s.version == "1"
        assert s.default_provider == "anthropic"
        assert s.log_level == "info"

    def test_from_toml(self) -> None:
        s = MariboxSection.from_toml({"default_provider": "google", "log_level": "debug"})
        assert s.default_provider == "google"
        assert s.log_level == "debug"

    def test_roundtrip(self) -> None:
        original = MariboxSection(default_provider="openai", log_level="warn")
        data = original.to_toml()
        restored = MariboxSection.from_toml(data)
        assert restored == original


class TestMarimoSection:
    def test_port_range_from_list(self) -> None:
        s = MarimoSection.from_toml({"port_range": [8000, 9000]})
        assert s.port_range == (8000, 9000)


class TestMariboxConfig:
    def test_defaults(self) -> None:
        config = MariboxConfig()
        assert config.maribox.default_provider == "anthropic"
        assert config.sandbox.timeout_seconds == 300

    def test_from_toml_partial(self) -> None:
        config = MariboxConfig.from_toml({"maribox": {"log_level": "debug"}})
        assert config.maribox.log_level == "debug"
        assert config.sandbox.timeout_seconds == 300  # default

    def test_roundtrip(self) -> None:
        config = MariboxConfig()
        data = config.to_toml()
        restored = MariboxConfig.from_toml(data)
        assert restored.maribox == config.maribox
        assert restored.sandbox == config.sandbox


class TestProjectConfig:
    def test_from_toml(self) -> None:
        data = {
            "project": {"name": "test", "provider": "google", "model": "gemini-pro"},
            "agents": {"notebook": {"model": "claude-sonnet-4-6"}},
        }
        project = ProjectConfig.from_toml(data)
        assert project.name == "test"
        assert project.provider == "google"
        assert "notebook" in project.agents
        assert project.agents["notebook"].model == "claude-sonnet-4-6"


class TestAgentProfile:
    def test_from_toml(self) -> None:
        p = AgentProfile.from_toml({"model": "gpt-4o", "provider": "openai"})
        assert p.model == "gpt-4o"
        assert p.provider == "openai"
