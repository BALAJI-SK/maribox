"""Tests for auth manager."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from maribox.auth.manager import PROVIDER_NAMES, AuthManager


class TestAuthManager:
    def test_set_key_stores_in_both(self, tmp_maribox_home: Path) -> None:
        manager = AuthManager(config_root=tmp_maribox_home)
        with patch.object(manager, "_keyring", MagicMock()) as mock_keyring, \
             patch.object(manager, "_keystore", MagicMock()) as mock_keystore:
            manager.set_key("anthropic", "test-api-key")
            mock_keyring.store_key.assert_called_once_with("anthropic", "test-api-key")
            mock_keystore.store_key.assert_called_once_with("anthropic", "test-api-key")

    def test_get_key_keyring_first(self, tmp_maribox_home: Path) -> None:
        manager = AuthManager(config_root=tmp_maribox_home)
        with patch.object(manager, "_keyring", MagicMock()) as mock_keyring:
            mock_keyring.retrieve_key.return_value = "from-keyring"
            result = manager.get_key("anthropic")
            assert result == "from-keyring"

    def test_get_key_falls_back_to_keystore(self, tmp_maribox_home: Path) -> None:
        manager = AuthManager(config_root=tmp_maribox_home)
        with patch.object(manager, "_keyring", MagicMock()) as mock_keyring, \
             patch.object(manager, "_keystore", MagicMock()) as mock_keystore:
            mock_keyring.retrieve_key.return_value = None
            mock_keystore.retrieve_key.return_value = "from-keystore"
            result = manager.get_key("anthropic")
            assert result == "from-keystore"

    def test_list_keys(self, tmp_maribox_home: Path) -> None:
        manager = AuthManager(config_root=tmp_maribox_home)
        with patch.object(manager, "_keyring", MagicMock()) as mock_keyring, \
             patch.object(manager, "_keystore", MagicMock()) as mock_keystore:
            mock_keyring.retrieve_key.side_effect = (
                lambda p: "sk-ant-long-key-here" if p == "anthropic" else None
            )
            mock_keystore.retrieve_key.return_value = None
            result = manager.list_keys()
            anthropic = next(r for r in result if r.provider == "anthropic")
            assert anthropic.has_key is True
            assert "sk-ant-l" in anthropic.masked_key

    def test_revoke_key(self, tmp_maribox_home: Path) -> None:
        manager = AuthManager(config_root=tmp_maribox_home)
        with patch.object(manager, "_keyring", MagicMock()) as mock_keyring, \
             patch.object(manager, "_keystore", MagicMock()) as mock_keystore:
            manager.revoke_key("anthropic")
            mock_keyring.remove_key.assert_called_once_with("anthropic")
            mock_keystore.remove_key.assert_called_once_with("anthropic")

    def test_set_key_unknown_provider(self, tmp_maribox_home: Path) -> None:
        manager = AuthManager(config_root=tmp_maribox_home)
        with pytest.raises(ValueError, match="Unknown provider"):
            manager.set_key("unknown_provider", "key")

    def test_provider_names(self) -> None:
        assert "anthropic" in PROVIDER_NAMES
        assert "google" in PROVIDER_NAMES
        assert "openai" in PROVIDER_NAMES
