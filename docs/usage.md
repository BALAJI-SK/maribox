# maribox Usage Guide

This guide walks through every feature of maribox with practical examples.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuring AI Providers](#configuring-ai-providers)
- [Session Workflow](#session-workflow)
- [Notebook Authoring](#notebook-authoring)
- [UI Generation](#ui-generation)
- [Debugging](#debugging)
- [AI Agents](#ai-agents)
- [MCP Server Integration](#mcp-server-integration)
- [TUI (Terminal UI)](#tui-terminal-ui)
- [Configuration Reference](#configuration-reference)
- [GLM 5.1 (Zhipu AI) Setup](#glm-51-zhipu-ai-setup)

---

## Getting Started

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) package manager

### Install

```bash
git clone https://github.com/BALAJI-SK/maribox.git
cd maribox
uv sync
```

Or run without cloning:

```bash
uvx maribox --help
```

### First-Time Setup

```bash
# 1. Initialize configuration
maribox config init

# 2. Set up an AI provider (pick one or more)
maribox auth set anthropic    # For Claude models
maribox auth set openai       # For GPT models
maribox auth set google       # For Gemini models

# 3. Verify setup
maribox config show
maribox auth list
```

---

## Configuring AI Providers

maribox supports five providers:

| Provider | Models | Setup Command |
|----------|--------|---------------|
| `anthropic` | claude-sonnet-4-6, claude-opus-4-6 | `maribox auth set anthropic` |
| `openai` | gpt-4o, gpt-4o-mini | `maribox auth set openai` |
| `google` | gemini-2.5-pro, gemini-2.5-flash | `maribox auth set google` |
| `glm` | glm-4-plus, glm-4-flash | `maribox glm` |
| `custom` | Any OpenAI-compatible API | `maribox auth set custom` |

### Set an API key

```bash
maribox auth set anthropic
# Prompts: Enter API key for anthropic: **** (hidden input)
```

### Switch active provider

```bash
maribox auth use openai                  # Global switch
maribox auth use openai --model gpt-4o   # With specific model
maribox auth use glm --project           # Per-project only
```

### Rotate or revoke keys

```bash
maribox auth rotate anthropic    # Replace key (prompts for new one)
maribox auth revoke openai       # Delete stored key
```

### Check key status

```bash
maribox auth list
```

Output shows masked keys and status per provider.

---

## Session Workflow

Sessions are the core unit of work in maribox. Each session has its own directory with marimo kernel state and notebook data.

### Create a session

```bash
maribox session new --name "data-cleaning"
# Output: session_id: a1b2c3d4e5f6, status: running
```

Options:
- `--name` — human-readable name (auto-generated if omitted)
- `--provider` — override default AI provider for this session
- `--model` — override default AI model

### List sessions

```bash
maribox session list
```

Shows a table with session ID, name, status, provider, and creation time.

### Attach to a session (TUI)

```bash
maribox session attach a1b2c3d4e5f6
```

Opens the TUI connected to the session.

### Stop or kill sessions

```bash
maribox session stop a1b2c3d4e5f6    # Graceful shutdown
maribox session kill a1b2c3d4e5f6    # Force terminate (no cleanup)
```

### Snapshot a session

```bash
maribox session snapshot a1b2c3d4e5f6              # Save to default location
maribox session snapshot a1b2c3d4e5f6 --out ./backup.tar.gz  # Custom path
```

Saves the notebook source and execution logs.

### Remove a session

```bash
maribox session rm a1b2c3d4e5f6
```

Deletes the session directory.

---

## Notebook Authoring

### Add cells

```bash
# Simple cell
maribox cell add <session-id> --code "x = 42"

# Multi-line cell
maribox cell add <session-id> --code "
import pandas as pd
df = pd.read_csv('data.csv')
print(df.head())
"

# Insert after a specific cell
maribox cell add <session-id> --code "y = x + 1" --after cell_1
```

### Run cells

```bash
# Run a single cell
maribox cell run <session-id> --cell cell_2

# Run all cells in dependency order
maribox cell run <session-id> --all
```

### Edit cells

```bash
maribox cell edit <session-id> --cell cell_1 --code "x = 100"
```

Editing a cell marks dependent cells as stale (reactive DAG).

### Delete cells

```bash
maribox cell rm <session-id> --cell cell_3
```

### View and save the notebook

```bash
# Pretty-print with syntax highlighting
maribox notebook show <session-id>

# Save to default location (session directory)
maribox notebook save <session-id>

# Save to a custom path
maribox notebook save <session-id> --out ./analysis.py
```

The saved `.py` file is a standalone marimo notebook runnable with `marimo run analysis.py`.

---

## UI Generation

Use the UI agent to generate marimo interactive widgets from natural language descriptions.

```bash
# Generate a slider
maribox ui generate <session-id> --prompt "Add a slider for variable x ranging from 1 to 100"

# Generate a data table
maribox ui generate <session-id> --prompt "Show df as an interactive data table with sorting"

# Generate a chart
maribox ui generate <session-id> --prompt "Create a bar chart of sales by region"

# Generate a form
maribox ui generate <session-id> --prompt "Create a form with name, email, and submit button"
```

### Available marimo UI components

| Component | marimo API | Description |
|-----------|-----------|-------------|
| Text input | `mo.ui.text()` | Single-line text field |
| Slider | `mo.ui.slider()` | Numeric range slider |
| Dropdown | `mo.ui.dropdown()` | Select from options |
| Checkbox | `mo.ui.checkbox()` | Boolean toggle |
| Button | `mo.ui.button()` | Click action trigger |
| Table | `mo.ui.table()` | Interactive data table |
| Dataframe | `mo.ui.dataframe()` | Editable dataframe viewer |
| Plotly chart | `mo.ui.plotly()` | Interactive Plotly chart |
| Tabs | `mo.ui.tabs()` | Tabbed container |
| Accordion | `mo.ui.accordion()` | Collapsible sections |
| Horizontal stack | `mo.hstack()` | Side-by-side layout |
| Vertical stack | `mo.vstack()` | Stacked layout |

### Preview in browser

```bash
maribox ui preview <session-id>
```

Opens the marimo browser UI if the session is running with a non-headless kernel.

---

## Debugging

### View last error

```bash
maribox debug last <session-id>
```

Shows the most recent error with full traceback, the cell source code, and cell output.

### AI-powered fix

```bash
# Fix last error
maribox debug fix <session-id>

# Fix a specific cell
maribox debug fix <session-id> --cell cell_4
```

The debug agent analyzes the error, checks cell dependencies, and proposes a fix.

### Explain a cell

```bash
maribox debug explain <session-id> --cell cell_2
```

Shows the cell code, its status, outputs, and a natural language explanation.

---

## AI Agents

### List available agents

```bash
maribox agent list
```

Output:

```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Role         ┃ Provider  ┃ Model              ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ debug        │ openai    │ gpt-4o             │
│ notebook     │ anthropic │ claude-sonnet-4-6  │
│ orchestrator │ anthropic │ claude-sonnet-4-6  │
│ session      │ anthropic │ claude-sonnet-4-6  │
│ ui           │ google    │ gemini-2.5-pro     │
└──────────────┴───────────┴────────────────────┘
```

### Run an agent directly

```bash
maribox agent run notebook --prompt "Create a cell that loads a CSV and shows summary statistics" --session <session-id>
maribox agent run debug --prompt "Fix the NameError in cell_3" --session <session-id>
maribox agent run ui --prompt "Add a date picker widget" --session <session-id>
```

### How routing works

When you use the orchestrator (default), messages are routed by keyword analysis:

- **notebook**: "cell", "code", "write", "function", "import"
- **ui**: "widget", "component", "slider", "table", "chart", "form"
- **debug**: "error", "fix", "debug", "traceback", "exception"
- **session**: "session", "start", "stop", "environment"

---

## MCP Server Integration

maribox can run as an MCP server, exposing all commands as tools for AI assistants.

### Start the server

```bash
# stdio transport (for Claude Code, OpenCode)
maribox serve --mcp --transport stdio

# SSE transport (for HTTP clients, IDE extensions)
maribox serve --mcp --transport sse
```

### Claude Code configuration

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

### Available MCP tools (25 total)

| Category | Tools |
|----------|-------|
| Config | `config_get`, `config_set`, `config_list`, `config_init` |
| Auth | `auth_login`, `auth_logout`, `auth_status` |
| Session | `session_create`, `session_list`, `session_resume`, `session_kill`, `session_logs` |
| Notebook | `notebook_list_cells`, `notebook_create_cell`, `notebook_edit_cell`, `notebook_run_cell`, `notebook_run_all` |
| Debug | `debug_last_error`, `debug_propose_fix`, `debug_explain_cell`, `debug_dependencies` |
| Agent/UI | `agent_run`, `agent_list`, `ui_generate`, `ui_preview` |

### Example: Using with Claude Code

Once configured, Claude Code can directly:

```
> Create a new session called "sales-analysis"
> Add a cell that loads sales.csv and computes monthly totals
> Run all cells
> Debug any errors
> Generate a bar chart showing sales by month
> Save the notebook
```

---

## TUI (Terminal UI)

### Launch

```bash
maribox tui                          # Chat interface
maribox tui --session <session-id>   # Attached to a specific session
```

### Interface Layout

The TUI follows an OpenCode-style design:

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

### Components

**Messages List** — Scrollable message feed with user messages (blue border), assistant messages (purple border), tool call outputs (muted border), and a thinking indicator.

**Sidebar** (toggleable with `Ctrl+L`) — Shows session information (ID, status, provider, model), modified files list, and agent status.

**Input Bar** — Multi-line text area at the bottom. `Enter` sends the message. `\+Enter` inserts a newline. `Ctrl+E` opens an external editor.

**Status Bar** — Bottom row showing help hint, status messages, token usage, and current model name.

### Dialogs

| Dialog | Key | Description |
|--------|-----|-------------|
| Help | `Ctrl+?` | All key bindings in a modal overlay |
| Command Palette | `Ctrl+K` | Filterable command list |
| Session Switcher | `Ctrl+S` | Switch between conversations |
| Model Selector | `Ctrl+O` | Pick provider and model (← → to switch provider) |
| Quit | `Ctrl+C` | Confirmation dialog |

### Key bindings

| Key | Action |
|-----|--------|
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

### Message Types

- **User messages** — Displayed with a blue left border
- **Assistant messages** — Purple left border, shows model name, duration, and token count
- **Tool call messages** — Muted border, shows tool name, input/output, and status
- **System messages** — Used for session info and command results

---

## Configuration Reference

### Resolution order

1. `MARIBOX_HOME` environment variable
2. `.maribox/` directory (walks up from current directory)
3. `~/.config/maribox/` (OS default via platformdirs)

### Directory structure

```
.maribox/
├── config.toml           # Global settings
├── keys.enc              # Encrypted API keys (never commit this)
├── project.toml          # Per-project overrides
├── agents/
│   └── profiles.toml     # Per-agent model configuration
└── sessions/
    └── <session-id>/
        ├── meta.toml     # Session metadata
        ├── notebook.py   # Generated marimo notebook
        └── run.log       # Execution logs
```

### config.toml

```toml
[maribox]
version = "1"
default_provider = "anthropic"
default_model = "claude-sonnet-4-6"
auto_open_browser = false
log_level = "info"

[marimo]
port_range = [7000, 7100]
headless = true

[tui]
theme = "dark"
refresh_rate_ms = 250
show_agent_thoughts = true
```

### agents/profiles.toml

```toml
[orchestrator]
model = "claude-sonnet-4-6"
provider = "anthropic"

[notebook]
model = "claude-sonnet-4-6"
provider = "anthropic"

[ui]
model = "gemini-2.5-pro"
provider = "google"

[debug]
model = "gpt-4o"
provider = "openai"

[session]
model = "claude-sonnet-4-6"
provider = "anthropic"
```

---

## GLM 5.1 (Zhipu AI) Setup

maribox includes first-class support for GLM models from Zhipu AI.

### Quick setup

```bash
maribox glm --api-key YOUR_ZHIPU_API_KEY
```

This single command:
1. Stores your Zhipu API key
2. Sets GLM as the default provider
3. Sets `glm-4-plus` as the default model
4. Verifies the `zhipuai` SDK is installed

### Manual setup

```bash
maribox auth set glm
maribox auth use glm
maribox config set maribox.default_model glm-4-plus
```

### Using GLM for specific agents

In `.maribox/project.toml`:

```toml
[project]
provider = "glm"
model = "glm-4-plus"

[agents]
notebook = { model = "glm-4-plus", provider = "glm" }
debug = { model = "glm-4-flash", provider = "glm" }
```
