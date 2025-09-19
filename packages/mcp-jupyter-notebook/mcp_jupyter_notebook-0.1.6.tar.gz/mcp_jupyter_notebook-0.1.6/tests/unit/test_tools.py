"""
Unit tests for notebook tools in tools.py using pytest and unittest.mock.
"""
import pytest
from unittest.mock import AsyncMock
from jupyter_agent_toolkit.notebook.types import NotebookCodeExecutionResult, NotebookMarkdownCellResult
from mcp_jupyter_notebook.tools import register_all_tools

def test_register_all_tools_registers_expected_tools(dummy_server, mock_session):
    """Test that all expected tools are registered on the server."""
    register_all_tools(dummy_server, mock_session)
    expected = {"notebook.markdown.add", "notebook.code.run", "notebook.packages.add"}
    assert expected.issubset(set(dummy_server.tools.keys()))

@pytest.mark.asyncio
async def test_notebook_markdown_add_calls_invoke_markdown_cell(monkeypatch, dummy_server, mock_session):
    """Test notebook_markdown_add tool calls invoke_markdown_cell and returns correct result."""
    # Ensure mock_result has all fields accessed by the tool function
    mock_result = NotebookMarkdownCellResult(
        status="ok",
        cell_index=42,
        error_message=None,
        elapsed_seconds=0.01
    )
    monkeypatch.setattr(
        "mcp_jupyter_notebook.tools.invoke_markdown_cell",
        AsyncMock(return_value=mock_result)
    )
    register_all_tools(dummy_server, mock_session)
    tool_fn = dummy_server.tools["notebook.markdown.add"]
    result = await tool_fn("# Hello")
    assert result == {
        "ok": True,
        "index": 42,
        "error": None,
        "elapsed_seconds": 0.01,
    }

@pytest.mark.asyncio
async def test_notebook_code_run_calls_invoke_code_cell(monkeypatch, dummy_server, mock_session):
    """Test notebook_code_run tool calls invoke_code_cell and returns expected result structure."""
    mock_result = NotebookCodeExecutionResult(
        status="ok",
        execution_count=1,
        cell_index=5,
        stdout="hi\n",
        stderr="",
        outputs=[],
        text_outputs=["hi"],
        formatted_output="hi",
        error_message=None,
        elapsed_seconds=0.02,
    )
    monkeypatch.setattr(
        "mcp_jupyter_notebook.tools.invoke_code_cell",
        AsyncMock(return_value=mock_result)
    )
    register_all_tools(dummy_server, mock_session)
    tool_fn = dummy_server.tools["notebook.code.run"]
    result = await tool_fn("print('hi')")
    assert result == {
        "ok": True,
        "cell_index": 5,
        "status": "ok",
        "stdout": "hi\n",
        "stderr": "",
        "outputs": [],
        "text_outputs": ["hi"],
        "formatted_output": "hi",
        "error_message": None,
        "elapsed_seconds": 0.02,
    }

@pytest.mark.asyncio
async def test_notebook_packages_add_calls_update_dependencies(monkeypatch, dummy_server, mock_session):
    """Test notebook_packages_add tool calls update_dependencies and returns correct packages."""
    # Patch check_package_availability and _run_json to avoid kernel execution
    monkeypatch.setattr(
        "jupyter_agent_toolkit.utils.packages.check_package_availability",
        AsyncMock(return_value={"pandas": True, "numpy": True})
    )
    monkeypatch.setattr(
        "jupyter_agent_toolkit.utils.packages._run_json",
        AsyncMock(return_value={"pandas": True, "numpy": True})
    )
    monkeypatch.setattr(
        "jupyter_agent_toolkit.utils.packages.update_dependencies",
        AsyncMock(return_value=True)
    )
    register_all_tools(dummy_server, mock_session)
    tool_fn = dummy_server.tools["notebook.packages.add"]
    result = await tool_fn(["pandas", "numpy"])
    assert result == {"ok": True, "packages": ["pandas", "numpy"]}