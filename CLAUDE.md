# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project summary

maribox is a CLI and TUI application that orchestrates isolated marimo notebook sessions inside AIO Sandbox containers, with multi-agent AI collaboration (Anthropic, Google, OpenAI). Distributed as a `uv` tool. Users build and run apps inside sandboxed environments via AIO Sandbox MCP servers.

## Tech stack

- **Python 3.11+** — `pyproject.toml` with `uv` packaging
- **Google ADK** (`google-adk`) — multi-agent orchestration and tool routing
- **Typer** — CLI framework
- **Textual** — async TUI framework
- **marimo** (headless) — notebook runtime with reactive cell DAG and WebSocket API
- **AIO Sandbox** — isolated containers providing secure code execution environments; accessed via MCP server protocol. Each sandbox is an ephemeral, containerized environment where agents can execute code, manage files, and install packages. Similar in concept to [E2B](https://github.com/e2b-dev/E2B) (cloud sandboxes for AI agents with Python/JS SDKs).
- **MCP SDK** (`mcp`) — stdio transport for Claude Code / OpenCode integration
- **cryptography** (AES-256-GCM) + **keyring** — encrypted API key storage
- **TOML** (`tomllib` / `tomli-w`) — all configuration files
- **Rich** — terminal output formatting

## Development commands

```bash
# Install for development
uv sync

# Lint and type-check (must pass before committing)
ruff check .
mypy --strict .

# Run tests (pytest, ≥80% coverage required on core modules)
pytest
pytest tests/test_specific.py::test_name   # single test

# Run the CLI locally
uv run maribox --help

# Run the TUI
uv run maribox tui

# Run as MCP server
uv run maribox serve --mcp --transport stdio
```

## Architecture

### Session management — session IDs

Every session is identified by a unique **session-id** (stored in `.maribox/sessions/<session-id>/`). All session operations accept a session-id:

```bash
maribox session attach <session-id>   # Open TUI attached to existing session
maribox session stop <session-id>     # Gracefully shut down session
maribox session kill <session-id>     # Force-terminate without cleanup
maribox session snapshot <session-id> # Save notebook + logs to archive
maribox session rm <session-id>       # Remove session and release sandbox
maribox cell add <session-id>         # Add cell to a specific session
maribox cell run <session-id>         # Run cells in a specific session
maribox ui generate <session-id>      # Generate UI in a specific session
maribox debug last <session-id>       # Debug errors in a specific session
```

Multiple sessions run concurrently — the TUI dashboard shows all sessions with independent status. Session state (notebook source + run log) persists across CLI restarts.

### AIO Sandbox integration

maribox uses AIO Sandbox MCP servers to build and run apps in isolated containers:

- Each `session new` provisions a fresh AIO Sandbox container with a marimo kernel
- Agents interact with sandboxes through MCP tools (`sandbox_exec`, file operations, package installation)
- The `SessionAgent` manages sandbox lifecycle (create, health-check, teardown)
- Sandboxes are ephemeral — state is persisted to `.maribox/sessions/<id>/` on the host
- The sandbox base URL is configurable in `config.toml` (`[sandbox] base_url`); leave blank to auto-provision
- Sandbox timeout defaults to 300 seconds (`[sandbox] timeout_seconds`)

### Config resolution (`.maribox/` directory)

Priority: `MARIBOX_HOME` env var → `<project-root>/.maribox/` (walk up ancestry) → `~/.config/maribox/`

Key files: `config.toml` (global settings), `project.toml` (per-project overrides), `keys.enc` (encrypted keys), `agents/profiles.toml` (per-agent model config), `sessions/<id>/` (session state with `meta.toml`, `notebook.py`, `run.log`).

### Agent hierarchy

```
OrchestratorAgent → routes user intent to specialized sub-agents:
  ├── SessionAgent   — sandbox + marimo kernel lifecycle (uses AIO Sandbox MCP tools)
  ├── NotebookAgent  — cell CRUD and execution
  ├── UIAgent        — marimo UI widget generation
  └── DebugAgent     — error capture, traceback analysis, fix proposals
```

Each agent has independent model/provider config in `agents/profiles.toml`, overridable per-project.

### CLI entry point

`maribox.cli:app` — Typer app. Command groups: `session`, `cell`, `notebook`, `ui`, `debug`, `agent`, `auth`, `config`, plus top-level `tui` and `serve` commands.

### MCP server

`maribox.mcp:server` — exposes all CLI commands as MCP tools over stdio transport. Configure in Claude Code via:

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

## Security constraints

- API keys are encrypted (AES-256-GCM, Argon2id key derivation), stored in OS keychain with `keys.enc` as local backup only
- Keys must never appear in env vars, subprocess args, temp files, or logs
- Log output must mask patterns matching `sk-ant-*`, `AIza*`, `sk-*`
- `keys.enc` must be in `.gitignore`
- Key material is zeroed with `ctypes` immediately after use
- Sandbox containers are isolated — no host filesystem or network access unless explicitly granted

## Code quality gates

- `ruff check .` and `mypy --strict .` must pass with zero errors
- Core modules require ≥80% test coverage
- CLI startup must be under 500ms
- TUI must render at ≥30fps
