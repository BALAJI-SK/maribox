# Phase 3: Authentication and Security

## Objective

Implement a security layer that protects API keys and credentials at rest and in transit. All secrets are encrypted with AES-256-GCM, derived from a user passphrase via Argon2id, and stored either in an encrypted file (`keys.enc`) or the OS keychain. Sensitive values are held in `bytearray` instances that can be explicitly zeroed, and all log output is sanitized through regex-based masking to prevent accidental credential leakage.

## Files to Create

- `src/maribox/security/__init__.py` — re-exports `AuthManager`, `mask_secrets`
- `src/maribox/security/encryption.py` — AES-256-GCM encryption with Argon2id key derivation
- `src/maribox/security/keyring_store.py` — OS keychain integration via `python-keyring`
- `src/maribox/security/log_mask.py` — regex-based log sanitization
- `src/maribox/auth/__init__.py` — re-exports `AuthManager`
- `src/maribox/auth/manager.py` — `AuthManager` orchestrating encryption and storage backends
- `src/maribox/commands/auth.py` — CLI subcommands: `maribox auth login`, `logout`, `status`, `keys`

## Key Interfaces

### `encryption.py`

```python
_SALT_SIZE = 32
_NONCE_SIZE = 12
_KEY_SIZE = 32                          # AES-256
_ARGON2_TIME_COST = 3
_ARGON2_MEMORY_COST = 65536             # 64 MB
_ARGON2_PARALLELISM = 4

class EncryptionError(Exception): ...

def derive_key(passphrase: str, salt: Optional[bytes] = None) -> Tuple[bytearray, bytes]:
    """
    Derive a 256-bit key from a passphrase using Argon2id.
    Returns (key_as_bytearray, salt).
    Key is a bytearray so it can be zeroed after use.
    If salt is None, a cryptographically random salt is generated.
    """

def encrypt(plaintext: str, key: bytearray) -> bytes:
    """
    Encrypt a string with AES-256-GCM.
    Output format: salt (32 bytes) || nonce (12 bytes) || ciphertext || tag.
    Raises EncryptionError on failure.
    """

def decrypt(ciphertext: bytes, passphrase: str) -> str:
    """
    Decrypt bytes produced by encrypt().
    Raises EncryptionError on authentication failure or corruption.
    """

def zero_key(key: bytearray) -> None:
    """
    Securely zero a key bytearray using ctypes.memset.
    Overwrites every byte with 0x00.
    """
```

### `keyring_store.py`

```python
_KEYRING_SERVICE = "maribox"

class KeyringStore:
    """Thin wrapper around python-keyring for storing/retrieving secrets."""

    @staticmethod
    def is_available() -> bool:
        """Return True if a keyring backend is functional on this OS."""

    @staticmethod
    def store(key_name: str, value: str) -> None:
        """Store a secret in the OS keychain under the maribox service."""

    @staticmethod
    def retrieve(key_name: str) -> Optional[str]:
        """Retrieve a secret from the OS keychain. Returns None if not found."""

    @staticmethod
    def delete(key_name: str) -> bool:
        """Delete a secret from the OS keychain. Returns True if it existed."""
```

### `log_mask.py`

```python
# Patterns for known secret prefixes
_SECRET_PATTERNS: List[Tuple[str, Pattern]] = [
    ("anthropic", re.compile(r"sk-ant-api03-[A-Za-z0-9\-_]{20,}")),
    ("google",    re.compile(r"AIza[A-Za-z0-9_\-]{35}")),
    ("openai",    re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("generic",   re.compile(r"(api[_-]?key|token|secret|password)\s*[:=]\s*\S+",
                             re.IGNORECASE)),
]

def mask_secrets(text: str) -> str:
    """
    Replace all detected secret patterns in text with masked equivalents.
    Example: 'sk-ant-api03-abc...' -> 'sk-ant-***REDACTED***'
    Returns the sanitized string.
    """

def register_pattern(name: str, pattern: Pattern) -> None:
    """Register a custom secret pattern for masking."""
```

### `auth/manager.py`

```python
class StorageBackend(Enum):
    ENCRYPTED_FILE = "file"              # keys.enc
    KEYRING = "keyring"                  # OS keychain

@dataclass
class StoredKey:
    name: str                            # e.g. "ANTHROPIC_API_KEY"
    provider: str                        # e.g. "anthropic"
    backend: StorageBackend
    added_at: datetime

class AuthManager:
    """
    Orchestrates credential storage and retrieval.
    Tries OS keyring first; falls back to encrypted file.
    All keys are held in bytearrays and zeroed after use.
    """

    def __init__(self, config_root: Optional[Path] = None): ...

    def login(self, provider: str, api_key: str, passphrase: Optional[str] = None) -> None:
        """
        Store an API key for the given provider.
        If keyring is available, store there (no passphrase needed).
        Otherwise, encrypt with passphrase and store in keys.enc.
        """

    def get_key(self, provider: str, passphrase: Optional[str] = None) -> Optional[str]:
        """
        Retrieve the API key for a provider.
        Returns None if no key is stored.
        The returned string should be used immediately and not logged.
        """

    def logout(self, provider: str) -> bool:
        """Remove the stored key for a provider. Returns True if it existed."""

    def status(self) -> Dict[str, StoredKey]:
        """Return metadata about all stored keys (never the key values themselves)."""

    def list_providers(self) -> List[str]:
        """Return a list of providers with stored keys."""

    def _get_keys_enc_path(self) -> Path:
        """Return path to keys.enc file."""
```

### `commands/auth.py`

```python
def auth_login(provider: str, api_key: str) -> None:
    """Interactive login flow. Prompts for passphrase if keyring is unavailable."""

def auth_logout(provider: str) -> None:
    """Remove stored credentials for a provider."""

def auth_status() -> None:
    """Print a Rich table showing stored key metadata (provider, backend, date)."""

def auth_keys() -> None:
    """List available provider names."""
```

## Dependencies

- **Phase 2 (Config)** must be complete: `AuthManager` needs `resolve_config_root()` to locate `keys.enc` and to read `MariboxConfig` for default storage backend preference.
- Runtime packages: `cryptography` (AES-256-GCM), `argon2-cffi` (Argon2id), `python-keyring` (OS keychain), `ctypes` (stdlib, for key zeroing).

## Testing Strategy

- **Unit tests for encryption round-trip**: Encrypt a known string, decrypt it, assert equality. Test with wrong passphrase to confirm `EncryptionError`.
- **Unit tests for key zeroing**: After calling `zero_key()`, assert the bytearray contains only `0x00` bytes.
- **Unit tests for Argon2id parameters**: Verify the derived key is 32 bytes, salt is 32 bytes, and that parameters match the spec (time_cost=3, memory=64MB).
- **Unit tests for log masking**: Feed strings containing `sk-ant-api03-...`, `AIza...`, `sk-...` and assert they are replaced with `***REDACTED***`. Test that non-secret text is preserved.
- **Unit tests for KeyringStore**: Mock the keyring backend; test store, retrieve, delete, and is_available.
- **Integration tests for AuthManager**: Full login -> get_key -> logout cycle with both backends. Verify keys.enc binary format is correct.
- **Negative tests**: Corrupt keys.enc file, missing passphrase, empty API key.
- **Timing tests**: Verify that key derivation takes a non-trivial amount of time (>= 0.5s) to confirm Argon2id parameters are active.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Argon2id with high memory cost is slow in CI | Test suite takes too long | Use reduced parameters (`time_cost=1`, `memory=64KB`) in test-only code paths via an env var |
| `keys.enc` corruption loses all keys | User must re-enter all API keys | Write keys.enc atomically (temp file + rename); keep a `.bak` of the previous version |
| Keyring unavailable on headless Linux | Falls back to encrypted file, but user may not expect it | `auth_status` clearly shows which backend each key uses; `auth login` prints a warning when falling back |
| `ctypes.memset` may be optimized away | Key zeroing is ineffective | Use `volatile` assignment pattern: read the bytearray after zeroing to prevent dead-store elimination |
| Log masking regex misses custom key formats | Secret leaks in logs | Allow user-defined patterns via `register_pattern()`; document how to add custom patterns in config |
| AES-256-GCM nonce reuse | Catastrophic confidentiality failure | Generate a cryptographically random nonce for every encryption call; never reuse nonces |

## Acceptance Criteria

- [ ] `encrypt()` and `decrypt()` round-trip correctly for all supported key formats
- [ ] Argon2id uses `time_cost=3`, 64MB memory, parallelism=4 as specified
- [ ] `zero_key()` overwrites the entire bytearray with zeros via `ctypes.memset`
- [ ] `keys.enc` is a binary file, not human-readable
- [ ] `mask_secrets()` catches `sk-ant-*`, `AIza*`, `sk-*` patterns and generic key=value patterns
- [ ] `AuthManager.login()` stores keys in OS keyring when available, encrypted file otherwise
- [ ] `AuthManager.get_key()` returns the correct key and never logs it
- [ ] `AuthManager.logout()` removes keys from the correct backend
- [ ] `maribox auth status` shows provider, backend, and date without revealing key values
- [ ] Corrupted `keys.enc` raises `EncryptionError`, does not crash silently
- [ ] All key material is held in `bytearray` (not `str`) wherever possible
- [ ] Unit test coverage >= 90% for `security/` and `auth/` packages
