# Phase 9: Terminal User Interface

## Objective

Build an OpenCode-style chat-centric terminal user interface using Textual that provides a messages list, collapsible sidebar, multi-line input bar, status bar, and modal dialogs (help, command palette, session switcher, model selector, quit). The TUI targets 30fps responsiveness by using workers for async operations and debounced input.

## Files Created

- `src/maribox/tui/__init__.py` — `run_tui()` entry point
- `src/maribox/tui/app.py` — `MariboxApp` (Textual App)
- `src/maribox/tui/styles.py` — Theme colors and CSS constants
- `src/maribox/tui/styles.tcss` — Textual CSS theme file
- `src/maribox/tui/message.py` — `ChatMessage`, `Conversation`, `MessageRole` data models
- `src/maribox/tui/screens/__init__.py` — re-exports `ChatScreen`
- `src/maribox/tui/screens/chat.py` — `ChatScreen` (main interface)
- `src/maribox/tui/widgets/__init__.py` — re-exports all widgets
- `src/maribox/tui/widgets/messages_list.py` — scrollable message list with auto-scroll
- `src/maribox/tui/widgets/message_display.py` — single message renderer (user/assistant/tool)
- `src/maribox/tui/widgets/sidebar.py` — right sidebar (session info, files, agents)
- `src/maribox/tui/widgets/input_bar.py` — multi-line input with Enter-send, \+Enter-newline
- `src/maribox/tui/widgets/status_bar.py` — bottom status bar (model, tokens, status)
- `src/maribox/tui/widgets/welcome.py` — welcome screen when no messages
- `src/maribox/tui/dialogs/__init__.py` — re-exports all dialogs
- `src/maribox/tui/dialogs/help_dialog.py` — help overlay with key bindings
- `src/maribox/tui/dialogs/session_switcher.py` — session switching modal
- `src/maribox/tui/dialogs/command_palette.py` — filterable command palette
- `src/maribox/tui/dialogs/model_selector.py` — provider/model selection
- `src/maribox/tui/dialogs/quit_dialog.py` — quit confirmation

## Layout

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

The sidebar is hidden by default and toggled with `Ctrl+L`.

## Key Interfaces

### `app.py`

```python
class MariboxApp(App):
    TITLE = "maribox"
    CSS_PATH = "styles.tcss"

    def __init__(self, session_id: str | None = None, provider: str = "", model: str = "") -> None: ...

    def compose(self) -> ComposeResult:
        yield ChatScreen(...)

    def on_mount(self) -> None:
        self.dark = True
```

### `screens/chat.py`

```python
class ChatScreen(Screen):
    """Main chat interface — OpenCode-style layout."""

    BINDINGS = [
        Binding("ctrl+question", "show_help", ...),
        Binding("ctrl+k", "show_commands", ...),
        Binding("ctrl+l", "toggle_sidebar", ...),
        Binding("ctrl+s", "show_sessions", ...),
        Binding("ctrl+o", "show_models", ...),
        Binding("ctrl+n", "new_session", ...),
        Binding("ctrl+c", "confirm_quit", ...),
    ]

    def compose(self) -> ComposeResult:
        # Main area (messages + sidebar)
        with Horizontal(id="main-area"):
            yield MessagesList(...)
            yield Sidebar()
        # Input bar
        yield InputBar()
        # Status bar
        yield StatusBar(...)

    def on_input_bar_submitted(self, event) -> None:
        """Handle message submission from the input bar."""
        ...

    def _process_message(self, text: str) -> None:
        """Process a user message through the agent system."""
        ...
```

### `widgets/messages_list.py`

```python
class MessagesList(VerticalScroll):
    """Scrollable list of chat messages with auto-scroll."""

    def add_message(self, message: ChatMessage) -> MessageWidget: ...
    def show_thinking(self) -> None: ...
    def hide_thinking(self) -> None: ...
    def update_last_assistant(self, content: str) -> None: ...
```

### `widgets/input_bar.py`

```python
class InputBar(Vertical):
    """Bottom input area with prompt indicator and text area."""

    class Submitted(Message):
        def __init__(self, text: str) -> None: ...

    def on_key(self, event: events.Key) -> None:
        """Enter = send, \\+Enter = newline."""
        ...

    def focus_input(self) -> None: ...
```

### `widgets/sidebar.py`

```python
class Sidebar(Vertical):
    """Right sidebar showing session context, files, and status."""

    def update_session(self, info: dict) -> None: ...
    def update_files(self, files: list[dict]) -> None: ...
    def update_agents(self, agents: list[dict]) -> None: ...
    def toggle(self) -> bool: ...
```

### `widgets/status_bar.py`

```python
class StatusBar(Horizontal):
    """Bottom status bar showing model, tokens, and status messages."""

    def set_model(self, model: str, provider: str = "") -> None: ...
    def set_tokens(self, total: int, cost: str = "") -> None: ...
    def set_status(self, text: str, msg_type: str = "info") -> None: ...
```

## Key Bindings

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

## Dialogs

All dialogs use `ModalScreen` and are centered overlays:

- **HelpScreen** — Multi-column key binding reference
- **SessionSwitcher** — Scrollable session list with j/k navigation
- **CommandPalette** — Filterable command list with text input
- **ModelSelector** — Per-provider model list with ← → provider switching
- **QuitDialog** — Yes/No confirmation

## Testing Strategy

- **Textual pilot tests**: Use `app.run_test()` with `Pilot` to simulate key presses and verify screen transitions.
- **Widget unit tests**: Test `MessageWidget`, `Sidebar`, `InputBar` with mock data.
- **Dialog tests**: Test modal screen interactions (selection, cancellation).
- **Integration tests**: Full app lifecycle: mount → type message → submit → verify response → quit.
- **Performance tests**: Measure rendering time for message list with 100 messages.

## Acceptance Criteria

- [x] `maribox tui` launches the Textual application and shows the chat interface
- [x] Chat interface shows welcome screen, messages list, input bar, and status bar
- [x] Messages are displayed with role-appropriate styling (user/assistant/tool)
- [x] Input bar supports multi-line input with Enter-send and \+Enter-newline
- [x] Sidebar toggles with Ctrl+L showing session info, files, and agents
- [x] Command palette opens with Ctrl+K with filtering
- [x] Model selector opens with Ctrl+O with provider switching
- [x] Session switcher opens with Ctrl+S
- [x] Help overlay shows all key bindings
- [x] Status bar shows model name and status messages
- [x] All dialogs respond within 33ms (30fps target)
- [x] TUI works on terminals with at least 80x24 dimensions
