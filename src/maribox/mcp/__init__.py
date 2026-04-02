"""maribox MCP server — exposes all maribox tools via Model Context Protocol."""

from __future__ import annotations

import sys

from maribox.mcp.server import create_mcp_server


def run_server(transport: str = "stdio") -> None:
    """Start the MCP server with the specified transport."""
    server = create_mcp_server()

    if transport == "stdio":
        # MCP over stdio — reads from stdin, writes to stdout
        # All logging must go to stderr to avoid corrupting the protocol
        import asyncio

        asyncio.run(server.run_stdio_async())
    elif transport == "sse":
        host = "127.0.0.1"
        port = 8765
        server.run(transport="sse", host=host, port=port)
    else:
        print(f"Unknown transport: {transport}. Use 'stdio' or 'sse'.", file=sys.stderr)
        raise SystemExit(1)


# Module-level server instance for entry point: maribox.mcp:server
server = create_mcp_server()
