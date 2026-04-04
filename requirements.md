# maribox — requirements

> Multi-session marimo notebook orchestrator with collaborative AI agents.  
> Distributed as a `uv` tool. Runs as a CLI and TUI application.

---

## 1. Project overview

`maribox` is a command-line and terminal UI application that spins up marimo
notebook sessions, orchestrates multiple AI agents (Anthropic, Google GLM,
OpenAI) to collaboratively author notebook cells and UI code, executes the
resulting notebooks, and manages all configuration under a `.maribox` directory
in either the OS user path or the project root.

---

## 2. Goals

- Let developers create, author, and run marimo notebooks entirely from the
  terminal without touching a browser.
- Enable multi-agent collaboration where each agent specialises in a role
  (notebook authoring, UI generation, debugging, session management).
- Provide an OpenCode-style TUI chat interface that gives live visibility into
  running sessions, cell outputs, agent activity, and supports multi-line input
  with command palette and model selection.
- Expose the same surface as an MCP server so Claude Code, OpenCode, and VS
  Code extensions can drive maribox as a tool.
- Store all configuration, credentials, and session state in a single
  `.maribox` directory — portable, version-controllable (secrets excluded),
  and OS-agnostic.

---

## 3. Non-goals

- maribox is not a general-purpose notebook IDE. It does not replace the
  marimo browser UI; it wraps it.
- maribox does not manage Python environments beyond the local session
  directories.
- maribox does not stream notebook outputs to external dashboards or BI tools.

---

## 4. Technology stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | ADK requirement; rich ecosystem |
| Agent framework | Google ADK (`google-adk`) | Multi-agent orchestration, tool routing |
| CLI framework | Typer | Ergonomic, auto-generates `--help` |
| TUI framework | Textual | Modern async TUI, first-class Python |
| Notebook runtime | marimo (headless) | Reactive cell DAG, WebSocket API |
| Secret storage | `python-keyring` | OS native (Keychain / libsecret / Win cred) |
| Encryption | `cryptography` (AES-256-GCM) | Envelope-encrypt keys at rest |
| Config format | TOML (`tomllib` / `tomli-w`) | Human-readable, stdlib in 3.11 |
| Packaging | `uv` + `pyproject.toml` | Zero-install via `uvx maribox` |
| MCP transport | stdio (`mcp` SDK) | Claude Code / OpenCode compatibility |

---

## 5. Configuration — `.maribox` directory

### 5.1 Resolution order

maribox resolves the config root using the following priority (first match wins):

1. `MARIBOX_HOME` environment variable (absolute path)
2. `<project-root>/.maribox/` — present when a `.maribox/` directory exists
   anywhere in the current directory ancestry (walk up to filesystem root)
3. `~/.config/maribox/` — OS user config path via `platformdirs`

### 5.2 Directory layout

```
.maribox/
├── config.toml          # Global settings (providers, defaults, TUI prefs)
├── keys.enc             # AES-256-GCM encrypted key ciphertext + nonces
├── sessions/
│   ├── <session-id>/
│   │   ├── meta.toml    # Session metadata (name, created, status)
│   │   ├── notebook.py  # Generated marimo notebook source
│   │   └── run.log      # Captured cell output log
├── agents/
│   └── profiles.toml    # Per-agent model + system prompt overrides
└── project.toml         # Project-level overrides (provider, model, ignore paths)
```

### 5.3 `config.toml` schema

```toml
[maribox]
version = "1"
default_provider = "anthropic"        # anthropic | google | openai | glm | custom
default_model = "claude-sonnet-4-6"
auto_open_browser = false
log_level = "info"                    # debug | info | warn | error

[marimo]
port_range = [7000, 7100]             # ports maribox may bind
headless = true

[tui]
theme = "dark"                        # dark | light | system
refresh_rate_ms = 250
show_agent_thoughts = true
```

### 5.4 `project.toml` schema (per-project override)

```toml
[project]
name = "my-analysis"
provider = "google"
model = "gemini-2.5-pro"

[agents]
notebook_agent = { model = "claude-sonnet-4-6" }
debug_agent    = { model = "gpt-4o" }
```

---

## 6. CLI specification

Invoked as `uvx maribox <command> [options]` or `maribox <command>` when
installed globally.

### 6.1 Session management

```
maribox session new [--name NAME] [--provider PROVIDER] [--model MODEL]
    Create a new marimo session.
    Outputs: session-id, status.

maribox session list
    Table of all sessions: id, name, status, provider, created.

maribox session attach <session-id>
    Opens the TUI attached to an existing session.

maribox session stop <session-id>
    Gracefully shuts down the marimo kernel.

maribox session kill <session-id>
    Force-terminates without cleanup.

maribox session snapshot <session-id> [--out PATH]
    Saves notebook.py + run.log to a snapshot archive.

maribox session rm <session-id>
    Removes session directory.
```

### 6.2 Notebook authoring

```
maribox cell add <session-id> --code CODE [--after CELL_ID]
    Appends or inserts a Python cell via the NotebookAgent.

maribox cell run <session-id> [--cell CELL_ID | --all]
    Executes one cell or the full notebook; streams output.

maribox cell edit <session-id> --cell CELL_ID --code CODE
    Replaces cell source; triggers downstream reactive re-run.

maribox cell rm <session-id> --cell CELL_ID
    Removes a cell and updates the DAG.

maribox notebook show <session-id>
    Pretty-prints the current notebook source with cell IDs.

maribox notebook save <session-id> [--out PATH]
    Writes notebook.py to disk (defaults to session dir).
```

### 6.3 UI generation

```
maribox ui generate <session-id> --prompt PROMPT
    UIAgent writes marimo UI components (sliders, tables, charts)
    as new cells and hot-reloads the kernel.

maribox ui preview <session-id>
    Opens the marimo browser UI for the session (if not headless).
```

### 6.4 Debugging

```
maribox debug last <session-id>
    Shows the last error with stack trace and cell context.

maribox debug fix <session-id> [--cell CELL_ID]
    DebugAgent analyses the error and proposes a patched cell;
    prompts for confirmation before applying.

maribox debug explain <session-id> --cell CELL_ID
    DebugAgent explains what a cell does and its dependencies.
```

### 6.5 Agent management

```
maribox agent list
    Lists available agent roles and their active model config.

maribox agent run <role> --prompt PROMPT [--session SESSION_ID]
    Runs a single agent role with an ad-hoc prompt.
```

### 6.6 Auth (API key management)

```
maribox auth set <provider>
    Hidden prompt for API key; encrypts and stores in OS keychain + keys.enc.
    Providers: anthropic | google | openai | glm | custom

maribox auth list
    Shows masked keys, models, and status per provider.

maribox auth use <provider> [--model MODEL] [--project]
    Sets the active provider globally or for the current project.

maribox auth rotate <provider>
    Replaces the key in-place; old key is zeroed.

maribox auth revoke <provider>
    Wipes key from keychain and keys.enc after confirmation.
```

### 6.7 Config

```
maribox config init [--global | --project]
    Scaffolds a .maribox/ directory with defaults.

maribox config show
    Prints resolved config (merged global + project, secrets redacted).

maribox config set KEY VALUE [--global | --project]
    Updates a single config key (dot-path notation).

maribox config path
    Prints the resolved config root in use.
```

### 6.8 MCP server mode

```
maribox serve --mcp [--transport stdio | sse]
    Starts maribox as an MCP server. All CLI commands are exposed
    as MCP tools callable by Claude Code, OpenCode, or VS Code.
```

### 6.9 TUI launcher

```
maribox tui [--session SESSION_ID]
    Opens the OpenCode-style Textual TUI. Without a session ID, shows the
    chat interface with a welcome screen.
```

---

## 7. TUI specification

The TUI follows an OpenCode-style design with a chat-centric interface,
collapsible sidebar, multi-line input, and modal dialogs.

### 7.1 Layout

```
+--------------------------------------------------+
|  Messages List (left)          | Sidebar (right)  |
|  - User/Assistant messages     | - Session info   |
|  - Tool call outputs           | - Files          |
|  - Welcome screen              | - Agents         |
+--------------------------------------------------+
|  > Input area (multi-line)                       |
|    Enter to send, \+Enter for newline            |
+--------------------------------------------------+
|  [Ctrl+? help] [status] ... [tokens] [model]     |
+--------------------------------------------------+
```

### 7.2 Screens and dialogs

| Component | Description |
|---|---|
| ChatScreen | Main interface with messages list, sidebar, and input bar |
| HelpScreen | Modal overlay showing all key bindings |
| SessionSwitcher | Modal for switching between conversation sessions |
| CommandPalette | Filterable command list (Ctrl+K) |
| ModelSelector | Provider/model selection with horizontal provider scroll |
| QuitDialog | Quit confirmation modal |

### 7.3 Key bindings

| Key | Action |
|---|---|
| `Enter` | Send message |
| `\+Enter` | Insert newline |
| `Ctrl+K` | Command palette |
| `Ctrl+L` | Toggle sidebar |
| `Ctrl+S` | Session switcher |
| `Ctrl+O` | Model selector |
| `Ctrl+N` | New session |
| `Ctrl+?` / `Ctrl+H` | Help overlay |
| `Ctrl+C` | Quit confirmation |
| `Escape` | Cancel / close dialog |
| `PageUp/PageDown` | Scroll messages |

### 7.4 Status indicators

- Session status: `running` (green) · `idle` (yellow) · `error` (red) · `stopped` (dim)
- Agent status: `thinking` (amber pulse) · `writing` (blue) · `idle` (dim)
- Cell status: `ok` · `running` (spinner) · `error` · `stale` (dependency changed)

---

## 8. Agent architecture

### 8.1 Agent roles

| Agent | Responsibility | Primary tools |
|---|---|---|
| `NotebookAgent` | Add, edit, run, and inspect cells | `cell_add`, `cell_run`, `cell_edit`, `notebook_show` |
| `UIAgent` | Generate marimo UI widgets and layouts | `cell_add`, `marimo_ui_components_reference` |
| `DebugAgent` | Capture errors, parse tracebacks, propose fixes | `cell_run`, `cell_edit`, `debug_last` |
| `SessionAgent` | Lifecycle management of sessions | `session_new`, `session_stop` |
| `OrchestratorAgent` | Route user intent to the right sub-agent | delegates to all above |

### 8.2 Collaboration flow

```
User prompt
    └── OrchestratorAgent
            ├── SessionAgent      →  ensure session is live
            ├── NotebookAgent     →  author Python cells
            ├── UIAgent           →  generate UI cells
            ├── DebugAgent        →  fix any errors after run
            └── NotebookAgent     →  final run + save
```

### 8.3 Agent configuration (`agents/profiles.toml`)

```toml
[orchestrator]
model    = "claude-sonnet-4-6"
provider = "anthropic"

[notebook]
model    = "claude-sonnet-4-6"
provider = "anthropic"

[ui]
model    = "gemini-2.5-pro"
provider = "google"

[debug]
model    = "gpt-4o"
provider = "openai"

[session]
model    = "claude-sonnet-4-6"
provider = "anthropic"
```

Each agent can be overridden independently at the project level via
`.maribox/project.toml`.

---

## 9. Security requirements

- API keys must never be written to environment variables, subprocess args, or
  temp files.
- Keys are encrypted with AES-256-GCM; the derived encryption key uses
  machine-id + random salt via Argon2id (minimum 3 iterations, 64 MB memory).
- Key material is decrypted in-process, passed directly to SDK constructors,
  and zeroed with `ctypes` immediately after each use.
- All log output must mask key substrings matching provider key patterns
  (`sk-ant-*`, `AIza*`, `sk-*`).
- `keys.enc` must be excluded from version control (`.gitignore` entry written
  by `maribox config init`).
- The OS keychain is the primary store; `keys.enc` is a local backup and must
  not be synced to cloud storage without explicit user opt-in.

---

## 10. Packaging and distribution

### 10.1 `pyproject.toml` entry points

```toml
[project]
name = "maribox"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "google-adk>=0.5",
  "typer>=0.12",
  "textual>=0.61",
  "marimo>=0.8",
  "cryptography>=42",
  "keyring>=25",
  "tomli-w>=1.0",
  "platformdirs>=4",
  "mcp>=1.0",
  "rich>=13",
]

[project.scripts]
maribox = "maribox.cli:app"

[project.entry-points."mcp.servers"]
maribox = "maribox.mcp:server"
```

### 10.2 Zero-install usage

```bash
uvx maribox session new --name demo
uvx maribox tui
uvx maribox serve --mcp
```

### 10.3 MCP config for Claude Code (`~/.claude/mcp.json`)

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

### 10.4 MCP config for OpenCode

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

---

## 11. Functional requirements

| ID | Requirement |
|---|---|
| F-01 | User can create a new session with `session new`; the command returns within 10 seconds. |
| F-02 | User can add a Python cell via natural language prompt; the NotebookAgent converts it to valid marimo cell source. |
| F-03 | User can run a cell and see streamed stdout/stderr in the TUI without leaving the terminal. |
| F-04 | When a cell raises an exception, the DebugAgent automatically captures it and offers a fix without a separate command. |
| F-05 | User can request a UI widget (chart, slider, table) and the UIAgent inserts valid marimo UI code as a new cell. |
| F-06 | Multiple sessions can run concurrently; the TUI shows all of them with independent status. |
| F-07 | Session state (notebook source + run log) persists across CLI restarts. |
| F-08 | `auth set` stores keys without echoing them; `auth list` shows only masked forms. |
| F-09 | Provider can be switched per-project without touching global config. |
| F-10 | `maribox serve --mcp` exposes all session and notebook commands as MCP tools callable from Claude Code. |
| F-11 | `config init` creates a `.maribox/` directory and writes defaults for both global and project scopes. |
| F-12 | Notebook can be saved as a standalone `notebook.py` runnable with `marimo run notebook.py`. |

---

## 12. Non-functional requirements

| ID | Requirement |
|---|---|
| NF-01 | CLI startup time (time to first output) must be under 500 ms on a modern laptop. |
| NF-02 | TUI must render at ≥ 30 fps under normal load. |
| NF-03 | No API key must appear in plaintext in `~/.config/maribox/`, project `.maribox/`, logs, or process args. |
| NF-04 | All Python code must pass `ruff` and `mypy --strict`. |
| NF-05 | Core modules must have ≥ 80% test coverage (pytest). |
| NF-06 | `maribox` must run on macOS 13+, Ubuntu 22.04+, and Windows 11 (WSL2). |
| NF-07 | Package size (wheel) must be under 5 MB excluding dependencies. |

---

## 13. Out-of-scope (v1)

- Notebook diffing or collaborative multi-user editing.
- Cloud-hosted session persistence (S3, GCS, etc.).
- Notebook export to Jupyter `.ipynb` format.
- GUI application (Electron, Tauri, etc.).
- Agent fine-tuning or custom model hosting.
