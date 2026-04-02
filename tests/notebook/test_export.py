"""Tests for notebook export/import."""

from pathlib import Path

from maribox.notebook.cell import Cell, CellId
from maribox.notebook.export import export_notebook, import_notebook


class TestExportNotebook:
    def test_export_creates_file(self, tmp_path: Path) -> None:
        cells = [
            Cell(id=CellId("c1"), code="x = 1", name="init"),
            Cell(id=CellId("c2"), code="y = x + 1\nprint(y)", name="calc"),
        ]
        out = tmp_path / "notebook.py"
        export_notebook(cells, out)
        content = (tmp_path / "notebook.py").read_text()
        assert "import marimo" in content
        assert "@app.cell" in content
        assert "def init():" in content
        assert "def calc():" in content

    def test_export_empty(self, tmp_path: Path) -> None:
        export_notebook([], tmp_path / "empty.py")
        content = (tmp_path / "empty.py").read_text()
        assert "import marimo" in content


class TestImportNotebook:
    def test_import_nonexistent(self, tmp_path: Path) -> None:
        cells = import_notebook(tmp_path / "nonexistent.py")
        assert cells == []

    def test_roundtrip(self, tmp_path: Path) -> None:
        original = [
            Cell(id=CellId("c1"), code="x = 42", name="answer"),
            Cell(id=CellId("c2"), code='print(f"Answer: {x}")', name="show"),
        ]
        out = tmp_path / "nb.py"
        export_notebook(original, out)
        imported = import_notebook(out)
        assert len(imported) == 2
        assert "x = 42" in imported[0].code
