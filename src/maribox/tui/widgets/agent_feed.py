"""Agent feed widget — scrollable log of agent messages."""

from __future__ import annotations

from textual.widgets import RichLog


class AgentFeed(RichLog):
    """Scrollable feed showing agent activity with color-coded messages."""

    DEFAULT_CSS = """
    AgentFeed {
        background: $surface;
        border: solid $accent;
        padding: 0 1;
        height: auto;
        max-height: 20;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(highlight=True, markup=True, **kwargs)

    def log_agent_message(self, agent_name: str, message: str) -> None:
        """Log a message from a specific agent with color coding."""
        colors = {
            "orchestrator": "cyan",
            "notebook": "green",
            "debug": "yellow",
            "ui": "magenta",
            "session": "blue",
        }
        color = colors.get(agent_name, "white")
        self.write(f"[{color}]{agent_name}[/{color}] — {message}")
