# Project Structure

**Analysis Date:** 2026-04-05

## Directory Layout

```
maribox/
├── .agents/skills/              # Agent skill definitions
│   ├── marimo-notebook/         # marimo notebook writing skill
│   │   ├── SKILL.md
│   │   └── references/          # marimo API references
│   └── uv-package-manager/      # uv package manager skill
│       ├── SKILL.md
│       └── references/
├── docs/
│   ├── planning/                # Phase planning documents
│   │   ├── phase-4-sandbox.md
│   │   ├── phase-9-tui.md
│   │   └── ...
│   └── usage.md                 # User-facing usage guide
├── src/maribox/                 # Main package (6421 lines across 63 files)
│   ├── __init__.py
│   ├── __main__.py              # `python -m maribox` support
│   ├── cli.py                   # Typer CLI entry point (381 lines)
│   ├── exceptions.py            # Exception hierarchy (26 lines)
│   ├── agents/                  # AI agent layer (911 lines)
│   │   ├── __init__.py
│   │   ├── base.py              # MariboxAgent ABC (130 lines)
│   │   ├── orchestrator.py      # Routing agent (106 lines)
│   │   ├── notebook_agent.py    # Cell authoring agent
│   │   ├── ui_agent.py          # UI generation agent
│   │   ├── debug_agent.py       # Error analysis agent
│   │   ├── session_agent.py     # Session lifecycle agent
│   │   ├── profile.py           # Agent profile loading
│   │   └── tools/               # Agent tool definitions
│   │       ├── cell_tools.py
│   │       ├── debug_tools.py
│   │       ├── notebook_tools.py
│   │       ├── session_tools.py
│   │       └── ui_tools.py
│   ├── auth/                    # Authentication management
│   │   ├── __init__.py
│   │   └── manager.py           # AuthManager (set/get/rotate/revoke keys)
│   ├── commands/                # CLI command implementations
│   │   ├── agent.py
│   │   ├── auth.py
│   │   ├── cell.py
│   │   ├── config.py
│   │   ├── debug.py
│   │   ├── notebook_cmds.py
│   │   ├── session.py
│   │   └── ui.py
│   ├── config/                  # Configuration system
│   │   ├── __init__.py
│   │   ├── defaults.py          # DEFAULT_CONFIG dict
│   │   ├── io.py                # Load/save/init config
│   │   ├── resolution.py        # Config root resolution (walk-up)
│   │   └── schema.py            # Dataclass models (MariboxConfig, etc.)
│   ├── mcp/                     # MCP server
│   │   ├── __init__.py
│   │   ├── server.py            # FastMCP tool registration (25 tools)
│   │   └── tools.py             # Shared tool helpers
│   ├── notebook/                # Notebook runtime
│   │   ├── __init__.py
│   │   ├── cell.py              # Cell, CellId, CellOutput, CellStatus
│   │   ├── dag.py               # Cell dependency graph
│   │   ├── export.py            # Import/export notebook.py files
│   │   └── runtime.py           # MarimoRuntime (headless kernel)
│   ├── sandbox/                 # Session management (legacy name, local-only)
│   │   ├── __init__.py
│   │   └── session.py           # SessionManager (directory-based)
│   ├── security/                # Encryption and key management
│   │   ├── __init__.py
│   │   ├── encryption.py        # AES-256-GCM + Argon2id + KeyStore
│   │   ├── keyring_store.py     # OS keychain wrapper
│   │   └── log_mask.py          # API key pattern masking
│   └── tui/                     # Terminal UI (2591 lines)
│       ├── __init__.py          # run_tui() entry point
│       ├── app.py               # MariboxApp (Textual App)
│       ├── message.py           # ChatMessage, Conversation, MessageRole
│       ├── styles.py            # Theme colors and CSS constants
│       ├── styles.tcss          # Textual CSS theme
│       ├── screens/
│       │   ├── __init__.py
│       │   └── chat.py          # ChatScreen (main interface, 432 lines)
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── input_bar.py     # Multi-line input with Enter-send
│       │   ├── message_display.py # Single message renderer
│       │   ├── messages_list.py  # Scrollable message list
│       │   ├── sidebar.py       # Toggleable right sidebar
│       │   ├── status_bar.py    # Bottom status bar
│       │   └── welcome.py       # Welcome/empty state screen
│       └── dialogs/
│           ├── __init__.py
│           ├── command_palette.py # Ctrl+K filterable commands
│           ├── help_dialog.py    # Key binding reference
│           ├── model_selector.py # Provider/model picker
│           ├── quit_dialog.py    # Quit confirmation
│           └── session_switcher.py # Session switching modal
├── tests/                       # Test suite (30 files, ~140 tests)
│   ├── conftest.py              # Shared fixtures
│   ├── agents/
│   ├── auth/
│   ├── commands/
│   ├── config/
│   ├── integration/
│   ├── mcp/
│   ├── notebook/
│   ├── sandbox/
│   ├── security/
│   └── tui/
├── pyproject.toml               # Package definition
├── uv.lock                      # Dependency lockfile
├── CLAUDE.md                    # Claude Code instructions
├── README.md                    # Project documentation
├── requirements.md              # Detailed requirements spec
└── .gitignore
```

## Key Locations

| What | Where |
|------|-------|
| CLI commands | `src/maribox/commands/*.py` |
| CLI entry point | `src/maribox/cli.py` → `app = typer.Typer()` |
| TUI entry | `src/maribox/tui/__init__.py` → `run_tui()` |
| MCP server | `src/maribox/mcp/server.py` → `create_mcp_server()` |
| Agent base class | `src/maribox/agents/base.py` → `MariboxAgent` |
| Agent routing | `src/maribox/agents/orchestrator.py` → `_ROUTING_RULES` |
| Session management | `src/maribox/sandbox/session.py` → `SessionManager` |
| Notebook runtime | `src/maribox/notebook/runtime.py` → `MarimoRuntime` |
| Encryption | `src/maribox/security/encryption.py` → `KeyStore` |
| Config schema | `src/maribox/config/schema.py` → `MariboxConfig` |
| Config resolution | `src/maribox/config/resolution.py` → `resolve_config_root()` |

## Naming Conventions

- **Modules:** `snake_case` (e.g., `notebook_agent.py`, `cell_tools.py`)
- **Classes:** `PascalCase` (e.g., `MariboxAgent`, `SessionManager`, `ChatScreen`)
- **Data models:** `PascalCase` dataclasses (e.g., `AgentProfile`, `CellOutput`)
- **CLI commands:** `kebab-case` groups (e.g., `session new`, `cell add`)
- **Config files:** `snake_case.toml` (e.g., `config.toml`, `profiles.toml`)
- **Tests:** `test_{module}.py` with `Test{ClassName}` class groups

## Code Size Distribution

| Module | Lines | % of Total |
|--------|-------|-----------|
| TUI (screens, widgets, dialogs) | 2591 | 40% |
| CLI (cli.py + commands) | ~700 | 11% |
| Agents (base + subs + tools) | 911 | 14% |
| Config system | ~200 | 3% |
| Notebook (runtime + cell + dag + export) | ~400 | 6% |
| Security (encryption + keyring + log_mask) | ~250 | 4% |
| MCP server | ~250 | 4% |
| Auth, sandbox, exceptions, etc. | ~500 | 8% |
| **Total** | **~6421** | **100%** |

---

*Structure analysis: 2026-04-05*
