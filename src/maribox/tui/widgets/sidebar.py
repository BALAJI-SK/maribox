"""Sidebar widget — session info, modified files, and context."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Sidebar(Vertical):
    """Right sidebar showing session context, files, and status."""

    DEFAULT_CSS = """
    Sidebar {
        width: 32;
        height: 1fr;
        background: $background-secondary;
        border-left: solid $border;
        padding: 1 1;
        display: none;
        overflow-y: auto;
        scrollbar-size: 1 1;
    }

    Sidebar.visible {
        display: block;
    }

    Sidebar .sidebar-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
        height: 1;
    }

    Sidebar .section-label {
        color: $text-secondary;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
        height: 1;
    }

    Sidebar .sidebar-item {
        color: $text;
        padding: 0 1;
        height: 1;
    }

    Sidebar .sidebar-item.dim {
        color: $text-muted;
    }

    Sidebar .session-status {
        height: 1;
    }

    Sidebar .session-status .status-dot {
        margin-right: 1;
    }

    Sidebar .session-status .status-running {
        color: $success;
    }

    Sidebar .session-status .status-idle {
        color: $warning;
    }

    Sidebar .session-status .status-stopped {
        color: $text-muted;
    }

    Sidebar .session-status .status-error {
        color: $error;
    }
    """

    def __init__(self, **kwargs) -> None:
        self._session_info: dict[str, Any] = {}
        self._files: list[dict[str, str]] = []
        self._agents: list[dict[str, str]] = []
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]Session[/bold cyan]", classes="sidebar-title")
        yield Static("", id="sidebar-session-info")
        yield Static("", classes="section-label", id="sidebar-files-label")
        yield Static("", id="sidebar-files-list")
        yield Static("[bold]Agents[/bold]", classes="section-label")
        yield Static("", id="sidebar-agents-list")

    def update_session(self, info: dict[str, Any]) -> None:
        """Update session information displayed in sidebar."""
        self._session_info = info
        self._render_session()

    def update_files(self, files: list[dict[str, str]]) -> None:
        """Update the modified files list."""
        self._files = files
        self._render_files()

    def update_agents(self, agents: list[dict[str, str]]) -> None:
        """Update the agents list."""
        self._agents = agents
        self._render_agents()

    def _render_session(self) -> None:
        try:
            widget = self.query_one("#sidebar-session-info", Static)
        except Exception:
            return

        info = self._session_info
        if not info:
            widget.update("[dim]No active session[/dim]")
            return

        status = info.get("status", "unknown")
        status_color = {
            "running": "green",
            "idle": "yellow",
            "stopped": "dim",
            "error": "red",
        }.get(status, "white")

        lines = [
            f"[cyan]{info.get('name', 'Unnamed')}[/cyan]",
            f"[dim]ID: {info.get('id', '-')}[/dim]",
            f"[{status_color}]● {status}[/{status_color}]",
        ]
        if info.get("provider"):
            lines.append(f"[dim]Provider: {info['provider']}[/dim]")
        if info.get("model"):
            lines.append(f"[dim]Model: {info['model']}[/dim]")
        widget.update("\n".join(lines))

    def _render_files(self) -> None:
        try:
            label = self.query_one("#sidebar-files-label", Static)
            widget = self.query_one("#sidebar-files-list", Static)
        except Exception:
            return

        if not self._files:
            label.update("")
            widget.update("")
            return

        label.update("[bold]Files[/bold]")
        lines = []
        for f in self._files[:10]:
            name = f.get("name", "?")
            status = f.get("status", "")
            if status == "modified":
                lines.append(f"  [yellow]M[/yellow] {name}")
            elif status == "added":
                lines.append(f"  [green]A[/green] {name}")
            elif status == "deleted":
                lines.append(f"  [red]D[/red] {name}")
            else:
                lines.append(f"  [dim]·[/dim] {name}")
        if len(self._files) > 10:
            lines.append(f"  [dim]... +{len(self._files) - 10} more[/dim]")
        widget.update("\n".join(lines))

    def _render_agents(self) -> None:
        try:
            widget = self.query_one("#sidebar-agents-list", Static)
        except Exception:
            return

        if not self._agents:
            widget.update("[dim]No agents configured[/dim]")
            return

        lines = []
        for agent in self._agents:
            name = agent.get("name", "?")
            model = agent.get("model", "")
            color = {
                "orchestrator": "cyan",
                "notebook": "green",
                "debug": "yellow",
                "ui": "magenta",
                "session": "blue",
            }.get(name, "white")
            lines.append(f"  [{color}]●[/{color}] {name} [dim]{model}[/dim]")
        widget.update("\n".join(lines))

    def toggle(self) -> bool:
        """Toggle sidebar visibility. Returns new visibility state."""
        if self.has_class("visible"):
            self.remove_class("visible")
            return False
        else:
            self.add_class("visible")
            return True

    @property
    def is_visible(self) -> bool:
        return self.has_class("visible")
