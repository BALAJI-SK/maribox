"""AES-256-GCM encryption with Argon2id key derivation."""

from __future__ import annotations

import ctypes
import os
import struct
import sys
from pathlib import Path

from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from maribox.exceptions import EncryptionError


def get_machine_id() -> str:
    """Get a unique machine identifier for key derivation."""
    if sys.platform == "linux":
        try:
            return Path("/etc/machine-id").read_text().strip()
        except OSError:
            pass
    elif sys.platform == "darwin":
        try:
            import subprocess
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True, check=True,
            )
            for line in result.stdout.splitlines():
                if "IOPlatformUUID" in line:
                    return line.split('"')[-2]
        except (OSError, subprocess.CalledProcessError):
            pass
    elif sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "MachineGuid")
                return str(value)
        except OSError:
            pass

    # Fallback: use hostname + username
    return f"{os.uname().nodename}:{os.getenv('USERNAME', os.getenv('USER', 'unknown'))}"


def derive_key(machine_id: str, salt: bytes) -> bytes:
    """Derive a 32-byte encryption key using Argon2id."""
    if len(salt) < 8:
        raise EncryptionError("Salt must be at least 8 bytes")

    try:
        return hash_secret_raw(
            secret=machine_id.encode("utf-8"),
            salt=salt,
            time_cost=3,
            memory_cost=65536,  # 64 MB
            parallelism=1,
            hash_len=32,
            type=Type.ID,
        )
    except Exception as e:
        raise EncryptionError(f"Argon2id key derivation failed: {e}") from e


def encrypt_key(api_key: str, derived_key: bytes) -> tuple[bytes, bytes]:
    """Encrypt an API key using AES-256-GCM.

    Returns:
        Tuple of (ciphertext_with_tag, nonce).
    """
    try:
        aesgcm = AESGCM(derived_key)
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = aesgcm.encrypt(nonce, api_key.encode("utf-8"), None)
        return ciphertext, nonce
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}") from e


def decrypt_key(ciphertext: bytes, nonce: bytes, derived_key: bytes) -> str:
    """Decrypt an API key using AES-256-GCM."""
    try:
        aesgcm = AESGCM(derived_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")
    except Exception as e:
        raise EncryptionError(f"Decryption failed: {e}") from e


def zero_memory(buffer: bytearray) -> None:
    """Securely zero a bytearray using ctypes.memset."""
    if buffer:
        ctypes.memset(
            ctypes.addressof((ctypes.c_char * len(buffer)).from_buffer(buffer)),
            0,
            len(buffer),
        )


class KeyStore:
    """Manages encrypted key storage in keys.enc file.

    File format (binary):
        - 4 bytes: salt length (uint32 LE)
        - N bytes: salt
        - 4 bytes: number of entries (uint32 LE)
        - For each entry:
            - 4 bytes: provider name length (uint32 LE)
            - N bytes: provider name (UTF-8)
            - 4 bytes: nonce length (uint32 LE)
            - N bytes: nonce
            - 4 bytes: ciphertext length (uint32 LE)
            - N bytes: ciphertext
    """

    def __init__(self, config_root: Path) -> None:
        self._path = config_root / "keys.enc"

    def _load_store(self) -> tuple[bytes, dict[str, tuple[bytes, bytes]]]:
        """Load the encrypted key store from disk."""
        if not self._path.is_file():
            return b"", {}

        try:
            data = self._path.read_bytes()
            offset = 0

            salt_len = struct.unpack_from("<I", data, offset)[0]
            offset += 4
            salt = data[offset : offset + salt_len]
            offset += salt_len

            num_entries = struct.unpack_from("<I", data, offset)[0]
            offset += 4

            entries: dict[str, tuple[bytes, bytes]] = {}
            for _ in range(num_entries):
                name_len = struct.unpack_from("<I", data, offset)[0]
                offset += 4
                name = data[offset : offset + name_len].decode("utf-8")
                offset += name_len

                nonce_len = struct.unpack_from("<I", data, offset)[0]
                offset += 4
                nonce = data[offset : offset + nonce_len]
                offset += nonce_len

                ct_len = struct.unpack_from("<I", data, offset)[0]
                offset += 4
                ciphertext = data[offset : offset + ct_len]
                offset += ct_len

                entries[name] = (nonce, ciphertext)

            return salt, entries
        except Exception as e:
            raise EncryptionError(f"Failed to load key store: {e}") from e

    def _save_store(self, salt: bytes, entries: dict[str, tuple[bytes, bytes]]) -> None:
        """Save the encrypted key store to disk atomically."""
        parts: list[bytes] = []
        parts.append(struct.pack("<I", len(salt)))
        parts.append(salt)
        parts.append(struct.pack("<I", len(entries)))

        for name, (nonce, ciphertext) in entries.items():
            name_bytes = name.encode("utf-8")
            parts.append(struct.pack("<I", len(name_bytes)))
            parts.append(name_bytes)
            parts.append(struct.pack("<I", len(nonce)))
            parts.append(nonce)
            parts.append(struct.pack("<I", len(ciphertext)))
            parts.append(ciphertext)

        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._path.with_suffix(".tmp")
            tmp_path.write_bytes(b"".join(parts))
            tmp_path.replace(self._path)
        except OSError as e:
            raise EncryptionError(f"Failed to save key store: {e}") from e

    def store_key(self, provider: str, api_key: str) -> None:
        """Encrypt and store an API key for a provider."""
        salt, entries = self._load_store()
        if not salt:
            salt = os.urandom(32)

        derived = derive_key(get_machine_id(), salt)
        ciphertext, nonce = encrypt_key(api_key, derived)
        zero_memory(bytearray(derived))

        entries[provider] = (nonce, ciphertext)
        self._save_store(salt, entries)

    def retrieve_key(self, provider: str) -> str | None:
        """Decrypt and return the API key for a provider."""
        salt, entries = self._load_store()
        if provider not in entries:
            return None

        derived = derive_key(get_machine_id(), salt)
        nonce, ciphertext = entries[provider]
        try:
            return decrypt_key(ciphertext, nonce, derived)
        finally:
            zero_memory(bytearray(derived))

    def remove_key(self, provider: str) -> None:
        """Remove a provider's encrypted key entry."""
        salt, entries = self._load_store()
        if provider in entries:
            del entries[provider]
            self._save_store(salt, entries)

    def list_providers(self) -> list[str]:
        """Return provider names without decrypting keys."""
        _, entries = self._load_store()
        return list(entries.keys())
