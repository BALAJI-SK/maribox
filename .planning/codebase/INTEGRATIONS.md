# Integrations

**Analysis Date:** 2026-04-05

## AI Provider APIs

**Anthropic (Claude):**
- Used for: Default provider for orchestrator, notebook agent, session agent
- Default model: `claude-sonnet-4-6`
- Auth: API key via `maribox auth set anthropic`, stored encrypted in `keys.enc` + OS keychain
- Interface: `litellm.acompletion()` with `provider="anthropic"`

**Google (Gemini):**
- Used for: UI agent (default), optional for other agents
- Default model: `gemini-2.5-pro`
- Auth: API key via `maribox auth set google`
- Interface: `litellm.acompletion()` with `provider="google"`

**OpenAI (GPT):**
- Used for: Debug agent (default), optional for other agents
- Default model: `gpt-4o`
- Auth: API key via `maribox auth set openai`
- Interface: `litellm.acompletion()` with `provider="openai"`

**Zhipu AI (GLM):**
- Used for: Optional provider, first-class support with `maribox glm` shortcut
- Default model: `glm-4-plus`
- Auth: API key via `maribox glm --api-key` or `maribox auth set glm`
- Interface: `zhipuai` SDK + `litellm`

## Notebook Runtime

**marimo (headless):**
- Started as subprocess via `subprocess.Popen` in `src/maribox/notebook/runtime.py`
- Communication: WebSocket API (planned), subprocess fallback (current)
- Cell lifecycle: add → run → edit → remove with reactive DAG updates
- Reactive DAG: `src/maribox/notebook/dag.py` tracks cell dependencies

## MCP Protocol

**FastMCP server:**
- Transport: stdio (primary) or SSE
- Entry: `maribox serve --mcp --transport stdio`
- 25 tools exposed covering: config, auth, session, notebook, debug, agent, UI
- Registration: `src/maribox/mcp/server.py` using `@server.tool()` decorators

**Claude Code integration:**
```json
{"mcpServers": {"maribox": {"command": "uvx", "args": ["maribox", "serve", "--mcp", "--transport", "stdio"]}}}
```

## OS Keychain

**keyring integration:**
- Primary key store: OS-native (Keychain on macOS, libsecret on Linux, Windows Credential Manager)
- Backup store: `keys.enc` (AES-256-GCM encrypted binary file)
- Access: `src/maribox/security/keyring_store.py` wraps `keyring` library
- Key is zeroed with `ctypes.memset` after use

## File System

**Session storage:**
- Sessions stored as directories: `.maribox/sessions/<session-id>/`
- Each session has: `meta.toml` (metadata), `notebook.py` (marimo source), `run.log` (execution output)
- Snapshot: `maribox session snapshot` creates tar.gz archives

**Config resolution:**
- `MARIBOX_HOME` env → `.maribox/` (walk up ancestry) → `~/.config/maribox/`
- Global config: `config.toml`
- Project overrides: `project.toml`
- Agent profiles: `agents/profiles.toml`

---

*Integration analysis: 2026-04-05*
