"""Tests for base agent class and data types."""

from maribox.agents.base import AgentMessage, AgentResponse


class TestAgentMessage:
    def test_creation(self) -> None:
        msg = AgentMessage(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"
        assert msg.tool_calls is None

    def test_with_tool_calls(self) -> None:
        msg = AgentMessage(
            role="assistant",
            content="",
            tool_calls=[{"name": "create_cell", "args": {"code": "x=1"}}],
        )
        assert len(msg.tool_calls) == 1

    def test_metadata(self) -> None:
        msg = AgentMessage(role="system", content="prompt", metadata={"key": "val"})
        assert msg.metadata["key"] == "val"


class TestAgentResponse:
    def test_success_response(self) -> None:
        resp = AgentResponse(
            message=AgentMessage(role="assistant", content="done"),
            success=True,
            model="claude-sonnet-4-6",
        )
        assert resp.success
        assert resp.model == "claude-sonnet-4-6"
        assert resp.tool_results == []

    def test_with_metrics(self) -> None:
        resp = AgentResponse(
            message=AgentMessage(role="assistant", content="ok"),
            success=True,
            duration_ms=150.0,
            tokens_used={"input": 10, "output": 20},
        )
        assert resp.duration_ms > 0
        assert resp.tokens_used["input"] == 10
