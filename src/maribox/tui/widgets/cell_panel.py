"""Cell panel widget — syntax-highlighted cell source display."""

from __future__ import annotations

from textual.widgets import Static


class CellPanel(Static):
    """Panel showing cell source code with syntax highlighting."""

    DEFAULT_CSS = """
    CellPanel {
        background: $surface;
        border: solid $primary-lighten-1;
        padding: 0 1;
        height: 1fr;
    }
    """

    def __init__(self, title: str = "Cell", code: str = "", **kwargs) -> None:
        self._title = title
        self._code = code
        content = self._render_content()
        super().__init__(content, **kwargs)

    def _render_content(self) -> str:
        if not self._code:
            return f"[bold]{self._title}[/bold]\n[dim]No cell selected[/dim]"
        return f"[bold]{self._title}[/bold]\n{self._code}"

    def update_code(self, code: str, title: str | None = None) -> None:
        """Update the displayed code."""
        self._code = code
        if title:
            self._title = title
        self.update(self._render_content())
