"""Debugging tools for agents — error analysis, fix proposals, traceback explanation."""

from __future__ import annotations

from typing import Any


def analyze_error_tool() -> dict[str, Any]:
    """Return a tool definition for analyzing an error."""
    return {
        "name": "analyze_error",
        "description": "Analyze an error from a cell and provide diagnosis.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell with the error",
                },
                "error_text": {
                    "type": "string",
                    "description": "The error message or traceback text",
                },
            },
            "required": ["cell_id"],
        },
    }


def propose_fix_tool() -> dict[str, Any]:
    """Return a tool definition for proposing a fix."""
    return {
        "name": "propose_fix",
        "description": "Propose a code fix for a cell with an error.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell to fix",
                },
                "fix_description": {
                    "type": "string",
                    "description": "Description of what the fix does",
                },
                "new_code": {
                    "type": "string",
                    "description": "The proposed replacement code",
                },
            },
            "required": ["cell_id", "new_code"],
        },
    }


def explain_traceback_tool() -> dict[str, Any]:
    """Return a tool definition for explaining a traceback."""
    return {
        "name": "explain_traceback",
        "description": "Explain a Python traceback in plain language.",
        "parameters": {
            "type": "object",
            "properties": {
                "traceback_text": {
                    "type": "string",
                    "description": "The full traceback text",
                },
            },
            "required": ["traceback_text"],
        },
    }


def check_dependencies_tool() -> dict[str, Any]:
    """Return a tool definition for checking cell dependencies."""
    return {
        "name": "check_dependencies",
        "description": "Check which cells depend on or are depended upon by a given cell.",
        "parameters": {
            "type": "object",
            "properties": {
                "cell_id": {
                    "type": "string",
                    "description": "ID of the cell to check dependencies for",
                },
            },
            "required": ["cell_id"],
        },
    }
