# Phase 7: CLI Commands

## Objective

Implement the remaining CLI commands that expose the sandbox, notebook, and agent systems to the user. This phase also optimizes CLI startup time to under 500ms through lazy imports, and establishes a consistent output pattern using Rich for formatted terminal output with streaming support for agent responses.

## Files to Create

- `src/maribox/commands/ui.py` — UI generation commands
- `src/maribox/commands/debug.py` — debugging commands
- `src/maribox/commands/agent.py` — agent invocation commands

## Files to Modify

- `src/maribox/cli.py` — add lazy imports, register all new subcommands, optimize startup
- `src/maribox/commands/__init__.py` — update re-exports

## Key Interfaces

### `commands/ui.py`

```python
async def ui_generate(
    description: str,
    agent: Optional[str] = None,
    output: Optional[Path] = None,
    preview: bool = False,
) -> None:
    """
    Generate a Marimo UI component from a natural language description.

    Flow:
    1. Load config and resolve agent profile (default: "ui")
    2. Construct UiAgent with the description as context
    3. Stream the agent's response with Rich spinner -> stream -> Rich table
    4. Write generated code to output file or stdout
    5. If preview=True, open the generated component in the default browser

    Output pattern:
    - Start: Rich spinner "Generating UI component..."
    - Stream: Incrementally render the agent's streamed text response
    - Done: Rich table showing the generated component metadata
    """

async def ui_preview(file_path: Path) -> None:
    """
    Open a generated UI component file in Marimo for live preview.

    Flow:
    1. Validate the file exists and contains valid Marimo code
    2. Start a sandbox with Marimo running the file
    3. Open the sandbox URL in the default browser
    4. Print the URL to stdout for manual access
    """

async def ui_list_components() -> None:
    """Print a Rich table of available Marimo UI component categories."""
```

### `commands/debug.py`

```python
async def debug_last(
    session_id: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """
    Show the most recent error from a session.

    Flow:
    1. Resolve session (last active if session_id not specified)
    2. Load run.log and find the last error entry
    3. Display with Rich:
       - Error traceback in a panel with syntax highlighting
       - Cell ID and code that caused the error
       - Variables in scope at the time of error (if verbose)
       - Suggestions from DebugAgent (optional, --suggest flag)

    Output:
    - Rich panel with red border for errors
    - Syntax-highlighted traceback
    - Optional: agent suggestions in a separate panel
    """

async def debug_fix(
    session_id: Optional[str] = None,
    cell_id: Optional[str] = None,
    auto_apply: bool = False,
) -> None:
    """
    Ask the DebugAgent to propose a fix for the last error.

    Flow:
    1. Collect error context (traceback, cell code, related cells)
    2. Invoke DebugAgent with the error context
    3. Display the proposed fix:
       - Diff view showing old code vs. new code (Rich syntax)
       - Explanation of the fix
       - Confirmation prompt (unless --auto-apply)
    4. If confirmed, apply the fix via NotebookAgent and re-run the cell

    Output pattern:
    - Rich spinner "Analyzing error..."
    - Stream: incremental display of fix explanation
    - Done: Rich diff panel + confirmation prompt
    """

async def debug_explain(
    cell_id: Optional[str] = None,
    session_id: Optional[str] = None,
    depth: str = "medium",             # brief | medium | detailed
) -> None:
    """
    Explain a notebook cell's code in natural language.

    Flow:
    1. Load the cell's code from the session
    2. If cell_id not specified, use the last modified cell
    3. Invoke NotebookAgent with the "explain" intent
    4. Display the explanation with Rich markdown rendering

    Output:
    - Rich markdown panel with the explanation
    - Optional: dependency graph visualization (ASCII art)
    """
```

### `commands/agent.py`

```python
async def agent_run(
    message: str,
    agent: Optional[str] = None,
    session_id: Optional[str] = None,
    stream: bool = True,
) -> None:
    """
    Send a message to an agent and display the response.

    Flow:
    1. Resolve the agent (default: orchestrator for auto-routing)
    2. Load session context if session_id is provided
    3. If stream=True: Rich spinner -> stream chunks -> final Rich table
    4. If stream=False: Rich spinner -> wait -> Rich table
    5. Display any tool calls the agent made in a secondary panel

    Output pattern:
    - Rich spinner "[agent_name] is thinking..."
    - Stream: Live.update() with incremental text
    - Done: Rich table with response summary, tokens used, duration
    """

async def agent_list() -> None:
    """Print a Rich table of available agents and their descriptions."""
```

### Modifications to `cli.py`

```python
# Lazy import pattern for sub-500ms startup:
#
# BEFORE (slow - imports everything at module level):
#   from maribox.commands.session import session_create
#   from maribox.commands.ui import ui_generate
#   ...
#
# AFTER (fast - imports only when the command is invoked):
#   @click.command()
#   def create():
#       """Create a new session."""
#       import asyncio
#       from maribox.commands.session import session_create
#       asyncio.run(session_create())

# In cli.py:

@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Maribox - AI-powered Marimo notebook environment."""

# --- Session commands (already registered but update imports) ---
@cli.group()
def session() -> None:
    """Manage sandbox sessions."""
    pass

@session.command()
@click.option("--name", "-n", help="Session name")
def create(name: Optional[str]) -> None:
    """Create a new sandbox session."""
    import asyncio
    from maribox.commands.session import session_create
    asyncio.run(session_create(name))

# --- UI commands ---
@cli.group()
def ui() -> None:
    """Generate and preview UI components."""
    pass

@ui.command()
@click.argument("description")
@click.option("--agent", "-a", help="Agent profile to use")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--preview", "-p", is_flag=True, help="Open in browser after generation")
def generate(description: str, agent: Optional[str], output: Optional[str], preview: bool) -> None:
    """Generate a UI component from a description."""
    import asyncio
    from maribox.commands.ui import ui_generate
    asyncio.run(ui_generate(description, agent, output, preview))

# --- Debug commands ---
@cli.group()
def debug() -> None:
    """Debug notebook errors."""
    pass

@debug.command("last")
@click.option("--session-id", "-s", help="Session ID")
@click.option("--verbose", "-v", is_flag=True)
def debug_last_cmd(session_id: Optional[str], verbose: bool) -> None:
    """Show the most recent error."""
    import asyncio
    from maribox.commands.debug import debug_last
    asyncio.run(debug_last(session_id, verbose))

# --- Agent commands ---
@cli.group()
def agent() -> None:
    """Interact with AI agents."""
    pass

@agent.command("run")
@click.argument("message")
@click.option("--agent", "-a", help="Agent to use")
@click.option("--session-id", "-s", help="Session context")
@click.option("--no-stream", is_flag=True, help="Disable streaming")
def agent_run_cmd(message: str, agent: Optional[str], session_id: Optional[str], no_stream: bool) -> None:
    """Send a message to an AI agent."""
    import asyncio
    from maribox.commands.agent import agent_run
    asyncio.run(agent_run(message, agent, session_id, stream=not no_stream))

# Helper for streaming output pattern
class StreamingOutput:
    """
    Consistent streaming output pattern used across all commands:
    1. Rich spinner with status message
    2. Live update with incremental text
    3. Final Rich table with summary

    Usage:
        async with StreamingOutput("Generating...") as out:
            async for chunk in agent.stream(message):
                out.update(chunk)
            out.finish(table_data)
    """
```

## Dependencies

- **Phase 4 (Sandbox)** must be complete: session commands use `SessionManager`.
- **Phase 5 (Notebook)** must be complete: debug commands access `CellDAG` and cell data.
- **Phase 6 (Agents)** must be complete: all agent commands construct and invoke agents.
- Runtime packages: `click` (CLI framework), `rich` (terminal formatting), `textual` (not yet, Phase 9).

## Testing Strategy

- **CLI invocation tests**: Use `click.testing.CliRunner` to invoke each command in isolation. Verify exit codes, output text, and error messages.
- **Lazy import verification**: Profile startup time with `python -c "import maribox.cli"` and assert < 500ms. Use `time.time()` measurements in a dedicated test.
- **Streaming output tests**: Mock the agent stream and verify that `StreamingOutput` produces the correct Rich renderable sequence.
- **Debug command tests**: Provide a session with a known error in `run.log`. Verify `debug_last` displays the traceback and cell code.
- **Debug fix tests**: Mock `DebugAgent.invoke()` to return a known fix. Verify the diff display and the apply/discard logic.
- **UI generate tests**: Mock `UiAgent.invoke()` to return generated code. Verify file output and browser preview trigger.
- **Agent run tests**: Mock `OrchestratorAgent.stream()` and verify streaming output chunks.
- **Edge cases**: No active session, session in ERROR state, agent returns empty response, agent returns error, malformed cell ID.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Lazy imports still too slow | CLI startup exceeds 500ms target | Profile with `python -X importtime`; defer heavy imports (httpx, websockets, docker) behind the command function; use `importlib.util.find_module()` to check availability without importing |
| Rich streaming stutters on slow LLM responses | Poor UX with visible pauses | Buffer chunks for 50ms before rendering; use Rich Live with auto-refresh; show a pulsing spinner between chunks |
| Click async commands are awkward | Mixing sync Click with async handlers | Use a single `asyncio.run()` wrapper per command; avoid any sync code inside the async handler |
| Debug fix applies wrong code | Breaks user's notebook | Always show a diff and require confirmation unless `--auto-apply` is explicitly set; create a backup of the cell before applying |
| Browser preview fails on headless systems | `ui_preview` crashes | Catch `webbrowser.open()` errors; fall back to printing the URL |
| Multiple debug commands access same session | Race condition on run.log | Acquire a file lock before reading run.log; release after display |

## Acceptance Criteria

- [ ] `maribox ui generate <description>` streams agent output and writes a UI component file
- [ ] `maribox ui preview <file>` opens a browser pointing to a sandbox running the file
- [ ] `maribox debug last` shows the most recent error with traceback and cell context
- [ ] `maribox debug fix` proposes and optionally applies a code fix with diff display
- [ ] `maribox debug explain <cell>` provides a natural language explanation of cell code
- [ ] `maribox agent run <message>` streams an agent response to the terminal
- [ ] `maribox agent list` shows available agents in a Rich table
- [ ] All commands use lazy imports; `import maribox.cli` completes in < 500ms
- [ ] Streaming output pattern is consistent: spinner -> stream -> table
- [ ] All commands exit with code 0 on success, 1 on error, 2 on usage error
- [ ] Error messages are user-friendly (no raw tracebacks for expected failures)
- [ ] Unit test coverage >= 80% for all command modules
