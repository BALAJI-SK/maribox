"""Tests for agent tool definitions."""

from maribox.agents.tools.cell_tools import create_cell_tool, delete_cell_tool, edit_cell_tool, run_cell_tool
from maribox.agents.tools.debug_tools import (
    analyze_error_tool,
    check_dependencies_tool,
    explain_traceback_tool,
    propose_fix_tool,
)
from maribox.agents.tools.notebook_tools import explain_cell_tool, run_notebook_tool
from maribox.agents.tools.session_tools import (
    create_session_tool,
    get_session_status_tool,
    kill_session_tool,
    list_sessions_tool,
)
from maribox.agents.tools.ui_tools import list_available_components_tool, suggest_layout_tool


class TestCellTools:
    def test_create_cell_has_required_schema(self) -> None:
        tool = create_cell_tool()
        assert tool["name"] == "create_cell"
        assert "code" in tool["parameters"]["properties"]
        assert "code" in tool["parameters"]["required"]

    def test_edit_cell_has_required_schema(self) -> None:
        tool = edit_cell_tool()
        assert tool["name"] == "edit_cell"
        assert "cell_id" in tool["parameters"]["required"]
        assert "code" in tool["parameters"]["required"]

    def test_delete_cell_has_required_schema(self) -> None:
        tool = delete_cell_tool()
        assert tool["name"] == "delete_cell"
        assert "cell_id" in tool["parameters"]["required"]

    def test_run_cell_has_required_schema(self) -> None:
        tool = run_cell_tool()
        assert tool["name"] == "run_cell"
        assert "cell_id" in tool["parameters"]["required"]


class TestNotebookTools:
    def test_run_notebook_tool(self) -> None:
        tool = run_notebook_tool()
        assert tool["name"] == "run_notebook"
        assert "parameters" in tool

    def test_explain_cell_tool(self) -> None:
        tool = explain_cell_tool()
        assert tool["name"] == "explain_cell"
        assert "cell_id" in tool["parameters"]["required"]


class TestSessionTools:
    def test_create_session(self) -> None:
        tool = create_session_tool()
        assert tool["name"] == "create_session"

    def test_list_sessions(self) -> None:
        tool = list_sessions_tool()
        assert tool["name"] == "list_sessions"

    def test_kill_session(self) -> None:
        tool = kill_session_tool()
        assert "session_id" in tool["parameters"]["required"]

    def test_get_session_status(self) -> None:
        tool = get_session_status_tool()
        assert "session_id" in tool["parameters"]["required"]


class TestDebugTools:
    def test_analyze_error(self) -> None:
        tool = analyze_error_tool()
        assert tool["name"] == "analyze_error"

    def test_propose_fix(self) -> None:
        tool = propose_fix_tool()
        assert "new_code" in tool["parameters"]["required"]

    def test_explain_traceback(self) -> None:
        tool = explain_traceback_tool()
        assert "traceback_text" in tool["parameters"]["required"]

    def test_check_dependencies(self) -> None:
        tool = check_dependencies_tool()
        assert "cell_id" in tool["parameters"]["required"]


class TestUiTools:
    def test_list_components(self) -> None:
        tool = list_available_components_tool()
        assert tool["name"] == "list_available_components"

    def test_suggest_layout(self) -> None:
        tool = suggest_layout_tool()
        assert "description" in tool["parameters"]["required"]
