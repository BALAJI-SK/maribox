"""Tests for TUI widgets."""

from maribox.tui.widgets.agent_feed import AgentFeed
from maribox.tui.widgets.cell_panel import CellPanel
from maribox.tui.widgets.session_card import SessionCard


class TestSessionCard:
    def test_render_running(self) -> None:
        card = SessionCard(session_id="abc123", session_name="Test", status="running")
        content = card._render_content()
        assert "abc123" in content
        assert "Test" in content
        assert "running" in content

    def test_render_error(self) -> None:
        card = SessionCard(session_id="err1", status="error")
        content = card._render_content()
        assert "error" in content

    def test_render_no_name(self) -> None:
        card = SessionCard(session_id="xyz", status="idle")
        content = card._render_content()
        assert "xyz" in content


class TestCellPanel:
    def test_render_empty(self) -> None:
        panel = CellPanel(title="Cell 1")
        content = panel._render_content()
        assert "Cell 1" in content
        assert "No cell selected" in content

    def test_render_with_code(self) -> None:
        panel = CellPanel(title="Cell 1", code="x = 42")
        content = panel._render_content()
        assert "x = 42" in content


class TestAgentFeed:
    def test_is_rich_log(self) -> None:
        feed = AgentFeed()
        assert hasattr(feed, "write")

    def test_log_agent_message(self) -> None:
        feed = AgentFeed()
        # Should not raise
        feed.log_agent_message("notebook", "Created cell")
