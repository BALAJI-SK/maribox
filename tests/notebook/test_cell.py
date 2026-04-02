"""Tests for cell data types."""

from maribox.notebook.cell import Cell, CellId, CellOutput, CellStatus


class TestCell:
    def test_cell_creation(self):
        cell = Cell(id=CellId("test_1"), code="x = 1")
        assert cell.id == CellId("test_1")
        assert cell.code == "x = 1"
        assert cell.status == CellStatus.OK

    def test_cell_with_name(self):
        cell = Cell(id=CellId("test_2"), code="print('hello')", name="greet")
        assert cell.name == "greet"

    def test_cell_output(self):
        output = CellOutput(type="stdout", text="hello")
        assert output.type == "stdout"
        assert output.text == "hello"
        assert output.timestamp  # not empty

    def test_cell_status(self):
        assert CellStatus.OK == "ok"
        assert CellStatus.RUNNING == "running"
        assert CellStatus.ERROR == "error"
        assert CellStatus.STALE == "stale"


class TestCellId:
    def test_cell_id_is_str(self):
        assert isinstance(CellId("abc"), str)
        assert CellId("abc") == "abc"
