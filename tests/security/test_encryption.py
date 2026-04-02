"""Tests for encryption module."""

from __future__ import annotations

from pathlib import Path

import pytest

from maribox.exceptions import EncryptionError
from maribox.security.encryption import (
    KeyStore,
    decrypt_key,
    derive_key,
    encrypt_key,
    get_machine_id,
    zero_memory,
)


class TestDeriveKey:
    def test_produces_32_bytes(self) -> None:
        key = derive_key("test-machine-id", b"salt1234")
        assert len(key) == 32

    def test_deterministic(self) -> None:
        key1 = derive_key("test-machine-id", b"salt1234")
        key2 = derive_key("test-machine-id", b"salt1234")
        assert key1 == key2

    def test_different_salts_different_keys(self) -> None:
        key1 = derive_key("test-machine-id", b"salt1234")
        key2 = derive_key("test-machine-id", b"different")
        assert key1 != key2

    def test_rejects_short_salt(self) -> None:
        with pytest.raises(EncryptionError, match="at least 8 bytes"):
            derive_key("test", b"short")


class TestEncryptDecrypt:
    def test_roundtrip(self) -> None:
        derived = derive_key("test-machine-id", b"salt1234")
        ciphertext, nonce = encrypt_key("sk-ant-test-key-12345", derived)
        result = decrypt_key(ciphertext, nonce, derived)
        assert result == "sk-ant-test-key-12345"

    def test_different_keys_fail(self) -> None:
        derived1 = derive_key("machine-a", b"salt1234")
        derived2 = derive_key("machine-b", b"salt1234")
        ciphertext, nonce = encrypt_key("secret-key", derived1)
        with pytest.raises(EncryptionError, match="Decryption failed"):
            decrypt_key(ciphertext, nonce, derived2)


class TestZeroMemory:
    def test_zeros_bytearray(self) -> None:
        buf = bytearray(b"sensitive-data-here")
        zero_memory(buf)
        assert buf == bytearray(len(buf))

    def test_empty_buffer(self) -> None:
        buf = bytearray()
        zero_memory(buf)  # Should not raise


class TestGetMachineId:
    def test_returns_nonempty_string(self) -> None:
        mid = get_machine_id()
        assert isinstance(mid, str)
        assert len(mid) > 0


class TestKeyStore:
    def test_store_and_retrieve(self, tmp_path: Path) -> None:
        store = KeyStore(tmp_path)
        store.store_key("anthropic", "sk-ant-test-key")
        result = store.retrieve_key("anthropic")
        assert result == "sk-ant-test-key"

    def test_list_providers(self, tmp_path: Path) -> None:
        store = KeyStore(tmp_path)
        store.store_key("anthropic", "key1")
        store.store_key("openai", "key2")
        providers = store.list_providers()
        assert set(providers) == {"anthropic", "openai"}

    def test_remove_key(self, tmp_path: Path) -> None:
        store = KeyStore(tmp_path)
        store.store_key("anthropic", "key1")
        store.remove_key("anthropic")
        assert store.retrieve_key("anthropic") is None

    def test_retrieve_missing_returns_none(self, tmp_path: Path) -> None:
        store = KeyStore(tmp_path)
        assert store.retrieve_key("nonexistent") is None

    def test_empty_store(self, tmp_path: Path) -> None:
        store = KeyStore(tmp_path)
        assert store.list_providers() == []
