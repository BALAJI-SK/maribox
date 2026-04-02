"""Tests for MCP server creation and tool registration."""

from pathlib import Path

from maribox.mcp.server import create_mcp_server


class TestCreateMcpServer:
    def test_creates_server(self) -> None:
        server = create_mcp_server()
        assert server is not None
        assert server.name == "maribox"

    def test_with_config_root(self, tmp_path: Path) -> None:
        server = create_mcp_server(config_root=tmp_path)
        assert server is not None

    def test_server_has_tools(self) -> None:
        server = create_mcp_server()
        # The FastMCP object should be usable
        assert hasattr(server, "run")
