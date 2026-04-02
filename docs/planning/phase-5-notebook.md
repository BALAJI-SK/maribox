# Phase 5: Notebook Engine

## Objective

Build the core notebook abstraction layer that models Marimo notebooks as directed acyclic graphs (DAGs) of cells, tracks inter-cell dependencies via AST-based variable analysis, and wraps Marimo's headless WebSocket API to provide programmatic control over notebook execution. This phase also provides standalone read/write utilities for `.py` notebook files so that the rest of Maribox can manipulate notebooks without a running Marimo server.

## Files to Create

- `src/maribox/notebook/__init__.py` — re-exports `Cell`, `CellDAG`, `MarimoRuntime`
- `src/maribox/notebook/cell.py` — cell data model and types
- `src/maribox/notebook/dag.py` — cell dependency graph with topological sort
- `src/maribox/notebook/runtime.py` — async wrapper around Marimo headless WebSocket API
- `src/maribox/notebook/export.py` — standalone `.py` notebook file read/write
- `src/maribox/notebook/ast_analysis.py` — AST visitor for variable dependency extraction

## Key Interfaces

### `cell.py`

```python
from typing import NewType, Optional, List, Any, Dict
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

CellId = NewType("CellId", str)

class CellStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    STALE = "stale"
    DISABLED = "disabled"

@dataclass
class CellOutput:
    """Represents the output of a single cell execution."""
    channel: str                    # "stdout" | "stderr" | "output" | "error"
    data: Any                       # string, rich object, or error traceback
    mime_type: Optional[str] = None
    timestamp: Optional[datetime] = None

@dataclass
class Cell:
    """
    A single notebook cell with its code, metadata, and execution state.
    Immutable except for status and outputs which track execution progress.
    """
    id: CellId
    name: str                       # variable name or auto-generated
    code: str
    status: CellStatus = CellStatus.PENDING
    outputs: List[CellOutput] = field(default_factory=list)
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    last_run: Optional[datetime] = None
    position: int = 0               # visual ordering

    def mark_stale(self) -> "Cell":
        """Return a new Cell with status STALE."""

    def with_result(self, outputs: List[CellOutput], exec_time: float) -> "Cell":
        """Return a new Cell with status SUCCESS and the given outputs."""

    def with_error(self, error: str, exec_time: float) -> "Cell":
        """Return a new Cell with status ERROR and the given error message."""
```

### `dag.py`

```python
class CyclicDependencyError(Exception): ...

class CellDAG:
    """
    Directed acyclic graph of cells in a notebook.
    Edges represent variable dependencies discovered via AST analysis.
    Supports topological sort for execution ordering.
    """

    def __init__(self) -> None: ...

    def add_cell(self, cell: Cell) -> None:
        """Add a cell to the DAG. Discovers dependencies via AST analysis."""

    def remove_cell(self, cell_id: CellId) -> None:
        """Remove a cell and all its edges from the DAG."""

    def update_cell(self, cell: Cell) -> None:
        """Update a cell's code and recompute its dependencies."""

    def get_cell(self, cell_id: CellId) -> Optional[Cell]:
        """Retrieve a cell by ID."""

    def dependencies(self, cell_id: CellId) -> Set[CellId]:
        """
        Return the set of cell IDs that the given cell depends on.
        These are cells that define variables used by this cell.
        """

    def dependents(self, cell_id: CellId) -> Set[CellId]:
        """
        Return the set of cell IDs that depend on the given cell.
        These are cells that use variables defined by this cell.
        """

    def topological_sort(self) -> List[CellId]:
        """
        Return cell IDs in a valid execution order.
        Raises CyclicDependencyError if the graph contains a cycle.
        """

    def execution_order(self, changed_cell_id: CellId) -> List[CellId]:
        """
        Return the cells that need re-execution when a given cell changes.
        Includes the changed cell and all its transitive dependents,
        in topological order.
        """

    def stale_cells(self) -> Set[CellId]:
        """Return all cells with status STALE."""

    def all_cells(self) -> List[Cell]:
        """Return all cells in topological order."""

    def validate(self) -> List[str]:
        """
        Check the DAG for issues (undefined variables, cycles, etc.).
        Returns a list of warning/error messages.
    """
```

### `ast_analysis.py`

```python
@dataclass
class VariableAnalysis:
    """Result of analyzing a cell's AST for variable usage."""
    defines: Set[str]               # variables defined/assigned in this cell
    uses: Set[str]                  # variables referenced but not defined here
    imports: Set[str]               # module names imported

def analyze_cell(code: str) -> VariableAnalysis:
    """
    Parse a cell's code into an AST and extract variable definitions and uses.
    Handles: assignments, function defs, class defs, imports, for loops,
    with statements, comprehensions, and augmented assignments.
    """

def analyze_import_alias(name: str) -> str:
    """Resolve import aliases: 'import numpy as np' -> 'numpy'."""
```

### `runtime.py`

```python
class RuntimeError(Exception): ...
class ConnectionError(RuntimeError): ...

@dataclass
class ExecutionResult:
    cell_id: CellId
    success: bool
    outputs: List[CellOutput]
    error: Optional[str]
    duration_ms: float

class MarimoRuntime:
    """
    Async wrapper around Marimo's headless WebSocket API.
    Provides programmatic control over notebook execution.
    """

    def __init__(self, ws_url: str, session_id: str): ...

    async def connect(self) -> None:
        """Establish WebSocket connection to the Marimo server."""

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""

    async def run_cell(self, cell_id: CellId, code: str) -> ExecutionResult:
        """
        Execute a single cell and wait for the result.
        Returns an ExecutionResult with outputs and timing.
        """

    async def run_cells(self, cell_ids: List[CellId], codes: List[str]) -> List[ExecutionResult]:
        """Execute multiple cells in order, returning all results."""

    async def get_cell_status(self, cell_id: CellId) -> CellStatus:
        """Query the current execution status of a cell."""

    async def set_cell_code(self, cell_id: CellId, code: str) -> None:
        """Update a cell's code without executing it."""

    async def get_notebook_state(self) -> Dict[CellId, Cell]:
        """Retrieve the current state of all cells."""

    async def interrupt(self) -> None:
        """Send an interrupt signal to the running kernel."""

    async def restart_kernel(self) -> None:
        """Restart the notebook kernel, clearing all cell outputs."""

    async def __aenter__(self) -> "MarimoRuntime": ...
    async def __aexit__(self, *args) -> None: ...
```

### `export.py`

```python
def read_notebook(path: Path) -> List[Cell]:
    """
    Parse a standalone Marimo .py notebook file into a list of Cell objects.
    Handles the standard Marimo file format (cells as function definitions).
    """

def write_notebook(path: Path, cells: List[Cell]) -> None:
    """
    Write a list of Cell objects to a Marimo .py notebook file.
    Produces a valid Marimo notebook that can be opened in the Marimo editor.
    """

def notebook_metadata(path: Path) -> Dict[str, Any]:
    """Extract metadata (title, description, tags) from a notebook file."""
```

## Dependencies

- **Phase 4 (Sandbox)** must be complete: `MarimoRuntime` connects to a Marimo server running inside a sandbox container, using the `SandboxClient` to manage the container lifecycle and obtain the WebSocket URL.
- Runtime packages: `websockets` (async WebSocket client), `ast` (stdlib, for variable analysis), `marimo` (for notebook format compatibility).

## Testing Strategy

- **Unit tests for Cell data model**: Test `with_result()`, `with_error()`, `mark_stale()` produce correct new instances. Verify immutability of original Cell.
- **Unit tests for VariableAnalysis**: Test `analyze_cell()` against representative code patterns: simple assignment, function definition, class definition, import with alias, for-loop variable, comprehension variable, augmented assignment, global/nonlocal declarations.
- **Unit tests for CellDAG**: Build a DAG with known dependencies (cell A defines x, cell B uses x, cell C uses y from B). Test `dependencies()`, `dependents()`, `topological_sort()`, `execution_order()`. Test cycle detection with `CyclicDependencyError`.
- **Unit tests for export**: Round-trip a notebook through `write_notebook()` then `read_notebook()` and assert cell codes and names match.
- **Integration tests for MarimoRuntime**: Requires a running Marimo server (spawned in Docker from Phase 4). Test `connect`, `run_cell`, `get_cell_status`, `interrupt`, `disconnect`. Tagged with `@pytest.mark.integration`.
- **Property-based tests for topological sort**: Use Hypothesis to generate random DAGs and verify that topological sort always produces a valid ordering (every cell appears after its dependencies).
- **Edge cases**: Empty notebook, single cell with no dependencies, cell with only imports, cell referencing undefined variable, self-referential cell.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Marimo headless WebSocket API is internal/unstable | API changes between Marimo versions break the runtime | Pin the Marimo version in the sandbox image; wrap all WebSocket messages in an adapter layer that can be updated independently; log the Marimo version for debugging |
| AST analysis misses dynamic variable references | Dependency graph is incomplete, cells execute out of order | Support common patterns (`getattr`, `globals()`, `locals()`) with explicit warnings; allow manual dependency annotations via cell metadata |
| Large notebooks with hundreds of cells | Topological sort is slow, DAG operations are O(n^2) | Cache the sort result and invalidate only on cell changes; use adjacency lists instead of matrix representation |
| WebSocket connection drops mid-execution | Cell results are lost | Implement reconnection with message replay; persist cell state locally so it can be restored |
| `.py` notebook format changes in future Marimo | `read_notebook`/`write_notebook` break | Pin the format version; validate on read and warn on version mismatch |
| Cyclic dependencies in user code | Infinite loop in topological sort | Detect cycles eagerly on `add_cell()` and `update_cell()`; raise `CyclicDependencyError` with a clear message showing the cycle path |

## Acceptance Criteria

- [ ] `Cell` dataclass correctly tracks status transitions and outputs
- [ ] `analyze_cell()` correctly identifies defines, uses, and imports for all tested patterns
- [ ] `CellDAG.add_cell()` discovers dependencies via AST analysis and adds edges
- [ ] `CellDAG.topological_sort()` returns a valid execution order
- [ ] `CellDAG.execution_order()` returns only affected cells when a cell changes
- [ ] `CellDAG.validate()` detects undefined variables and reports them
- [ ] `CyclicDependencyError` is raised with a descriptive cycle path message
- [ ] `MarimoRuntime.run_cell()` executes code and returns `ExecutionResult` with outputs
- [ ] `MarimoRuntime.interrupt()` cancels a running cell execution
- [ ] `read_notebook()` and `write_notebook()` round-trip without data loss
- [ ] All WebSocket messages are handled asynchronously with proper error propagation
- [ ] Unit test coverage >= 80% for `notebook/` package
- [ ] Integration tests pass against a Docker-based Marimo server
