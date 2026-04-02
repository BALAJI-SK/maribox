"""Debug agent — error analysis, traceback explanation, and fix proposals."""

from __future__ import annotations

from typing import Any

from maribox.agents.base import MariboxAgent
from maribox.agents.tools.cell_tools import edit_cell_tool, run_cell_tool
from maribox.agents.tools.debug_tools import (
    analyze_error_tool,
    check_dependencies_tool,
    explain_traceback_tool,
    propose_fix_tool,
)


class DebugAgent(MariboxAgent):
    """Agent specialized in debugging notebook cells:
    analyzing errors, proposing fixes, explaining tracebacks.
    """

    @property
    def name(self) -> str:
        return "debug"

    @property
    def description(self) -> str:
        return "Analyzes errors, explains tracebacks, and proposes fixes for notebook cells."

    def _register_tools(self) -> list[dict[str, Any]]:
        return [
            edit_cell_tool(),
            run_cell_tool(),
            analyze_error_tool(),
            propose_fix_tool(),
            explain_traceback_tool(),
            check_dependencies_tool(),
        ]

    def _system_prompt(self) -> str:
        return (
            "You are the maribox debug agent. You help users diagnose and fix errors "
            "in their notebook cells.\n\n"
            "Approach:\n"
            "1. Analyze the error message and traceback\n"
            "2. Check the cell's code for common issues (typos, wrong types, missing imports)\n"
            "3. Check if the error is caused by a dependency (stale variable from another cell)\n"
            "4. Propose a specific fix with explanation\n"
            "5. If the fix requires editing a cell, clearly show the before/after\n\n"
            "Always explain WHY the error occurred, not just how to fix it."
        )
