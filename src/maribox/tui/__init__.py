"""maribox TUI — Textual-based terminal user interface."""

from __future__ import annotations


def run_tui(session_id: str | None = None) -> None:
    """Launch the Textual TUI application."""
    from maribox.tui.app import MariboxApp

    app = MariboxApp(session_id=session_id)
    app.run()
