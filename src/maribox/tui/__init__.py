"""maribox TUI — OpenCode-style terminal user interface for AI-assisted notebook development."""

from __future__ import annotations


def run_tui(session_id: str | None = None) -> None:
    """Launch the Textual TUI application."""
    from maribox.config.io import load_config
    from maribox.config.resolution import resolve_config_root
    from maribox.tui.app import MariboxApp

    # Load config for provider/model defaults
    provider = ""
    model = ""
    try:
        root = resolve_config_root()
        config = load_config(root)
        provider = config.maribox.default_provider
        model = config.maribox.default_model
    except Exception:
        pass

    app = MariboxApp(
        session_id=session_id,
        provider=provider,
        model=model,
    )
    app.run()
