# maribox MCP Server Skill

## Description

Start and manage maribox as an MCP server, allowing Claude Code to directly create sessions, author notebook cells, execute code in AIO Sandbox containers, and manage multi-agent workflows.

## Trigger

When the user asks to:
- Start maribox as an MCP server
- Use maribox tools from Claude Code / OpenCode / VS Code
- Configure maribox MCP integration
- Serve maribox over stdio or SSE transport

## Instructions

### Start the MCP server

Run maribox as an MCP server over stdio transport:

```bash
uv run maribox serve --mcp --transport stdio
```

For SSE transport (used by web-based clients):

```bash
uv run maribox serve --mcp --transport sse
```

### Configure for Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "maribox": {
      "command": "uvx",
      "args": ["maribox", "serve", "--mcp", "--transport", "stdio"]
    }
  }
}
```

### Configure for OpenCode

Add to OpenCode config:

```json
{
  "mcp": {
    "servers": {
      "maribox": {
        "command": "uvx maribox serve --mcp"
      }
    }
  }
}
```

### Configure for VS Code

Add to VS Code `settings.json`:

```json
{
  "maribox.mcpCommand": "uvx maribox serve --mcp",
  "maribox.autoAttach": true
}
```

### Available MCP tools (once connected)

When maribox is running as an MCP server, the following tools are exposed:

| Tool | Description |
|------|-------------|
| `session_new` | Create a new sandbox + marimo session (returns session-id) |
| `session_list` | List all sessions with status |
| `session_attach` | Attach to an existing session by session-id |
| `session_stop` | Gracefully shut down a session |
| `session_kill` | Force-terminate a session |
| `session_snapshot` | Save notebook + logs to archive |
| `session_rm` | Remove session and release sandbox |
| `cell_add` | Add a Python cell to a session's notebook |
| `cell_run` | Execute a cell or all cells |
| `cell_edit` | Replace cell source |
| `cell_rm` | Remove a cell from the DAG |
| `notebook_show` | Display notebook source with cell IDs |
| `notebook_save` | Write notebook.py to disk |
| `ui_generate` | Generate marimo UI components from a prompt |
| `ui_preview` | Open browser UI for the session |
| `debug_last` | Show last error with context |
| `debug_fix` | DebugAgent proposes and applies a fix |
| `debug_explain` | Explain a cell's behavior and dependencies |
| `agent_list` | List agent roles and model config |
| `agent_run` | Run a single agent with an ad-hoc prompt |
| `auth_set` | Store API key for a provider |
| `auth_list` | Show masked keys per provider |
| `auth_use` | Set active provider |
| `config_show` | Print resolved config |
| `config_set` | Update a config key |

### Session workflow via MCP

1. **Create session**: Use `session_new` with optional name/provider/model. Returns a `session-id`.
2. **Author cells**: Use `cell_add` with the session-id and code (or natural language — NotebookAgent converts to valid marimo source).
3. **Execute**: Use `cell_run` with the session-id to execute one cell or all cells.
4. **Generate UI**: Use `ui_generate` with a prompt to create sliders, tables, charts as marimo UI cells.
5. **Debug**: If a cell errors, `debug_fix` automatically captures the traceback and proposes a patched cell.
6. **Save**: Use `notebook_save` to write a standalone `notebook.py` runnable with `marimo run`.

### Environment variables

- `MARIBOX_HOME` — override config root directory (highest priority in resolution order)
- `E2B_API_KEY` or sandbox provider key — if using cloud sandbox providers

### Notes

- All operations require a valid `session-id` (obtained from `session_new`)
- API keys are stored encrypted — never passed in plaintext
- The MCP server runs as a long-lived process; Claude Code manages its lifecycle
- Sandboxes are ephemeral — session state is persisted to `.maribox/sessions/<id>/`
