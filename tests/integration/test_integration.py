"""Integration tests — full workflow tests using temp directories."""

from pathlib import Path

import pytest

from maribox.auth.manager import AuthManager
from maribox.config.io import init_config_dir, load_config, save_config
from maribox.notebook.cell import Cell, CellId
from maribox.notebook.dag import CellDAG
from maribox.notebook.export import export_notebook, import_notebook
from maribox.notebook.runtime import MarimoRuntime


class TestConfigWorkflow:
    """Test config init -> load -> modify -> save -> reload."""

    def test_full_config_lifecycle(self, tmp_path: Path) -> None:
        # 1. Init config directory
        config_root = init_config_dir(tmp_path, scope="project")
        assert config_root.is_dir()
        assert (config_root / "config.toml").is_file()

        # 2. Load and verify defaults
        config = load_config(config_root)
        assert config.maribox.default_provider == "anthropic"

        # 3. Modify and save
        config.maribox.default_provider = "glm"
        config.maribox.default_model = "glm-4-plus"
        save_config(config_root, config)

        # 4. Reload and verify persistence
        reloaded = load_config(config_root)
        assert reloaded.maribox.default_provider == "glm"
        assert reloaded.maribox.default_model == "glm-4-plus"


class TestAuthWorkflow:
    """Test key storage and retrieval."""

    def test_set_and_get_key(self, tmp_path: Path) -> None:
        auth = AuthManager(tmp_path)
        auth.set_key("anthropic", "sk-ant-test123456789012345678901234567890")

        key = auth.get_key("anthropic")
        assert key == "sk-ant-test123456789012345678901234567890"

        keys = auth.list_keys()
        anthropic_entry = next((k for k in keys if k.provider == "anthropic"), None)
        assert anthropic_entry is not None
        assert anthropic_entry.has_key

    def test_rotate_key(self, tmp_path: Path) -> None:
        auth = AuthManager(tmp_path)
        auth.set_key("openai", "sk-proj-oldkey12345678901234567890123456")
        auth.rotate_key("openai", "sk-proj-newkey12345678901234567890123456")

        assert auth.get_key("openai") == "sk-proj-newkey12345678901234567890123456"


class TestSessionWorkflow:
    """Test session creation with notebook export."""

    def test_session_notebook_roundtrip(self, tmp_path: Path) -> None:
        # Simulate a session directory
        session_id = "test-session-1"
        session_dir = tmp_path / "sessions" / session_id
        session_dir.mkdir(parents=True)

        # Create cells and export
        cells = [
            Cell(id=CellId("c1"), code="x = 42", name="init"),
            Cell(id=CellId("c2"), code="y = x * 2\nprint(y)", name="calc"),
        ]
        nb_path = session_dir / "notebook.py"
        export_notebook(cells, nb_path)

        # Import and verify
        imported = import_notebook(nb_path)
        assert len(imported) == 2
        assert "x = 42" in imported[0].code

        # Verify file is readable
        content = nb_path.read_text(encoding="utf-8")
        assert "import marimo" in content
        assert "def init" in content


class TestNotebookDAGWorkflow:
    """Test cell dependency tracking end-to-end."""

    def test_dependency_chain(self) -> None:
        dag = CellDAG()

        c1 = Cell(id=CellId("c1"), code="x = 1")
        c2 = Cell(id=CellId("c2"), code="y = x + 1")
        c3 = Cell(id=CellId("c3"), code="z = y * 2")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3, after=c2.id)

        assert dag.get_dependencies(c2.id) == {c1.id}
        assert dag.get_dependencies(c3.id) == {c2.id}

        stale = dag.get_stale_cells(c1.id)
        assert stale == {c2.id, c3.id}

        order = dag.topological_order()
        assert order.index(c1.id) < order.index(c2.id)
        assert order.index(c2.id) < order.index(c3.id)

    def test_parallel_dependencies(self) -> None:
        dag = CellDAG()

        c1 = Cell(id=CellId("c1"), code="x = 1")
        c2 = Cell(id=CellId("c2"), code="y = x + 1")
        c3 = Cell(id=CellId("c3"), code="z = x * 2")
        dag.add_cell(c1)
        dag.add_cell(c2, after=c1.id)
        dag.add_cell(c3, after=c1.id)

        assert dag.get_dependencies(c2.id) == {c1.id}
        assert dag.get_dependencies(c3.id) == {c1.id}

        stale = dag.get_stale_cells(c1.id)
        assert stale == {c2.id, c3.id}


class TestRuntimeWorkflow:
    """Test runtime cell operations."""

    @pytest.mark.asyncio
    async def test_add_and_run_cell(self) -> None:
        runtime = MarimoRuntime()
        cell = await runtime.add_cell("x = 42")
        assert cell.code == "x = 42"

        output = await runtime.run_cell(cell.id)
        assert output is not None

    @pytest.mark.asyncio
    async def test_edit_cell(self) -> None:
        runtime = MarimoRuntime()
        cell = await runtime.add_cell("x = 1")
        edited = await runtime.edit_cell(cell.id, "x = 2")
        assert edited.code == "x = 2"
        assert edited.status == "stale"

    @pytest.mark.asyncio
    async def test_remove_cell(self) -> None:
        runtime = MarimoRuntime()
        cell = await runtime.add_cell("x = 1")
        await runtime.remove_cell(cell.id)
        cells = await runtime.list_cells()
        assert len(cells) == 0

    @pytest.mark.asyncio
    async def test_list_and_get_cells(self) -> None:
        runtime = MarimoRuntime()
        c1 = await runtime.add_cell("a = 1")
        await runtime.add_cell("b = 2")
        cells = await runtime.list_cells()
        assert len(cells) == 2

        retrieved = await runtime.get_cell(c1.id)
        assert retrieved.code == "a = 1"

    @pytest.mark.asyncio
    async def test_get_errors(self) -> None:
        runtime = MarimoRuntime()
        await runtime.add_cell("x = 1")
        errors = await runtime.get_errors()
        assert len(errors) == 0
