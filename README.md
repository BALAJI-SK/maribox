# maribox

Multi-session marimo notebook orchestrator with collaborative AI agents. Build and run marimo notebooks from your terminal with multi-provider AI assistance and an OpenCode-style chat interface.

## Features

- **OpenCode-style TUI** — full terminal chat interface with messages, sidebar, command palette, and model selector
- **Multi-agent AI** — specialized agents for notebook authoring, UI generation, debugging, and session management (Anthropic, Google, OpenAI, GLM 5.1)
- **Reactive cell DAG** — automatic variable dependency tracking; edit a cell and see downstream impacts instantly
- **Session management** — create, list, attach, snapshot, and manage notebook sessions from the CLI
- **MCP server** — expose all commands as tools for Claude Code, OpenCode, or VS Code integration
- **Encrypted secrets** — API keys stored with AES-256-GCM encryption in your OS keychain
- **Zero-install** — run directly with `uvx maribox`

## Quick Start

```bash
# Install (requires Python 3.11+)
uv sync

# Or run without installing
uvx maribox --help

# 1. Configure an AI provider
maribox auth set anthropic       # Prompts for API key (hidden input)
maribox auth set openai
maribox glm --api-key YOUR_KEY   # Configure GLM 5.1 (Zhipu AI)

# 2. Initialize config
maribox config init

# 3. Create a session
maribox session new --name "my-analysis"

# 4. Add and run cells
maribox cell add <session-id> --code "import marimo as mo; x = 42"
maribox cell add <session-id> --code "print(f'Answer: {x}')"
maribox cell run <session-id> --all

# 5. Debug errors
maribox debug last <session-id>
maribox debug fix <session-id>

# 6. Save the notebook
maribox notebook save <session-id>
```

## Installation

### From source (development)

```bash
git clone https://github.com/BALAJI-SK/maribox.git
cd maribox
uv sync
uv run maribox --help
```

### Run without installing

```bash
uvx maribox --help
```

## CLI Reference

### Configuration

```bash
maribox config init              # Create .maribox/ directory with defaults
maribox config show              # Display resolved config
maribox config set maribox.default_provider glm  # Update a setting
maribox config path              # Show active config directory
```

### Authentication

```bash
maribox auth set <provider>      # Store API key (anthropic|google|openai|glm|custom)
maribox auth list                # Show masked keys per provider
maribox auth use <provider>      # Set active provider
maribox auth rotate <provider>   # Replace stored key
maribox auth revoke <provider>   # Delete stored key
maribox glm                      # One-command GLM 5.1 setup
```

### Sessions

```bash
maribox session new --name "analysis"     # Create a new session
maribox session list                      # Show all sessions
maribox session attach <session-id>       # Open TUI attached to session
maribox session stop <session-id>         # Graceful shutdown
maribox session kill <session-id>         # Force terminate
maribox session snapshot <session-id>     # Save notebook + logs
maribox session rm <session-id>           # Remove session
```

### Cells

```bash
maribox cell add <session-id> --code "x = 1"           # Add cell
maribox cell add <session-id> --code "y = x+1" --after <cell-id>  # Insert after cell
maribox cell run <session-id> --cell <cell-id>          # Run single cell
maribox cell run <session-id> --all                     # Run all cells
maribox cell edit <session-id> --cell <cell-id> --code "x = 2"  # Edit cell
maribox cell rm <session-id> --cell <cell-id>           # Remove cell
```

### Notebook

```bash
maribox notebook show <session-id>         # Pretty-print notebook source
maribox notebook save <session-id>         # Save to notebook.py
maribox notebook save <session-id> --out ./my_notebook.py  # Custom path
```

### UI Generation

```bash
maribox ui generate <session-id> --prompt "Add a slider for x with range 1-100"
maribox ui preview <session-id>            # Open marimo browser UI
```

### Debugging

```bash
maribox debug last <session-id>            # Show last error + traceback
maribox debug fix <session-id>             # AI proposes a fix
maribox debug fix <session-id> --cell <id> # Fix specific cell
maribox debug explain <session-id> --cell <id>  # Explain cell behavior
```

### Agents

```bash
maribox agent list                         # List agent roles and models
maribox agent run notebook --prompt "Create a data loading cell" --session <id>
```

### TUI

```bash
maribox tui                                # Open OpenCode-style chat interface
maribox tui --session <session-id>         # Open attached to session
```

The TUI provides an OpenCode-style interface:

```
+--------------------------------------------------+
|  Messages List (left)          | Sidebar (right)  |
|  - User/Assistant messages     | - Session info   |
|  - Tool call outputs           | - Files          |
|  - Markdown rendering          | - Agents         |
+--------------------------------------------------+
|  > Input area (multi-line)                       |
|    Enter to send, \+Enter for newline            |
+--------------------------------------------------+
|  [Ctrl+? help] [status] ... [tokens] [model]     |
+--------------------------------------------------+
```

Key bindings inside the TUI:

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `\+Enter` | Insert newline |
| `Ctrl+K` | Command palette |
| `Ctrl+L` | Toggle sidebar |
| `Ctrl+O` | Model selector |
| `Ctrl+S` | Session switcher |
| `Ctrl+N` | New session |
| `Ctrl+?` | Help overlay |
| `Ctrl+C` | Quit |

### MCP Server

```bash
maribox serve --mcp --transport stdio      # For Claude Code / OpenCode
maribox serve --mcp --transport sse        # For HTTP clients
```

Configure in Claude Code (`~/.claude/mcp.json`):

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

## Architecture

```
maribox/
├── src/maribox/
│   ├── cli.py              # Typer CLI entry point
│   ├── config/             # 3-tier config resolution (env > project > global)
│   ├── security/           # AES-256-GCM encryption, keyring, log masking
│   ├── auth/               # API key management (set, rotate, revoke)
│   ├── sandbox/            # Session lifecycle management
│   ├── notebook/           # Cell DAG, marimo runtime, export/import
│   ├── agents/             # Multi-agent system (orchestrator + specialists)
│   ├── commands/           # CLI command implementations
│   ├── mcp/                # FastMCP server with 25 tools
│   └── tui/                # OpenCode-style Textual TUI
│       ├── app.py          # MariboxApp
│       ├── screens/chat.py # ChatScreen (main interface)
│       ├── widgets/        # MessagesList, Sidebar, InputBar, StatusBar
│       ├── dialogs/        # Help, SessionSwitcher, CommandPalette, ModelSelector
│       └── message.py      # ChatMessage, Conversation data models
├── tests/                  # Unit + integration tests
└── docs/planning/          # Phase-by-phase design documents
```

### Agent Hierarchy

```
OrchestratorAgent — routes user intent to specialized agents:
  ├── NotebookAgent  — cell CRUD, code generation, execution
  ├── UIAgent        — marimo UI widget generation (sliders, tables, charts)
  ├── DebugAgent     — error analysis, traceback parsing, fix proposals
  └── SessionAgent   — session lifecycle management
```

Each agent has independent model/provider config in `agents/profiles.toml`.

### Cell DAG

maribox tracks variable dependencies between cells using Python AST analysis. When you edit a cell, the DAG automatically identifies which downstream cells need re-execution:

```
Cell 1: x = 1
Cell 2: y = x + 1    ← depends on Cell 1
Cell 3: z = y * 2    ← depends on Cell 2
```

Editing Cell 1 marks Cells 2 and 3 as stale.

## Configuration

### Config Resolution

maribox resolves config in this order (first match wins):
1. `MARIBOX_HOME` environment variable
2. `.maribox/` directory (walks up from current directory)
3. `~/.config/maribox/` (OS default)

### config.toml

```toml
[maribox]
default_provider = "anthropic"     # anthropic | google | openai | glm | custom
default_model = "claude-sonnet-4-6"
log_level = "info"

[marimo]
port_range = [7000, 7100]
headless = true

[tui]
theme = "dark"
refresh_rate_ms = 250
```

### Per-Project Overrides

Create `.maribox/project.toml`:

```toml
[project]
name = "my-analysis"
provider = "glm"
model = "glm-4-plus"

[agents]
notebook = { model = "glm-4-plus", provider = "glm" }
debug = { model = "gpt-4o", provider = "openai" }
```

## Development

```bash
uv sync                                    # Install dependencies
ruff check .                               # Lint
pytest                                     # Run all tests
pytest --cov=maribox                       # Coverage report
pytest tests/notebook/test_dag.py          # Single test file
pytest tests/agents/test_profile.py::TestResolveModel::test_glm  # Single test
```

## License

Private repository.
