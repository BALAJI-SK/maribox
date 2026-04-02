"""Tests for MCP server tool implementations."""

from pathlib import Path

from maribox.config.schema import MariboxConfig
from maribox.mcp.tools import ToolContext, format_result, resolve_tool_context


class TestFormatResult:
    def test_string_passthrough(self) -> None:
        assert format_result("hello") == "hello"

    def test_list_formatting(self) -> None:
        result = format_result(["a", "b", "c"])
        assert "a" in result
        assert "b" in result

    def test_dict_formatting(self) -> None:
        result = format_result({"key": "value", "num": 42})
        assert "key" in result
        assert "value" in result

    def test_truncation(self) -> None:
        long_text = "x" * 20_000
        result = format_result(long_text)
        assert len(result) < 15_000
        assert "truncated" in result

    def test_short_text_not_truncated(self) -> None:
        short = "hello world"
        assert format_result(short) == short


class TestResolveToolContext:
    def test_resolves_with_tmp_path(self, tmp_path: Path) -> None:
        # Create minimal config structure
        ctx = resolve_tool_context(tmp_path)
        assert isinstance(ctx, ToolContext)
        assert isinstance(ctx.config, MariboxConfig)
        assert ctx.config_root == tmp_path


class TestToolContext:
    def test_has_expected_fields(self, tmp_path: Path) -> None:
        config = MariboxConfig()
        ctx = ToolContext(config=config, config_root=tmp_path, auth_manager=None)  # type: ignore[arg-type]
        assert ctx.config is config
        assert ctx.config_root == tmp_path
