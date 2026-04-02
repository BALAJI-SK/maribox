"""Tests for TUI app and screen creation."""

from maribox.tui.app import MariboxApp


class TestMariboxApp:
    def test_app_creation(self) -> None:
        app = MariboxApp(session_id=None)
        assert app._session_id is None

    def test_app_with_session(self) -> None:
        app = MariboxApp(session_id="test123")
        assert app._session_id == "test123"

    def test_app_title(self) -> None:
        assert MariboxApp.TITLE == "maribox"
