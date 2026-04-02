"""Reactive cell DAG — tracks variable dependencies between cells."""

from __future__ import annotations

import ast
import bisect
from collections import defaultdict
from dataclasses import dataclass, field

from maribox.notebook.cell import Cell, CellId


@dataclass
class _Node:
    """Internal DAG node."""

    cell_id: CellId
    defines: set[str] = field(default_factory=set)
    uses: set[str] = field(default_factory=set)


class CellDAG:
    """Directed acyclic graph tracking cell dependencies via variable analysis.

    When a cell is added or edited, the DAG re-analyzes which variables it
    defines (assignments, function/class defs) and which it uses (names referenced
    but not defined). Edges connect defining cells to using cells.
    """

    def __init__(self) -> None:
        self._nodes: dict[CellId, _Node] = {}
        self._edges: dict[CellId, set[CellId]] = defaultdict(set)  # src -> set of dependents
        self._reverse: dict[CellId, set[CellId]] = defaultdict(set)  # dst -> set of dependencies
        self._order: list[CellId] = []

    def add_cell(self, cell: Cell, after: CellId | None = None) -> None:
        """Add a cell to the DAG, optionally inserting after another cell."""
        defs, uses = _analyze_vars(cell.code)
        node = _Node(cell_id=cell.id, defines=defs, uses=uses)
        self._nodes[cell.id] = node

        if after is not None and after in self._order:
            idx = self._order.index(after) + 1
            self._order.insert(idx, cell.id)
        else:
            self._order.append(cell.id)

        self._rebuild_edges()

    def remove_cell(self, cell_id: CellId) -> None:
        """Remove a cell and update edges."""
        self._nodes.pop(cell_id, None)
        if cell_id in self._order:
            self._order.remove(cell_id)
        self._edges.pop(cell_id, None)
        self._reverse.pop(cell_id, None)
        for deps in self._edges.values():
            deps.discard(cell_id)
        for deps in self._reverse.values():
            deps.discard(cell_id)
        self._rebuild_edges()

    def get_dependencies(self, cell_id: CellId) -> set[CellId]:
        """Return cells that this cell depends on."""
        return set(self._reverse.get(cell_id, set()))

    def get_dependents(self, cell_id: CellId) -> set[CellId]:
        """Return cells that depend on this cell."""
        return set(self._edges.get(cell_id, set()))

    def get_stale_cells(self, changed_cell_id: CellId) -> set[CellId]:
        """Return cells that need re-execution after a change (transitive dependents)."""
        stale: set[CellId] = set()
        queue = [changed_cell_id]
        while queue:
            current = queue.pop()
            for dep in self._edges.get(current, set()):
                if dep not in stale:
                    stale.add(dep)
                    queue.append(dep)
        return stale

    def topological_order(self) -> list[CellId]:
        """Return cells in execution order respecting dependencies.

        Uses Kahn's algorithm with insertion-order as tiebreaker so cells
        added earlier (or with explicit `after`) appear before later ones
        when both have equal in-degree.
        """
        order_index = {cid: i for i, cid in enumerate(self._order)}
        in_degree: dict[CellId, int] = {cid: 0 for cid in self._order}
        for cid in self._order:
            for dep in self._edges.get(cid, set()):
                in_degree[dep] += 1

        # Seed with zero in-degree, sorted by insertion order
        queue = sorted(
            [cid for cid in self._order if in_degree[cid] == 0],
            key=lambda c: order_index[c],
        )
        result: list[CellId] = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            newly_ready: list[CellId] = []
            for dep in self._edges.get(node, set()):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    newly_ready.append(dep)
            # Insert newly ready nodes sorted by insertion order
            for nr in sorted(newly_ready, key=lambda c: order_index[c]):
                # Insert in sorted position to maintain order
                bisect.insort(queue, nr, key=lambda c: order_index[c])

        # Add any remaining nodes (cycles — shouldn't happen in a DAG)
        for cid in self._order:
            if cid not in result:
                result.append(cid)

        return result

    def _rebuild_edges(self) -> None:
        """Rebuild dependency edges based on variable definitions and uses."""
        self._edges.clear()
        self._reverse.clear()

        # Map variable name -> CellId that defines it (last definition wins)
        var_to_cell: dict[str, CellId] = {}
        for cell_id in self._order:
            node = self._nodes.get(cell_id)
            if node is None:
                continue
            for var in node.defines:
                var_to_cell[var] = cell_id

        # Create edges: if cell B uses a variable defined by cell A, A -> B
        for cell_id in self._order:
            node = self._nodes.get(cell_id)
            if node is None:
                continue
            for var in node.uses:
                source = var_to_cell.get(var)
                if source is not None and source != cell_id:
                    self._edges[source].add(cell_id)
                    self._reverse[cell_id].add(source)


def _analyze_vars(code: str) -> tuple[set[str], set[str]]:
    """Analyze Python code to find defined and used names.

    Returns (defines, uses) where:
    - defines: names assigned or defined (assignments, function/class defs)
    - uses: names referenced but not defined in this code
    """
    defines: set[str] = set()
    uses: set[str] = set()

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return defines, uses

    # Collect all names that are defined
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef | ast.AsyncFunctionDef, ast.ClassDef)):
            defines.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defines.add(target.id)
                elif isinstance(target, ast.Tuple | ast.List):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            defines.add(elt.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            defines.add(node.target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name.split(".")[0]
                defines.add(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                defines.add(name)

    # Collect all names that are used (loaded)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            uses.add(node.id)

    # Uses = names referenced minus names defined
    uses -= defines
    return defines, uses
