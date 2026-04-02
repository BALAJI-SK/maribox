"""Tests for cell DAG — variable dependency tracking."""

from maribox.notebook.cell import Cell, CellId
from maribox.notebook.dag import CellDAG


def _make_cell(cell_id: str, code: str | None = None) -> Cell:
    if code is None:
        code = f"x = {cell_id}\n"
    return Cell(id=CellId(f"c_{cell_id}"), code=code)


class TestCellDAG:
    def test_add_cell(self):
        dag = CellDAG()
        c1 = _make_cell("a")
        c2 = _make_cell("b")
        c3 = _make_cell("c")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3)
        assert len(dag.topological_order()) == 3
        assert c1.id in dag.topological_order()

    def test_variable_dependencies(self):
        dag = CellDAG()
        c1 = _make_cell("a", "x = 1")
        c2 = _make_cell("b", "y = x + 1")
        c3 = _make_cell("c", "print(x)")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3)
        # c1 defines x -> c2 depends on c1, c3 depends on c1
        deps = dag.get_dependencies(c3.id)
        assert deps == {c1.id}
        deps = dag.get_dependencies(c2.id)
        assert deps == {c1.id}

    def test_stale_cells(self):
        dag = CellDAG()
        c1 = _make_cell("a", "x = 1")
        c2 = _make_cell("b", "y = x + 1")
        c3 = _make_cell("c", "z = 1")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3)
        stale = dag.get_stale_cells(c1.id)
        # c2 dependents on c1, c3 dependents on nothing.
        assert stale == {c2.id}

    def test_remove_cell(self):
        dag = CellDAG()
        c1 = _make_cell("a")
        c2 = _make_cell("b")
        c3 = _make_cell("c")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3)
        dag.remove_cell(c2.id)
        assert len(dag.topological_order()) == 2
        assert c2.id not in dag.get_dependencies(c3.id)

    def test_topological_order(self):
        dag = CellDAG()
        c1 = _make_cell("a", "x = 1")
        c2 = _make_cell("b", "y = x + 1")
        c3 = _make_cell("c", "print(x)")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3)
        order = dag.topological_order()
        assert order == [c1.id, c2.id, c3.id]

    def test_empty_dag(self):
        dag = CellDAG()
        assert dag.topological_order() == []
        assert dag.get_stale_cells(CellId("nonexistent")) == set()
