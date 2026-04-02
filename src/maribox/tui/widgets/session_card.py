"""Session card widget — displays session info in a compact card."""

from __future__ import annotations

from textual.widgets import Static


class SessionCard(Static):
    """A card showing session ID, name, and status."""

    DEFAULT_CSS = """
    SessionCard {
        background: $panel;
        border: round $primary;
        padding: 1 2;
        margin: 0 1;
        height: auto;
    }
    """

    def __init__(
        self,
        session_id: str,
        session_name: str = "",
        status: str = "unknown",
        **kwargs,
    ) -> None:
        self._session_id = session_id
        self._session_name = session_name
        self._status = status
        content = self._render_content()
        super().__init__(content, **kwargs)

    def _render_content(self) -> str:
        status_color = {
            "running": "green",
            "idle": "yellow",
            "error": "red",
            "stopped": "dim",
            "creating": "cyan",
        }.get(self._status, "white")
        return (
            f"[bold]{self._session_name or self._session_id}[/bold]\n"
            f"[dim]{self._session_id}[/dim]\n"
            f"[{status_color}]{self._status}[/{status_color}]"
        )
