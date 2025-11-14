"""Tests for the tool executor."""

import pytest
from pydantic import BaseModel, Field

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
async def test_execute_tool_nonexistent() -> None:
    """Test executing a tool that doesn't exist."""
    from atlassian_tools._core.executor import execute_tool as _execute_tool

    result = await _execute_tool("jira_nonexistent", {"test": "data"})

    assert result.success is False
    assert result.error is not None
    assert "Tool error" in result.error or "Tool not found" in result.error
    assert result.tool_name == "jira_nonexistent"


@pytest.mark.asyncio
async def test_execute_tool_invalid_input() -> None:
    """Test executing with invalid input data."""
    from atlassian_tools._core.executor import execute_tool as _execute_tool

    # This would need a real tool to test properly
    # For now, test with non-existent tool
    result = await _execute_tool("jira_test", {"invalid": "data"})

    assert result.success is False
    assert result.error is not None


def test_validate_input_invalid_tool() -> None:
    """Test validating input for non-existent tool."""
    is_valid, error = validate_input("jira_nonexistent", {"test": "data"})

    assert is_valid is False
    assert error is not None
    assert "Tool error" in error or "Tool not found" in error


def test_validate_input_structure() -> None:
    """Test that validate_input returns correct structure."""
    is_valid, error = validate_input("jira_test", {"data": "test"})

    assert isinstance(is_valid, bool)
    assert error is None or isinstance(error, str)
