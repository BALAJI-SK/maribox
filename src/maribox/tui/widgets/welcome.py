"""Welcome widget — displayed when no conversation is active."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from maribox import __version__


class WelcomeWidget(Vertical):
    """Welcome screen shown when there are no messages."""

    DEFAULT_CSS = """
    WelcomeWidget {
        padding: 4 6;
        height: auto;
        margin: 2 4;
    }
    """

    def __init__(
        self,
        cwd: str = "",
        provider: str = "",
        model: str = "",
        **kwargs,
    ) -> None:
        self._cwd = cwd
        self._provider = provider
        self._model = model
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Static(f"[bold cyan]⌬ maribox[/bold cyan] [dim]v{__version__}[/dim]", classes="logo")
        yield Static("[dim]Multi-session marimo notebook orchestrator with AI agents[/dim]", classes="version")
        if self._cwd:
            yield Static(f"[dim]cwd:[/dim] {self._cwd}", classes="cwd-info")
        if self._provider:
            yield Static(f"[dim]provider:[/dim] {self._provider}  [dim]model:[/dim] {self._model}", classes="provider-info")
        yield Static("", classes="help-keys")
        yield Static(
            "[dim]─────────────────────────────────────[/dim]\n"
            "[bold]Key bindings[/bold]\n"
            "[cyan]Enter[/cyan]      Send message\n"
            "[cyan]\\\\+Enter[/cyan]   New line in input\n"
            "[cyan]Ctrl+K[/cyan]     Command palette\n"
            "[cyan]Ctrl+L[/cyan]     Toggle sidebar\n"
            "[cyan]Ctrl+O[/cyan]     Model selector\n"
            "[cyan]Ctrl+?[/cyan]     Help\n"
            "[cyan]Ctrl+N[/cyan]     New session\n"
            "[cyan]Ctrl+S[/cyan]     Session switcher\n"
            "[cyan]Escape[/cyan]    Cancel / close dialog\n"
            "[cyan]Ctrl+C[/cyan]    Quit",
            classes="help-keys",
        )
