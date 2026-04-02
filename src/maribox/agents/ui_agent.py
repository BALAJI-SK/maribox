"""UI agent — generates marimo UI components, forms, tables, charts, and layouts."""

from __future__ import annotations

from typing import Any

from maribox.agents.base import MariboxAgent
from maribox.agents.tools.cell_tools import create_cell_tool
from maribox.agents.tools.ui_tools import list_available_components_tool, suggest_layout_tool


class UiAgent(MariboxAgent):
    """Agent specialized in generating marimo UI components:
    forms, tables, charts, layouts, and interactive widgets.
    """

    @property
    def name(self) -> str:
        return "ui"

    @property
    def description(self) -> str:
        return "Generates marimo UI components, widgets, and interactive layouts."

    def _register_tools(self) -> list[dict[str, Any]]:
        return [
            create_cell_tool(),
            list_available_components_tool(),
            suggest_layout_tool(),
        ]

    def _system_prompt(self) -> str:
        return (
            "You are the maribox UI agent. You help users create interactive UI components "
            "using the marimo library (imported as `mo`).\n\n"
            "Available marimo UI components:\n"
            "- mo.ui.text(), mo.ui.slider(), mo.ui.dropdown(), mo.ui.checkbox()\n"
            "- mo.ui.table(), mo.ui.dataframe(), mo.ui.data_explorer()\n"
            "- mo.md() for markdown rendering\n"
            "- mo.ui.plotly() for Plotly charts\n"
            "- mo.hstack(), mo.vstack() for layouts\n"
            "- mo.ui.tabs(), mo.ui.card(), mo.ui.accordion()\n\n"
            "Guidelines:\n"
            "- Always use reactive patterns — link UI elements to computations\n"
            "- Use mo.hstack/mo.vstack for clean layouts\n"
            "- Provide sensible defaults for sliders and dropdowns\n"
            "- Include labels and descriptions for accessibility"
        )
