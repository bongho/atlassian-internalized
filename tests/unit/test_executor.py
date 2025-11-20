"""Tests for the tool executor."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field, ValidationError

from atlassian_tools._core.executor import execute_tool, validate_input


class MockInput(BaseModel):
    """Mock input schema."""

    value: int = Field(description="A test value", ge=0)


class MockOutput(BaseModel):
    """Mock output schema."""

    doubled: int = Field(description="The doubled value")


async def mock_tool(input: MockInput) -> MockOutput:
    """A mock tool that doubles the input."""
    return MockOutput(doubled=input.value * 2)


# Add metadata
mock_tool.tool_name = "test_mock_tool"  # type: ignore[attr-defined]
mock_tool.input_schema = MockInput  # type: ignore[attr-defined]
mock_tool.output_schema = MockOutput  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_execute_tool_success() -> None:
    """Test successful tool execution."""
    mock_registry = MagicMock()
    mock_tool_instance = AsyncMock()
    mock_output = MockOutput(doubled=10)
    mock_tool_instance.return_value = mock_output
    mock_tool_instance.input_schema = MockInput

    mock_registry.load_tool.return_value = mock_tool_instance

    with patch("atlassian_tools._core.executor.get_registry", return_value=mock_registry):
        result = await execute_tool("test_tool", {"value": 5})

    assert result.success is True
    assert result.data == {"doubled": 10}
    assert result.error is None


@pytest.mark.asyncio
async def test_execute_tool_nonexistent() -> None:
    """Test executing a tool that doesn't exist."""
    result = await execute_tool("jira_nonexistent", {"test": "data"})

    assert result.success is False
    assert result.error is not None
    assert "Tool error" in result.error or "Tool not found" in result.error
    assert result.tool_name == "jira_nonexistent"


@pytest.mark.asyncio
async def test_execute_tool_invalid_input() -> None:
    """Test executing with invalid input data."""
    mock_registry = MagicMock()
    mock_tool_instance = MagicMock()
    mock_tool_instance.input_schema = MockInput

    mock_registry.load_tool.return_value = mock_tool_instance

    with patch("atlassian_tools._core.executor.get_registry", return_value=mock_registry):
        # Invalid: negative value
        result = await execute_tool("test_tool", {"value": -1})

    assert result.success is False
    assert "Input validation error" in result.error


@pytest.mark.asyncio
async def test_execute_tool_generic_exception() -> None:
    """Test handling of generic exceptions during execution."""
    mock_registry = MagicMock()
    mock_tool_instance = AsyncMock()
    mock_tool_instance.input_schema = MockInput
    mock_tool_instance.side_effect = RuntimeError("Unexpected error")

    mock_registry.load_tool.return_value = mock_tool_instance

    with patch("atlassian_tools._core.executor.get_registry", return_value=mock_registry):
        result = await execute_tool("test_tool", {"value": 5})

    assert result.success is False
    assert "Execution error" in result.error
    assert "RuntimeError" in result.error


def test_validate_input_success() -> None:
    """Test successful input validation."""
    mock_registry = MagicMock()
    mock_tool_instance = MagicMock()
    mock_tool_instance.input_schema = MockInput

    mock_registry.load_tool.return_value = mock_tool_instance

    with patch("atlassian_tools._core.executor.get_registry", return_value=mock_registry):
        is_valid, error = validate_input("test_tool", {"value": 5})

    assert is_valid is True
    assert error is None


def test_validate_input_invalid_tool() -> None:
    """Test validating input for non-existent tool."""
    is_valid, error = validate_input("jira_nonexistent", {"test": "data"})

    assert is_valid is False
    assert error is not None
    assert "Tool error" in error or "Tool not found" in error


def test_validate_input_validation_error() -> None:
    """Test validation error handling."""
    mock_registry = MagicMock()
    mock_tool_instance = MagicMock()
    mock_tool_instance.input_schema = MockInput

    mock_registry.load_tool.return_value = mock_tool_instance

    with patch("atlassian_tools._core.executor.get_registry", return_value=mock_registry):
        # Invalid: negative value
        is_valid, error = validate_input("test_tool", {"value": -1})

    assert is_valid is False
    assert error is not None
    assert "Input validation error" in error


def test_validate_input_generic_exception() -> None:
    """Test generic exception handling in validate_input."""
    mock_registry = MagicMock()
    mock_registry.load_tool.side_effect = RuntimeError("Unexpected error")

    with patch("atlassian_tools._core.executor.get_registry", return_value=mock_registry):
        is_valid, error = validate_input("test_tool", {"value": 5})

    assert is_valid is False
    assert error is not None
    assert "Unexpected error" in error
    assert "RuntimeError" in error


def test_validate_input_structure() -> None:
    """Test that validate_input returns correct structure."""
    is_valid, error = validate_input("jira_test", {"data": "test"})

    assert isinstance(is_valid, bool)
    assert error is None or isinstance(error, str)
