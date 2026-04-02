"""Notebook-level tools for agents — run all cells, explain cell code."""

from __future__ import annotations

from typing import Any


def run_notebook_tool() -> dict[str, Any]:
    """Return a tool definition for running the entire notebook."""
    return {
        "name": "run_notebook",
        "description": "Execute all cells in the notebook in dependency order.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    }


def explain_cell_tool() -> dict[str, Any]:
    """Return a tool definition for explaining a cell's code."""
    return {
        "name": "explain_cell",
        "description": "Explain what a cell's code does in plain language.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell to explain",
                },
                "detail_level": {
                    "type": "string",
                    "description": "Level of detail: 'brief' or 'detailed'",
                    "enum": ["brief", "detailed"],
                },
            },
            "required": ["cell_id"],
        },
    }
