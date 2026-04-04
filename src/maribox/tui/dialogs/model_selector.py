"""Model selector dialog — modal overlay for choosing AI model."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


# Default models per provider
PROVIDER_MODELS: dict[str, list[str]] = {
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3.5-haiku-20241022",
    ],
    "google": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "o3",
        "o4-mini",
    ],
    "glm": [
        "glm-5.1",
    ],
}


class ModelSelector(ModalScreen[str | None]):
    """Modal dialog for selecting an AI model."""

    DEFAULT_CSS = """
    ModelSelector {
        align: center middle;
    }

    #model-selector-container {
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        width: 60;
        height: auto;
        max-height: 18;
    }

    .selector-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
        height: 1;
    }

    .provider-label {
        color: $secondary;
        text-style: bold;
        height: 1;
        margin-top: 1;
    }

    .model-entry {
        height: 1;
        padding: 0 2;
        color: $text;
    }

    .model-entry:hover {
        background: $surface;
    }

    .model-entry.selected {
        background: $primary-dim;
        color: $text-emphasized;
    }

    .model-entry .model-name {
        color: $text;
    }

    .model-entry.active {
        color: $success;
    }

    .model-entry.active::after {
        content: " ✓";
        color: $success;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
        Binding("up", "move_up", show=False),
        Binding("down", "move_down", show=False),
        Binding("k", "move_up", show=False),
        Binding("j", "move_down", show=False),
        Binding("enter", "select", show=False),
        Binding("left", "prev_provider", show=False),
        Binding("right", "next_provider", show=False),
        Binding("h", "prev_provider", show=False),
        Binding("l", "next_provider", show=False),
    ]

    def __init__(self, current_model: str = "", current_provider: str = "", **kwargs) -> None:
        self._current_model = current_model
        self._current_provider = current_provider
        self._providers = list(PROVIDER_MODELS.keys())
        self._provider_idx = 0
        if current_provider in self._providers:
            self._provider_idx = self._providers.index(current_provider)
        self._selected = 0
        super().__init__(**kwargs)

    @property
    def _current_models(self) -> list[str]:
        provider = self._providers[self._provider_idx] if self._providers else ""
        return PROVIDER_MODELS.get(provider, [])

    def compose(self) -> ComposeResult:
        with Vertical(id="model-selector-container"):
            yield Static("[bold cyan]Select Model[/bold cyan]", classes="selector-title")
            self._render_models()

    def _render_models(self) -> None:
        # Remove old entries
        for widget in self.query(".provider-label, .model-entry"):
            widget.remove()

        container = self.query_one("#model-selector-container", Vertical)
        provider = self._providers[self._provider_idx] if self._providers else ""
        provider_idx_str = f"({self._provider_idx + 1}/{len(self._providers)})"

        container.mount(Static(
            f"[bold][{provider}][/bold] {provider_idx_str}  [dim]← → to switch provider[/dim]",
            classes="provider-label",
        ))

        for i, model in enumerate(self._current_models):
            is_active = model == self._current_model
            selected_class = " selected" if i == self._selected else ""
            active_class = " active" if is_active else ""
            container.mount(Static(
                f"  {model}",
                classes=f"model-entry{selected_class}{active_class}",
            ))

    def action_move_up(self) -> None:
        if self._selected > 0:
            self._selected -= 1
            self._refresh_selection()

    def action_move_down(self) -> None:
        models = self._current_models
        if self._selected < len(models) - 1:
            self._selected += 1
            self._refresh_selection()

    def action_prev_provider(self) -> None:
        if self._provider_idx > 0:
            self._provider_idx -= 1
            self._selected = 0
            self._render_models()

    def action_next_provider(self) -> None:
        if self._provider_idx < len(self._providers) - 1:
            self._provider_idx += 1
            self._selected = 0
            self._render_models()

    def action_select(self) -> None:
        models = self._current_models
        if models and 0 <= self._selected < len(models):
            self.dismiss(models[self._selected])
        else:
            self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)

    def _refresh_selection(self) -> None:
        entries = self.query(".model-entry")
        for i, entry in enumerate(entries):
            if i == self._selected:
                entry.add_class("selected")
            else:
                entry.remove_class("selected")
