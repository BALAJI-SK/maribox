"""Chat screen — OpenCode-style main interface with messages, sidebar, and input."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from maribox.tui.message import ChatMessage, Conversation, MessageRole
from maribox.tui.widgets.messages_list import MessagesList
from maribox.tui.widgets.sidebar import Sidebar
from maribox.tui.widgets.input_bar import InputBar
from maribox.tui.widgets.status_bar import StatusBar
from maribox.tui.dialogs import (
    HelpScreen,
    SessionSwitcher,
    CommandPalette,
    ModelSelector,
    QuitDialog,
)


class ChatScreen(Screen):
    """Main chat interface — OpenCode-style layout.

    ┌──────────────────────────────────┬──────────────┐
    │     Messages List (left)         │   Sidebar    │
    │     (scrollable)                 │   (right)    │
    │                                  │   toggleable │
    ├──────────────────────────────────┴──────────────┤
    │ > Input area (textarea)                         │
    │   Enter to send · \\+Enter for newline           │
    └──────────────────────────────────────────────────┘
    │ Status bar: [help] [status] .... [tokens] [model]│
    """

    DEFAULT_CSS = """
    ChatScreen {
        layout: vertical;
    }

    #main-area {
        layout: horizontal;
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+question", "show_help", "Help", show=False),
        Binding("ctrl+h", "show_help", "Help", show=False),
        Binding("ctrl+k", "show_commands", "Commands", show=False),
        Binding("ctrl+l", "toggle_sidebar", "Sidebar", show=False),
        Binding("ctrl+s", "show_sessions", "Sessions", show=False),
        Binding("ctrl+o", "show_models", "Model", show=False),
        Binding("ctrl+n", "new_session", "New session", show=False),
        Binding("ctrl+c", "confirm_quit", "Quit", show=False),
        Binding("pageup", "scroll_up", "Scroll up", show=False),
        Binding("pagedown", "scroll_down", "Scroll down", show=False),
    ]

    def __init__(
        self,
        session_id: str | None = None,
        provider: str = "",
        model: str = "",
        **kwargs,
    ) -> None:
        self._session_id = session_id
        self._provider = provider
        self._model = model
        self._conversations: list[Conversation] = []
        self._active_conversation: Conversation | None = None
        self._thinking = False
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        # Main content area (messages + sidebar)
        with Horizontal(id="main-area"):
            yield MessagesList(
                cwd=os.getcwd(),
                provider=self._provider,
                model=self._model,
            )
            yield Sidebar()

        # Input bar
        yield InputBar()

        # Status bar
        yield StatusBar(model=self._model, provider=self._provider)

    def on_mount(self) -> None:
        """Initialize the UI on mount."""
        self._focus_input()

        # Create initial conversation if session_id provided
        if self._session_id:
            conv = Conversation(
                id=self._session_id,
                title="",
                model=self._model,
                provider=self._provider,
            )
            self._conversations.append(conv)
            self._active_conversation = conv

        # Update sidebar with agent info
        sidebar = self.query_one(Sidebar)
        sidebar.update_agents([
            {"name": "orchestrator", "model": self._model},
            {"name": "notebook", "model": self._model},
            {"name": "debug", "model": ""},
            {"name": "ui", "model": ""},
            {"name": "session", "model": self._model},
        ])

    # ── Message handling ─────────────────────────────────────────────

    def on_input_bar_submitted(self, event: InputBar.Submitted) -> None:
        """Handle message submission from the input bar."""
        text = event.text
        if not text:
            return

        # Ensure we have an active conversation
        if self._active_conversation is None:
            conv = Conversation(
                id=uuid.uuid4().hex[:12],
                model=self._model,
                provider=self._provider,
            )
            self._conversations.append(conv)
            self._active_conversation = conv

        # Add user message
        user_msg = ChatMessage(
            id=uuid.uuid4().hex[:8],
            role=MessageRole.USER,
            content=text,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self._active_conversation.add_message(user_msg)

        # Display user message
        messages_list = self.query_one(MessagesList)
        messages_list.add_message(user_msg)

        # Update status bar
        status = self.query_one(StatusBar)
        status.set_status("Thinking...", "info")

        # Show thinking indicator
        messages_list.show_thinking()
        self._thinking = True

        # Process the message (placeholder — in production this goes to the agent system)
        self._process_message(text)

        # Re-focus input
        self._focus_input()

    def _process_message(self, text: str) -> None:
        """Process a user message through the agent system.

        In production, this would invoke the OrchestratorAgent.
        For now, add a placeholder assistant response.
        """
        # Simulate a response
        import time
        start = time.monotonic()

        # Hide thinking
        messages_list = self.query_one(MessagesList)
        messages_list.hide_thinking()
        self._thinking = False

        # Create assistant response
        response_text = (
            f"Received your message. The agent system will process: [dim]{text[:100]}[/dim]\n\n"
            f"[dim]Note: Full agent integration is coming soon. "
            f"Use CLI commands for now: maribox session new, maribox cell add, etc.[/dim]"
        )
        duration_ms = (time.monotonic() - start) * 1000

        assistant_msg = ChatMessage(
            id=uuid.uuid4().hex[:8],
            role=MessageRole.ASSISTANT,
            content=response_text,
            timestamp=datetime.now(UTC).isoformat(),
            model=self._model,
            duration_ms=duration_ms,
            token_usage={"total": 0},
        )

        if self._active_conversation:
            self._active_conversation.add_message(assistant_msg)

        messages_list.add_message(assistant_msg)

        # Update status bar
        status = self.query_one(StatusBar)
        status.clear_status()

    # ── Action handlers ──────────────────────────────────────────────

    def action_show_help(self) -> None:
        """Show the help overlay."""
        self.app.push_screen(HelpScreen())

    def action_show_commands(self) -> None:
        """Show the command palette."""
        self.app.push_screen(CommandPalette(), self._on_command_selected)

    def action_toggle_sidebar(self) -> None:
        """Toggle the sidebar visibility."""
        sidebar = self.query_one(Sidebar)
        visible = sidebar.toggle()
        status = self.query_one(StatusBar)
        status.set_status("Sidebar: " + ("visible" if visible else "hidden"), "info")

    def action_show_sessions(self) -> None:
        """Show the session switcher."""
        self.app.push_screen(
            SessionSwitcher(self._conversations),
            self._on_session_selected,
        )

    def action_show_models(self) -> None:
        """Show the model selector."""
        self.app.push_screen(
            ModelSelector(current_model=self._model, current_provider=self._provider),
            self._on_model_selected,
        )

    def action_new_session(self) -> None:
        """Create a new conversation session."""
        conv = Conversation(
            id=uuid.uuid4().hex[:12],
            model=self._model,
            provider=self._provider,
        )
        self._conversations.append(conv)
        self._active_conversation = conv

        # Clear messages and show welcome
        messages_list = self.query_one(MessagesList)
        # Remove all message widgets
        for child in list(messages_list.children):
            if not getattr(child, "id", "") == "thinking-indicator":
                child.remove()

        # Re-add welcome
        from maribox.tui.widgets.welcome import WelcomeWidget
        indicator = messages_list.query_one("#thinking-indicator", Static)
        messages_list.mount(
            WelcomeWidget(
                cwd=os.getcwd(),
                provider=self._provider,
                model=self._model,
            ),
            before=indicator,
        )

        # Update sidebar
        sidebar = self.query_one(Sidebar)
        sidebar.update_session({
            "id": conv.id,
            "name": f"session-{conv.id[:8]}",
            "status": "running",
            "provider": self._provider,
            "model": self._model,
        })

        status = self.query_one(StatusBar)
        status.set_status(f"New session: {conv.id[:8]}", "info")

        self._focus_input()

    def action_confirm_quit(self) -> None:
        """Show quit confirmation dialog."""
        self.app.push_screen(QuitDialog(), self._on_quit_confirmed)

    def action_scroll_up(self) -> None:
        """Scroll messages up."""
        messages_list = self.query_one(MessagesList)
        messages_list.scroll_page_up()

    def action_scroll_down(self) -> None:
        """Scroll messages down."""
        messages_list = self.query_one(MessagesList)
        messages_list.scroll_page_down()

    # ── Dialog callbacks ─────────────────────────────────────────────

    def _on_command_selected(self, command: str | None) -> None:
        """Handle command palette selection."""
        if command is None:
            return

        status = self.query_one(StatusBar)
        status.set_status(f"Command: {command}", "info")

        # Dispatch commands
        if command == "new-session":
            self.action_new_session()
        elif command == "help":
            self.action_show_help()
        elif command == "clear":
            self._clear_conversation()
        elif command == "switch-session":
            self.action_show_sessions()
        elif command == "list-sessions":
            self._list_sessions()
        elif command == "compact":
            status.set_status("Conversation compacted", "info")
        else:
            status.set_status(f"Command '{command}' not yet implemented", "warn")

    def _on_session_selected(self, session_id: str | None) -> None:
        """Handle session switcher selection."""
        if session_id is None:
            return

        conv = next((c for c in self._conversations if c.id == session_id), None)
        if conv is None:
            return

        self._active_conversation = conv

        # Re-render messages for this conversation
        messages_list = self.query_one(MessagesList)
        # Remove all message widgets except thinking indicator
        for child in list(messages_list.children):
            if not getattr(child, "id", "") == "thinking-indicator":
                child.remove()

        if conv.messages:
            from maribox.tui.widgets.welcome import WelcomeWidget
            for msg in conv.messages:
                from maribox.tui.widgets.message_display import MessageWidget
                indicator = messages_list.query_one("#thinking-indicator", Static)
                messages_list.mount(MessageWidget(msg), before=indicator)
        else:
            from maribox.tui.widgets.welcome import WelcomeWidget
            indicator = messages_list.query_one("#thinking-indicator", Static)
            messages_list.mount(
                WelcomeWidget(
                    cwd=os.getcwd(),
                    provider=self._provider,
                    model=self._model,
                ),
                before=indicator,
            )

        status = self.query_one(StatusBar)
        status.set_status(f"Switched to session {session_id[:8]}", "info")

    def _on_model_selected(self, model: str | None) -> None:
        """Handle model selector selection."""
        if model is None:
            return

        self._model = model
        status = self.query_one(StatusBar)
        status.set_model(model, self._provider)
        status.set_status(f"Model: {model}", "info")

    def _on_quit_confirmed(self, confirmed: bool) -> None:
        """Handle quit confirmation."""
        if confirmed:
            self.app.exit()

    # ── Helpers ──────────────────────────────────────────────────────

    def _focus_input(self) -> None:
        """Focus the message input."""
        try:
            input_bar = self.query_one(InputBar)
            input_bar.focus_input()
        except Exception:
            pass

    def _clear_conversation(self) -> None:
        """Clear all messages from the current conversation."""
        if self._active_conversation:
            self._active_conversation.messages.clear()

        messages_list = self.query_one(MessagesList)
        for child in list(messages_list.children):
            if not getattr(child, "id", "") == "thinking-indicator":
                child.remove()

        from maribox.tui.widgets.welcome import WelcomeWidget
        indicator = messages_list.query_one("#thinking-indicator", Static)
        messages_list.mount(
            WelcomeWidget(
                cwd=os.getcwd(),
                provider=self._provider,
                model=self._model,
            ),
            before=indicator,
        )

        status = self.query_one(StatusBar)
        status.set_status("Conversation cleared", "info")

    def _list_sessions(self) -> None:
        """Show session list as assistant message."""
        if not self._conversations:
            return

        lines = ["[bold]Sessions:[/bold]"]
        for conv in self._conversations:
            active = " [dim]← active[/dim]" if conv == self._active_conversation else ""
            title = conv.title or f"Session {conv.id[:8]}"
            lines.append(f"  [cyan]{conv.id[:8]}[/cyan] {title} ({conv.message_count} msgs){active}")

        msg = ChatMessage(
            id=uuid.uuid4().hex[:8],
            role=MessageRole.SYSTEM,
            content="\n".join(lines),
            timestamp=datetime.now(UTC).isoformat(),
        )
        messages_list = self.query_one(MessagesList)
        messages_list.add_message(msg)
