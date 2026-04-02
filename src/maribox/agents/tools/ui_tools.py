"""UI component tools for agents — marimo widget and layout helpers."""

from __future__ import annotations

from typing import Any

# Reference of marimo UI components available for agent use
MARIMO_COMPONENTS = {
    "text": "mo.ui.text() — text input field",
    "slider": "mo.ui.slider() — numeric slider",
    "dropdown": "mo.ui.dropdown() — dropdown selector",
    "checkbox": "mo.ui.checkbox() — checkbox toggle",
    "button": "mo.ui.button() — clickable button",
    "table": "mo.ui.table() — interactive data table",
    "dataframe": "mo.ui.dataframe() — editable dataframe viewer",
    "data_explorer": "mo.ui.data_explorer() — data profiling tool",
    "plotly": "mo.ui.plotly() — Plotly chart integration",
    "tabs": "mo.ui.tabs() — tabbed container",
    "card": "mo.ui.card() — card container",
    "accordion": "mo.ui.accordion() — collapsible sections",
    "hstack": "mo.hstack() — horizontal layout",
    "vstack": "mo.vstack() — vertical layout",
    "markdown": "mo.md() — markdown rendering",
    "html": "mo.Html() — raw HTML rendering",
}


def list_available_components_tool() -> dict[str, Any]:
    """Return a tool definition for listing available UI components."""
    return {
        "name": "list_available_components",
        "description": "List all available marimo UI components with descriptions.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter by category: 'input', 'display', 'layout', or omit for all",
                    "enum": ["input", "display", "layout"],
                },
            },
        },
    }


def suggest_layout_tool() -> dict[str, Any]:
    """Return a tool definition for suggesting a UI layout."""
    return {
        "name": "suggest_layout",
        "description": "Suggest a layout structure for a set of UI components.",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of the desired UI layout",
                },
                "components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of component types to include",
                },
            },
            "required": ["description"],
        },
    }
