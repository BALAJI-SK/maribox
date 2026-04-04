"""Custom exception hierarchy for maribox."""


class MariboxError(Exception):
    """Base exception for all maribox errors."""


class ConfigError(MariboxError):
    """Configuration-related error."""


class AuthError(MariboxError):
    """Authentication or key management error."""


class SessionError(MariboxError):
    """Session lifecycle error."""


class AgentError(MariboxError):
    """Agent orchestration error."""



class EncryptionError(MariboxError):
    """Encryption or decryption error."""
