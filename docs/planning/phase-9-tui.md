# Phase 9: Terminal User Interface

## Objective

Build a rich, interactive terminal user interface using Textual that provides a dashboard view of all sessions, a three-pane session inspector with keyboard-driven navigation, an agent activity monitor, and a configuration editor with live TOML validation. The TUI targets 30fps responsiveness by using `set_interval` for polling, debounce for user input, workers for async operations, and a ring buffer for log rendering.

## Files to Create

- `src/maribox/tui/__init__.py` — re-exports `MariboxApp`
- `src/maribox/tui/app.py` — main Textual application
- `src/maribox/tui/screens/__init__.py` — re-exports all screens
- `src/maribox/tui/screens/dashboard.py` — session dashboard grid view
- `src/maribox/tui/screens/session_view.py` — three-pane session inspector
- `src/maribox/tui/screens/agent_monitor.py` — agent activity log
- `src/maribox/tui/screens/auth_manager.py` — credential management
- `src/maribox/tui/screens/config_editor.py` — TOML configuration editor
- `src/maribox/tui/widgets/__init__.py` — re-exports all widgets
- `src/maribox/tui/widgets/session_card.py` — session summary card widget
- `src/maribox/tui/widgets/cell_panel.py` — cell code and output display
- `src/maribox/tui/widgets/agent_feed.py` — scrolling agent message feed
- `src/maribox/tui/widgets/status_bar.py` — global status bar
- `src/maribox/tui/styles.py` — status formatting and color definitions

## Key Interfaces

### `app.py`

```python
from textual.app import App, ComposeResult
from textual.binding import Binding

class MariboxApp(App):
    """
    Main TUI application for Maribox.
    Extends textual.App with Maribox-specific screens, bindings, and services.
    """

    TITLE = "Maribox"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("d", "switch_screen('dashboard')", "Dashboard", show=True),
        Binding("a", "switch_screen('agent_monitor')", "Agents", show=True),
        Binding("c", "switch_screen('config_editor')", "Config", show=True),
        Binding("?", "help", "Help", show=True, key_display="?"),
    ]

    def __init__(self, config_root: Optional[Path] = None) -> None:
        """
        Initialize the TUI app.
        Constructs the shared services:
        - AuthManager
        - SessionManager
        - OrchestratorAgent
        - Config state
        """
        ...

    def compose(self) -> ComposeResult:
        """
        Compose the root layout.
        Returns the StatusBar widget (always visible at bottom).
        Screens are mounted on top as the user navigates.
        """

    def on_mount(self) -> None:
        """
        Called when the app is mounted.
        - Install the dashboard as the default screen
        - Start the background polling interval (30fps = ~33ms)
        - Initialize async workers for session health checks
        """

    def action_quit(self) -> None:
        """Gracefully shut down all services before quitting."""
```

### `screens/dashboard.py`

```python
from textual.screen import Screen
from textual.containers import Grid
from textual.widgets import Header, Footer

class DashboardScreen(Screen):
    """
    Grid view of all active and recent sessions.
    Each session is represented by a SessionCard widget.

    Layout:
    - Header with app title and global status
    - Scrollable grid of SessionCard widgets (responsive columns)
    - Footer with keybinding hints

    Keybindings:
    - Enter: open selected session in SessionViewScreen
    - n: create new session
    - r: refresh session list
    - k: kill selected session (with confirmation)
    - /: filter sessions by name
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Grid(
            *[SessionCard(session) for session in self.app.session_manager.list_sessions()],
            id="session-grid",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up periodic refresh (every 2 seconds) via set_interval."""
        self.set_interval(2.0, self.refresh_sessions)

    async def refresh_sessions(self) -> None:
        """Poll session states and update the grid."""

    def on_session_card_selected(self, event: SessionCard.Selected) -> None:
        """Navigate to SessionViewScreen for the selected session."""
```

### `screens/session_view.py`

```
class SessionViewScreen(Screen):
    """
    Three-pane session inspector with keybindings from requirements section 7.2.

    Layout (three vertical panes):
    +------------------------------------------+
    | Left: Cell list       | Right top: Code  |
    | (scrollable list of   | (syntax-         |
    |  cell names + status) | highlighted      |
    |                       | cell code)       |
    |                       |------------------|
    |                       | Right bottom:    |
    |                       | Cell output /    |
    |                       | agent feed       |
    +------------------------------------------+
    | Status bar                              |
    +------------------------------------------+

    Keybindings (from requirements 7.2):
    - j/k or Arrow Up/Down: navigate cells
    - Enter: run selected cell
    - Shift+Enter: run all cells
    - e: edit cell (opens inline editor)
    - d: delete cell (with confirmation)
    - x: debug cell (opens DebugAgent panel)
    - a: ask agent about cell
    - Tab: switch focus between panes
    - Esc: back to dashboard
    - 1-9: jump to cell by position
    """

    def __init__(self, session_id: str) -> None: ...

    def compose(self) -> ComposeResult:
        """Compose the three-pane layout with CellList, CodePanel, and OutputPanel."""
        ...

    def on_mount(self) -> None:
        """Load session data and set up polling."""
        self.set_interval(1.0, self.poll_session_state)

    async def poll_session_state(self) -> None:
        """Refresh cell statuses without full re-render (debounced)."""

    def action_run_cell(self) -> None:
        """Run the currently selected cell in a background worker."""

    def action_edit_cell(self) -> None:
        """Open an inline text editor for the selected cell's code."""

    def action_debug_cell(self) -> None:
        """Invoke the DebugAgent for the selected cell."""
```

### `screens/agent_monitor.py`

```python
class AgentMonitorScreen(Screen):
    """
    Real-time display of agent activity using RichLog.

    Layout:
    - RichLog widget showing agent messages, tool calls, and responses
    - Filter bar to show only specific agents
    - Input bar for sending messages to agents

    The RichLog uses a ring buffer (max 10,000 entries) to prevent
    unbounded memory growth during long sessions.
    """

    RING_BUFFER_SIZE = 10_000

    def compose(self) -> ComposeResult:
        """Compose the agent monitor layout."""
        ...

    def on_mount(self) -> None:
        """Subscribe to agent event stream."""
        ...

    def add_agent_event(self, event: AgentEvent) -> None:
        """
        Add an agent event to the RichLog.
        Respects the ring buffer limit by evicting oldest entries.
        Formats the event with appropriate Rich styling:
        - User messages: bold white
        - Agent responses: cyan
        - Tool calls: yellow
        - Errors: red
        """
```

### `screens/auth_manager.py`

```python
class AuthManagerScreen(Screen):
    """
    Credential management screen.

    Layout:
    - Table of stored keys (provider, backend, date added)
    - Login form: provider dropdown, API key input (masked), submit button
    - Logout button for selected provider

    Security:
    - API key input field uses password masking
    - Keys are never displayed in the TUI
    - Status messages use log_mask for safety
    """
```

### `screens/config_editor.py`

```python
class ConfigEditorScreen(Screen):
    """
    TOML configuration editor with live validation.

    Layout:
    - Left: TOML text editor (TextArea widget)
    - Right: validation status panel
    - Bottom: save / reset buttons

    Features:
    - Syntax highlighting for TOML
    - Live validation on every keystroke (debounced at 300ms)
    - Error markers on invalid lines
    - Save writes to the correct config file (project or user level)
    - Reset reverts to the last saved state
    """

    DEBOUNCE_MS = 300

    def compose(self) -> ComposeResult: ...

    def on_mount(self) -> None:
        """Load current config as TOML text and start debounce timer."""

    async def validate_toml(self, text: str) -> List[Tuple[int, str]]:
        """
        Validate TOML text and return a list of (line_number, error_message).
        Returns empty list if valid.
        Uses tomllib for parsing and schema.py for structural validation.
        """
```

### Widgets

```python
# widgets/session_card.py
class SessionCard(Static):
    """
    A card widget displaying session summary:
    - Session name and ID (truncated)
    - Status badge (color-coded: green=active, yellow=idle, red=error, gray=stopped)
    - Uptime or time since last activity
    - Cell count and error count
    Emits Selected event on click or Enter.
    """

    class Selected(Message):
        def __init__(self, session_id: str) -> None: ...

# widgets/cell_panel.py
class CellPanel(Static):
    """
    Displays a single cell's code and output.
    - Syntax-highlighted code area
    - Collapsible output area
    - Status indicator (pending, running, success, error, stale)
    """

# widgets/agent_feed.py
class AgentFeed(Static):
    """
    Scrolling feed of agent messages within a session view.
    Uses a ring buffer for the last 1,000 messages.
    Auto-scrolls to the bottom unless the user has scrolled up.
    """

# widgets/status_bar.py
class StatusBar(Widget):
    """
    Global status bar displayed at the bottom of the app.
    Shows:
    - Current screen name
    - Active session count
    - Agent status (idle/thinking)
    - Config root path
    - Time
    """

# styles.py
def format_status(status: CellStatus) -> Text:
    """Format a CellStatus as a Rich Text object with appropriate color."""
    # PENDING -> dim, RUNNING -> yellow animated, SUCCESS -> green,
    # ERROR -> red, STALE -> orange, DISABLED -> gray

def format_session_state(state: SessionState) -> Text:
    """Format a SessionState as a Rich Text object with appropriate color."""

THEME = {
    "background": "#1e1e2e",
    "surface": "#313244",
    "primary": "#89b4fa",
    "success": "#a6e3a1",
    "warning": "#f9e2af",
    "error": "#f38ba8",
    "text": "#cdd6f4",
    "dim": "#6c7086",
}
```

## Dependencies

- **Phase 7 (CLI Commands)** must be complete: the TUI reuses the same underlying functions and services that the CLI commands use.
- Runtime packages: `textual` (TUI framework, >=0.40), `rich` (terminal formatting, used by Textual), `tomllib` / `tomli_w` (config editor validation).

## Testing Strategy

- **Textual snapshot tests**: Use `textual.testing.SnapshotTest` to verify screen layouts match expected snapshots. Run with `pytest --snapshot-update` to regenerate.
- **Pilot tests**: Use `app.run_test()` with `Pilot` to simulate key presses and verify screen transitions, widget updates, and action dispatching.
- **Unit tests for widgets**: Test `SessionCard` with mock session data. Test `CellPanel` with mock cell data. Verify formatting functions in `styles.py`.
- **Unit tests for config editor validation**: Feed valid and invalid TOML to `validate_toml()` and verify error line numbers.
- **Unit tests for ring buffer**: Fill `AgentFeed` beyond the buffer limit and verify oldest entries are evicted.
- **Worker tests**: Test that async operations (session create, cell run) execute in workers and update the UI on completion.
- **Debounce tests**: Verify that rapid keypresses in the config editor trigger validation only after the debounce period.
- **Integration tests**: Full app lifecycle: mount -> navigate screens -> interact with session -> quit. Verify clean shutdown of all services.
- **Performance tests**: Measure rendering time for dashboard with 20 sessions; verify < 33ms per frame.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Textual version incompatibility | Layout breaks or APIs change | Pin Textual version; test against specific version in CI; use `CSS_PATH` for styling instead of inline CSS |
| 30fps target not met on slow terminals | Stuttery UI, poor UX | Use `set_interval` only for essential polling; debounce all user input; offload heavy work to workers; use `RichLog` with ring buffer instead of rebuilding entire log |
| Ring buffer causes visual glitches | Log entries disappear unexpectedly | Only evict entries above the buffer limit; keep a "scroll lock" mode where eviction pauses if user has scrolled up |
| Config editor allows saving invalid TOML | Maribox config is corrupted | Block save button when validation errors exist; always validate before write; maintain a backup of the previous config |
| Large notebook with many cells overwhelms the session view | Slow rendering, high memory | Virtualize the cell list (only render visible cells); paginate the code panel |
| WebSocket disconnections during TUI session | Agent feed goes stale | Show a "reconnecting" indicator; auto-reconnect with exponential backoff; cache last known state |
| Color theme conflicts with terminal themes | Unreadable text on light/dark backgrounds | Use Textual's built-in dark/light mode detection; provide both themes in `THEME`; allow user override in config |

## Acceptance Criteria

- [ ] `maribox tui` launches the Textual application and shows the dashboard
- [ ] Dashboard displays all sessions in a responsive grid with SessionCard widgets
- [ ] Pressing Enter on a session opens the SessionViewScreen with three panes
- [ ] SessionViewScreen shows cell list, code, and output with correct keybindings
- [ ] Cell navigation with j/k, cell execution with Enter, editing with e all work
- [ ] AgentMonitorScreen displays agent messages with color-coded formatting
- [ ] AuthManagerScreen allows login/logout without displaying raw API keys
- [ ] ConfigEditorScreen validates TOML on every keystroke (debounced at 300ms)
- [ ] StatusBar shows current screen, session count, and agent status
- [ ] All screens respond within 33ms (30fps target)
- [ ] Ring buffer limits AgentFeed to 1,000 entries and RichLog to 10,000 entries
- [ ] Graceful shutdown cleans up all services (sandboxes, connections, workers)
- [ ] TUI works on terminals with at least 80x24 dimensions
- [ ] Both dark and light terminal themes are supported
- [ ] Unit test coverage >= 70% for `tui/` package (acknowledging TUI testing limitations)
