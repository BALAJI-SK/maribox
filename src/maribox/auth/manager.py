"""High-level auth orchestration — manages API keys across keyring and keys.enc."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maribox.config.resolution import resolve_config_root
from maribox.security.encryption import KeyStore
from maribox.security.keyring_store import KeyringStore

PROVIDER_NAMES = ["anthropic", "google", "openai", "glm", "custom"]


@dataclass
class ProviderInfo:
    """Information about a configured provider."""

    provider: str
    masked_key: str
    has_key: bool
    model: str | None = None


class AuthManager:
    """Manages API keys for AI providers.

    Keys are stored in both the OS keychain (primary) and keys.enc (backup).
    """

    def __init__(self, config_root: Path | None = None) -> None:
        self._root = config_root or resolve_config_root()
        self._keyring = KeyringStore()
        self._keystore = KeyStore(self._root)

    def set_key(self, provider: str, api_key: str) -> None:
        """Store an API key for a provider in both keyring and keys.enc."""
        if provider not in PROVIDER_NAMES:
            raise ValueError(f"Unknown provider: {provider}. Must be one of {PROVIDER_NAMES}")
        self._keyring.store_key(provider, api_key)
        self._keystore.store_key(provider, api_key)

    def get_key(self, provider: str) -> str | None:
        """Retrieve an API key. Tries keyring first, falls back to keys.enc."""
        key = self._keyring.retrieve_key(provider)
        if key is not None:
            return key
        return self._keystore.retrieve_key(provider)

    def list_keys(self) -> list[ProviderInfo]:
        """List all providers with masked key status."""
        results: list[ProviderInfo] = []
        for provider in PROVIDER_NAMES:
            key = self.get_key(provider)
            if key:
                masked = key[:8] + "***REDACTED***" if len(key) > 12 else "***REDACTED***"
                results.append(ProviderInfo(provider=provider, masked_key=masked, has_key=True))
            else:
                results.append(ProviderInfo(provider=provider, masked_key="", has_key=False))
        return results

    def rotate_key(self, provider: str, new_api_key: str) -> None:
        """Replace the API key for a provider."""
        # Store new key (overwrites old)
        self.set_key(provider, new_api_key)

    def revoke_key(self, provider: str) -> None:
        """Remove the API key for a provider from both stores."""
        self._keyring.remove_key(provider)
        self._keystore.remove_key(provider)

    def set_active_provider(self, provider: str, model: str | None = None, project: bool = False) -> None:
        """Update config to set the active provider.

        Args:
            provider: Provider name to activate.
            model: Optional model to set alongside the provider.
            project: If True, write to project.toml instead of config.toml.
        """
        from maribox.config.io import set_config_value

        root = self._root
        set_config_value("maribox.default_provider", provider, root=root, project=project)
        if model:
            set_config_value("maribox.default_model", model, root=root, project=project)
