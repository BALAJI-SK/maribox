"""Log output sanitization — masks API key patterns."""

from __future__ import annotations

import logging
import re

# (pattern, replacement) pairs for known API key formats
KEY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"sk-ant-api03-[A-Za-z0-9\-]{20,}"), "sk-ant-***REDACTED***"),
    (re.compile(r"AIza[A-Za-z0-9\-_]{30,}"), "AIza***REDACTED***"),
    (re.compile(r"sk-[A-Za-z0-9\-_]{20,}"), "sk-***REDACTED***"),
    (re.compile(r"[a-f0-9]{32}\.[a-zA-Z0-9]{16}"), "zhipu-***REDACTED***"),
]


def mask_secrets(text: str) -> str:
    """Mask API key patterns in text.

    Args:
        text: Input string that may contain API keys.

    Returns:
        String with all matching key patterns replaced by masked versions.
    """
    for pattern, replacement in KEY_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class MaskingFormatter(logging.Formatter):
    """Logging formatter that automatically masks API keys in all output."""

    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        return mask_secrets(result)
