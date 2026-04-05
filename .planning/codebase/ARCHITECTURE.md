# Architecture

**Analysis Date:** 2026-04-05

## Pattern

maribox follows a **layered service architecture** with CLI/TUI/MCP as interchangeable frontends over a shared core:

```
┌─────────────────────────────────────────────┐
│  Frontends (entry points)                    │
│  CLI (Typer)  │  TUI (Textual)  │  MCP      │
├─────────────────────────────────────────────┤
│  Agent Layer (Google ADK)                    │
│  Orchestrator → Notebook / UI / Debug /     │
│                 Session                      │
├─────────────────────────────────────────────┤
│  Core Services                               │
│  SessionManager │ MarimoRuntime │ AuthManager│
│  ConfigManager  │ KeyStore      │ LogMask    │
├─────────────────────────────────────────────┤
│  Data Layer                                  │
│  TOML configs │ Binary keys.enc │ notebook.py│
│  Session dirs │ Run logs                     │
└─────────────────────────────────────────────┘
```

## Entry Points

Three entry points into the same core:

1. **CLI** (`src/maribox/cli.py`): Typer app with command groups: `session`, `cell`, `notebook`, `ui`, `debug`, `agent`, `auth`, `config`, plus top-level `tui` and `serve` commands. Commands in `src/maribox/commands/` delegate to core services.

2. **TUI** (`src/maribox/tui/app.py`): Textual `App` that renders an OpenCode-style chat interface. `ChatScreen` is the main screen with messages list, sidebar, input bar, and status bar. Modal dialogs for help, commands, sessions, models, quit.

3. **MCP** (`src/maribox/mcp/server.py`): FastMCP server exposing 25 tools over stdio/SSE. Each tool resolves config context, then delegates to the same core services.

## Agent Hierarchy

```
OrchestratorAgent (keyword-based routing)
  ├── SessionAgent    → session lifecycle (create, stop, kill, snapshot)
  ├── NotebookAgent   → cell CRUD and execution (add, run, edit, remove)
  ├── UIAgent         → marimo UI widget generation (sliders, tables, charts)
  └── DebugAgent      → error capture, traceback analysis, fix proposals
```

- Routing: Keyword matching in `src/maribox/agents/orchestrator.py` (`_ROUTING_RULES` dict)
- Each agent has: system prompt, tool definitions, provider/model profile
- Agents defined in `src/maribox/agents/`, tools in `src/maribox/agents/tools/`
- Base class: `MariboxAgent` (ABC) in `src/maribox/agents/base.py` with `invoke()` and `stream()` methods

## Data Flow

**Typical notebook authoring flow:**
```
User prompt → CLI/TUI/MCP
    → OrchestratorAgent._route_request(message)
        → NotebookAgent.invoke(message, context={session_id})
            → tool: cell_add / cell_run / cell_edit
                → MarimoRuntime.add_cell() / .run_cell()
                    → Session directory (notebook.py updated)
```

**Config resolution flow:**
```
resolve_config_root() → walk up from CWD looking for .maribox/
    → load_config(root) → parse config.toml
    → merge with project.toml if exists
    → merge with agents/profiles.toml if exists
```

**Key storage flow:**
```
maribox auth set anthropic
    → AuthManager.set_key(provider, key)
        → KeyStore.store_key() → AES-256-GCM encrypt → write keys.enc
        → keyring_store.set_password() → OS keychain
        → log_mask masks key patterns in output
```

## Abstractions

**`MariboxAgent` (ABC):** Base for all agents. Provides `invoke()`, `stream()`, `_register_tools()`, `_system_prompt()`. Subclasses implement domain-specific tools and prompts.

**`MarimoRuntime`:** Manages marimo kernel subprocess. Async API for cell CRUD. Currently uses subprocess fallback; real implementation will use WebSocket API.

**`SessionManager`:** Local directory-based session management. Creates/reads/removes session directories with `meta.toml`, `notebook.py`, `run.log`.

**`AuthManager`:** Unified interface for key storage. Wraps `KeyStore` (encrypted file) and OS keychain. Supports set/get/rotate/revoke operations.

**`CellDAG`:** Tracks cell dependencies via AST analysis. Provides topological ordering, stale cell detection, and dependency queries.

## Key Boundaries

- **`maribox.agents`** ↔ **`maribox.commands`**: Agents don't import commands. Commands instantiate agents.
- **`maribox.sandbox.session`** ↔ **`maribox.notebook.runtime`**: SessionManager manages directories; MarimoRuntime manages kernel process.
- **`maribox.security`** ↔ **`maribox.auth`**: Security provides primitives (encrypt, keyring); Auth provides the manager interface.
- **`maribox.tui`** ↔ **core**: TUI imports from agents, config, and auth. Core has no TUI dependency.

---

*Architecture analysis: 2026-04-05*
