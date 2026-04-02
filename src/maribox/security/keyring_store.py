"""OS keychain integration via python-keyring."""

from __future__ import annotations

import contextlib

import keyring

_SERVICE_NAME = "maribox"


class KeyringStore:
    """Wraps the keyring library for maribox API key storage."""

    def store_key(self, provider: str, api_key: str) -> None:
        """Store an API key in the OS keychain."""
        keyring.set_password(_SERVICE_NAME, provider, api_key)

    def retrieve_key(self, provider: str) -> str | None:
        """Retrieve an API key from the OS keychain."""
        return keyring.get_password(_SERVICE_NAME, provider)

    def remove_key(self, provider: str) -> None:
        """Remove an API key from the OS keychain."""
        with contextlib.suppress(keyring.errors.PasswordDeleteError):
            keyring.delete_password(_SERVICE_NAME, provider)

    def list_providers(self) -> list[str]:
        """Check known provider names for existing keys."""
        known = ["anthropic", "google", "openai", "glm", "custom"]
        return [p for p in known if keyring.get_password(_SERVICE_NAME, p) is not None]
