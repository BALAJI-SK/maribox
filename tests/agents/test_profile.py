"""Tests for agent profile loading and model resolution."""

from pathlib import Path

from maribox.agents.profile import get_default_profile, get_profile_for_role, load_profiles, resolve_model
from maribox.config.schema import AgentProfile


class TestLoadProfiles:
    def test_loads_defaults(self, tmp_path: Path) -> None:
        profiles = load_profiles(tmp_path)
        assert "orchestrator" in profiles
        assert "notebook" in profiles
        assert "ui" in profiles
        assert "debug" in profiles
        assert "session" in profiles

    def test_default_profiles_have_provider_and_model(self, tmp_path: Path) -> None:
        profiles = load_profiles(tmp_path)
        for name, profile in profiles.items():
            assert profile.provider, f"{name} missing provider"
            assert profile.model, f"{name} missing model"

    def test_merges_user_overrides(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "profiles.toml").write_text(
            '[notebook]\nmodel = "gpt-4o"\nprovider = "openai"\n',
            encoding="utf-8",
        )
        profiles = load_profiles(tmp_path)
        assert profiles["notebook"].model == "gpt-4o"
        assert profiles["notebook"].provider == "openai"
        # Other profiles still have defaults
        assert profiles["orchestrator"].provider == "anthropic"

    def test_adds_new_profile(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "profiles.toml").write_text(
            '[custom_agent]\nmodel = "glm-4-plus"\nprovider = "glm"\n',
            encoding="utf-8",
        )
        profiles = load_profiles(tmp_path)
        assert "custom_agent" in profiles
        assert profiles["custom_agent"].model == "glm-4-plus"


class TestResolveModel:
    def test_anthropic(self) -> None:
        assert resolve_model("anthropic", "claude-sonnet-4-6") == "anthropic/claude-sonnet-4-6"

    def test_google(self) -> None:
        assert resolve_model("google", "gemini-2.5-pro") == "gemini/gemini-2.5-pro"

    def test_openai(self) -> None:
        assert resolve_model("openai", "gpt-4o") == "openai/gpt-4o"

    def test_glm(self) -> None:
        assert resolve_model("glm", "glm-4-plus") == "openai/glm-4-plus"

    def test_custom(self) -> None:
        assert resolve_model("custom", "my-model") == "openai/my-model"

    def test_unknown_provider(self) -> None:
        assert resolve_model("mistral", "mistral-large") == "mistral/mistral-large"


class TestGetDefaultProfile:
    def test_returns_orchestrator(self) -> None:
        assert get_default_profile() == "orchestrator"


class TestGetProfileForRole:
    def test_returns_matching_profile(self, tmp_path: Path) -> None:
        profiles = load_profiles(tmp_path)
        profile = get_profile_for_role("debug", profiles)
        assert profile.model == "gpt-4o"

    def test_falls_back_to_orchestrator(self, tmp_path: Path) -> None:
        profiles = load_profiles(tmp_path)
        profile = get_profile_for_role("nonexistent", profiles)
        assert profile.provider == "anthropic"

    def test_loads_profiles_when_none(self) -> None:
        # Smoke test — just ensure it doesn't crash
        profile = get_profile_for_role("notebook")
        assert isinstance(profile, AgentProfile)
