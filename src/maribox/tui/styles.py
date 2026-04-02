"""TUI styles — CSS constants for the Textual app."""

DARK_THEME = """
Screen {
    background: $surface;
}

Header {
    background: $primary;
}

Footer {
    background: $primary-background;
}

SessionCard {
    background: $panel;
    border: round $primary;
    padding: 1 2;
    margin: 1;
}

CellPanel {
    background: $surface;
    border: solid $primary-lighten-1;
    padding: 0 1;
}

AgentFeed {
    background: $surface;
    border: solid $accent;
    padding: 0 1;
    height: auto;
    max-height: 20;
}
"""
