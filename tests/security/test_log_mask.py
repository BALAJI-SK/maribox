"""Tests for log masking."""

from __future__ import annotations

from maribox.security.log_mask import mask_secrets


class TestMaskSecrets:
    def test_anthropic_key(self) -> None:
        text = "Using key sk-ant-api03-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz for auth"
        masked = mask_secrets(text)
        assert "sk-ant-***REDACTED***" in masked
        assert "abc123" not in masked

    def test_google_key(self) -> None:
        text = "Google key AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"
        masked = mask_secrets(text)
        assert "AIza***REDACTED***" in masked

    def test_openai_key(self) -> None:
        text = "OpenAI key sk-proj-1234567890abcdef1234567890abcdef1234"
        masked = mask_secrets(text)
        assert "sk-***REDACTED***" in masked

    def test_no_keys_unchanged(self) -> None:
        text = "No API keys here, just normal text"
        assert mask_secrets(text) == text

    def test_multiple_keys(self) -> None:
        k1 = "sk-ant-api03-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
        k2 = "AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"
        text = f"key1={k1} key2={k2}"
        masked = mask_secrets(text)
        assert "abc123" not in masked
        assert "A1B2C3" not in masked
