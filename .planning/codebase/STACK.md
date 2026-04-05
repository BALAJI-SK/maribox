# Technology Stack

**Analysis Date:** 2026-04-05

## Languages

**Primary:**
- Python 3.11+ — All application code (CLI, TUI, agents, config, security, notebook runtime)

**Secondary:**
- Textual CSS (`.tcss`) — TUI styling and layout declarations

## Runtime

**Environment:**
- Python 3.11+ (CPython, tested on 3.11.14)
- No browser runtime (terminal-only application)
- Marimo kernel runs headless as a subprocess

**Package Manager:**
- uv (via `pyproject.toml` and `uv.lock`)
- Distributed as `uv` tool: `uvx maribox`
- Lockfile: `uv.lock` present

## Frameworks

**Core:**
- Google ADK (`google-adk` >=0.5) — Multi-agent orchestration and tool routing
- Typer (>=0.12) — CLI framework with auto-generated `--help`
- Textual (>=0.61) — Async TUI framework (OpenCode-style chat interface)
- marimo (>=0.8) — Headless notebook runtime with reactive cell DAG
- FastMCP (`mcp` >=1.0) — MCP server over stdio/SSE transport

**LLM Integration:**
- litellm (>=1.40) — Unified interface to Anthropic, Google, OpenAI, Zhipu AI
- zhipuai (>=2.0) — GLM 4/5.1 model access

**Security:**
- cryptography (>=42) — AES-256-GCM encryption for API key storage
- argon2-cffi (>=23.1) — Argon2id key derivation
- keyring (>=25) — OS-native keychain integration

**Testing:**
- pytest (>=8) — Test runner
- pytest-asyncio (>=0.24) — Async test support
- pytest-cov (>=6) — Coverage reporting

**Build/Dev:**
- ruff (>=0.8) — Linting + formatting (target: py311, line-length: 120)
- mypy (>=1.13) — Strict type checking
- hatchling — Build backend

## Key Dependencies

**Critical:**
- `litellm` >=1.40 — Unified LLM API calls across providers (Anthropic, Google, OpenAI, GLM)
- `textual` >=0.61 — Async TUI framework powering the chat interface
- `marimo` >=0.8 — Notebook runtime with reactive cell DAG and WebSocket API
- `mcp` >=1.0 — MCP SDK for stdio/SSE tool server
- `google-adk` >=0.5 — Agent orchestration framework (Orchestrator → sub-agents)

**Infrastructure:**
- `httpx` >=0.27 — Async HTTP client (API calls, marimo kernel communication)
- `rich` >=13 — Terminal output formatting and progress bars
- `platformdirs` >=4 — OS-agnostic config directory resolution
- `tomli-w` >=1.0 — TOML serialization (config files, session metadata)

## Configuration

**Environment:**
- `MARIBOX_HOME` — Override config root directory
- Config files in TOML format (`config.toml`, `project.toml`, `meta.toml`, `profiles.toml`)
- API keys encrypted at rest in `keys.enc`, backed by OS keychain

**Build:**
- `pyproject.toml` — Package definition, build config, ruff/mypy/pytest settings
- `uv.lock` — Dependency lockfile

## Platform Requirements

**Development:**
- macOS 13+, Ubuntu 22.04+, Windows 11 (WSL2 or native)
- Python 3.11+, uv package manager
- No Docker or container runtime required

**Production:**
- Distributed as `uv` tool (`uvx maribox`)
- Entry point: `maribox.cli:app` (Typer)
- TUI entry: `maribox.tui:run_tui()`
- MCP entry: `maribox.mcp:server`
- Zero-install usage: `uvx maribox <command>`

---

*Stack analysis: 2026-04-05*
*Update after major dependency changes*
