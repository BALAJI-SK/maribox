"""Notebook agent — code generation, cell manipulation, and dependency management."""

from __future__ import annotations

from typing import Any

from maribox.agents.base import MariboxAgent
from maribox.agents.tools.cell_tools import create_cell_tool, delete_cell_tool, edit_cell_tool, run_cell_tool
from maribox.agents.tools.notebook_tools import explain_cell_tool, run_notebook_tool


class NotebookAgent(MariboxAgent):
    """Agent specialized in notebook operations: creating cells, modifying code,
    explaining code, suggesting optimizations, and managing cell dependencies.
    """

    @property
    def name(self) -> str:
        return "notebook"

    @property
    def description(self) -> str:
        return "Creates, edits, runs, and explains notebook cells."

    def _register_tools(self) -> list[dict[str, Any]]:
        return [
            create_cell_tool(),
            edit_cell_tool(),
            delete_cell_tool(),
            run_cell_tool(),
            run_notebook_tool(),
            explain_cell_tool(),
        ]

    def _system_prompt(self) -> str:
        return (
            "You are the maribox notebook agent. You help users write, modify, and debug "
            "Python code in marimo notebook cells.\n\n"
            "Guidelines:\n"
            "- Write clean, well-documented Python code\n"
            "- Respect marimo's reactive programming model — cells react to changes\n"
            "- Consider cell dependencies when making changes (variables defined in one cell "
            "may be used in others)\n"
            "- Use appropriate variable names that work with the dependency DAG\n"
            "- When adding imports, create or update a dedicated imports cell\n"
            "- Explain your changes briefly when modifying existing code"
        )
