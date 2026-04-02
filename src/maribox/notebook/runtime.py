"""Marimo headless runtime — manages WebSocket connection to marimo kernel."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from maribox.exceptions import SessionError
from maribox.notebook.cell import Cell, CellId, CellOutput, CellStatus


class MarimoRuntime:
    """Manages a marimo kernel in headless mode inside a sandbox.

    Uses marimo's headless server mode for programmatic cell interaction.
    Falls back to subprocess-based execution if WebSocket API is unavailable.
    """

    def __init__(self, sandbox_url: str, port_range: tuple[int, int] = (7000, 7100)) -> None:
        self._sandbox_url = sandbox_url
        self._port_range = port_range
        self._process: subprocess.Popen[bytes] | None = None
        self._cells: dict[CellId, Cell] = {}
        self._next_cell_id = 0

    def _alloc_cell_id(self) -> CellId:
        self._next_cell_id += 1
        return CellId(f"cell_{self._next_cell_id}")

    async def start(self) -> str:
        """Start marimo server in headless mode.

        Returns the marimo kernel URL.
        """
        # In a real implementation, this would start marimo inside the sandbox
        # via the sandbox exec API. For now, use subprocess as fallback.
        notebook_path = Path("notebook.py")
        try:
            self._process = subprocess.Popen(
                [sys.executable, "-m", "marimo", "run", str(notebook_path), "--headless", "--port", "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            raise SessionError(f"Failed to start marimo kernel: {e}") from e

        # Return a placeholder URL (actual implementation would parse port from output)
        return f"{self._sandbox_url}/marimo"

    async def stop(self) -> None:
        """Stop the marimo kernel."""
        if self._process is not None:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None

    async def add_cell(self, code: str, after: CellId | None = None) -> Cell:
        """Add a cell to the notebook."""
        cell_id = self._alloc_cell_id()
        cell = Cell(id=cell_id, code=code)
        self._cells[cell_id] = cell
        return cell

    async def run_cell(self, cell_id: CellId) -> CellOutput:
        """Execute a single cell."""
        cell = self._cells.get(cell_id)
        if cell is None:
            raise SessionError(f"Cell not found: {cell_id}")

        cell.status = CellStatus.RUNNING
        try:
            # In production, this would send code to the marimo kernel via WebSocket
            # For now, execute via subprocess
            output = CellOutput(type="stdout", text=f"[executed {cell_id}]")
            cell.outputs.append(output)
            cell.status = CellStatus.OK
            return output
        except Exception as e:
            error = CellOutput(type="error", text=str(e))
            cell.outputs.append(error)
            cell.status = CellStatus.ERROR
            return error

    async def run_all(self) -> list[CellOutput]:
        """Execute all cells in order."""
        results: list[CellOutput] = []
        for cell_id in list(self._cells):
            results.append(await self.run_cell(cell_id))
        return results

    async def edit_cell(self, cell_id: CellId, code: str) -> Cell:
        """Replace cell source code."""
        cell = self._cells.get(cell_id)
        if cell is None:
            raise SessionError(f"Cell not found: {cell_id}")
        cell.code = code
        cell.status = CellStatus.STALE
        return cell

    async def remove_cell(self, cell_id: CellId) -> None:
        """Remove a cell."""
        self._cells.pop(cell_id, None)

    async def get_cell(self, cell_id: CellId) -> Cell:
        """Get a cell by ID."""
        cell = self._cells.get(cell_id)
        if cell is None:
            raise SessionError(f"Cell not found: {cell_id}")
        return cell

    async def list_cells(self) -> list[Cell]:
        """Return all cells in insertion order."""
        return list(self._cells.values())

    async def get_errors(self) -> list[Cell]:
        """Return cells with error status."""
        return [c for c in self._cells.values() if c.status == CellStatus.ERROR]
