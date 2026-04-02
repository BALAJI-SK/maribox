"""Agent profile loader — reads agent model/provider config from TOML."""

from __future__ import annotations

import tomllib
from pathlib import Path

from maribox.config.defaults import DEFAULT_PROFILES
from maribox.config.resolution import resolve_config_root
from maribox.config.schema import AgentProfile

# Provider prefix mapping for LiteLLM model strings
_PROVIDER_PREFIX: dict[str, str] = {
    "anthropic": "anthropic",
    "google": "gemini",
    "openai": "openai",
    "glm": "openai",  # zhipuai uses OpenAI-compatible API via litellm
    "custom": "openai",
}


def load_profiles(config_root: Path | None = None) -> dict[str, AgentProfile]:
    """Load agent profiles from agents/profiles.toml.

    Merges defaults with user overrides from the config root.
    """
    root = config_root or resolve_config_root()
    profiles_path = root / "agents" / "profiles.toml"

    # Start with defaults
    data: dict[str, dict[str, str]] = dict(DEFAULT_PROFILES)

    # Merge user overrides
    if profiles_path.is_file():
        with open(profiles_path, "rb") as f:
            user_profiles = tomllib.load(f)
        for name, profile_data in user_profiles.items():
            if isinstance(profile_data, dict):
                data[name] = {**data.get(name, {}), **profile_data}

    return {name: AgentProfile.from_toml(profile) for name, profile in data.items()}


def get_default_profile() -> str:
    """Return the name of the default agent profile (orchestrator)."""
    return "orchestrator"


def resolve_model(provider: str, model: str) -> str:
    """Convert a provider+model pair to a LiteLLM-compatible model string.

    Examples:
        ("anthropic", "claude-sonnet-4-6") -> "anthropic/claude-sonnet-4-6"
        ("google", "gemini-2.5-pro") -> "gemini/gemini-2.5-pro"
        ("openai", "gpt-4o") -> "openai/gpt-4o"
        ("glm", "glm-4-plus") -> "openai/glm-4-plus"
    """
    prefix = _PROVIDER_PREFIX.get(provider, provider)
    return f"{prefix}/{model}"


def get_profile_for_role(role: str, profiles: dict[str, AgentProfile] | None = None) -> AgentProfile:
    """Get the agent profile for a given role (e.g. 'notebook', 'debug').

    Falls back to the orchestrator profile if the role isn't found.
    """
    if profiles is None:
        profiles = load_profiles()
    default = AgentProfile(model="claude-sonnet-4-6", provider="anthropic")
    return profiles.get(role, profiles.get("orchestrator", default))
