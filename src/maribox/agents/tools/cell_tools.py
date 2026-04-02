"""Cell manipulation tools for agents — create, edit, delete, and run cells."""

from __future__ import annotations

from typing import Any


def create_cell_tool() -> dict[str, Any]:
    """Return a tool definition for creating a new cell."""
    return {
        "name": "create_cell",
        "description": "Create a new notebook cell with the given code.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code for the cell",
                },
                "name": {
                    "type": "string",
                    "description": "Optional human-readable name for the cell",
                },
                "after": {
                    "type": "string",
                    "description": "Optional cell ID to insert after",
                },
            },
            "required": ["code"],
        },
    }


def edit_cell_tool() -> dict[str, Any]:
    """Return a tool definition for editing cell code."""
    return {
        "name": "edit_cell",
        "description": "Edit the source code of an existing cell.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell to edit",
                },
                "code": {
                    "type": "string",
                    "description": "New Python code for the cell",
                },
            },
            "required": ["cell_id", "code"],
        },
    }


def delete_cell_tool() -> dict[str, Any]:
    """Return a tool definition for deleting a cell."""
    return {
        "name": "delete_cell",
        "description": "Delete a cell from the notebook.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell to delete",
                },
            },
            "required": ["cell_id"],
        },
    }


def run_cell_tool() -> dict[str, Any]:
    """Return a tool definition for running a cell."""
    return {
        "name": "run_cell",
        "description": "Execute a single cell and return its output.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell to run",
                },
            },
            "required": ["cell_id"],
        },
    }
