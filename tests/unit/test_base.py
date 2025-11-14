"""Tests for base protocols and types."""

import pytest
from pydantic import BaseModel, Field

from atlassian_tools._core.base import (
    ToolExecutionResult,
    ToolMetadata,
    create_tool_metadata,
)


class SampleInput(BaseModel):
    """Sample input schema."""

    test_field: str = Field(description="A test field")


class SampleOutput(BaseModel):
    """Sample output schema."""

    result: str = Field(description="Result field")


async def sample_tool(input: SampleInput) -> SampleOutput:
    """A sample tool function for testing."""
    return SampleOutput(result=f"Processed: {input.test_field}")


# Add metadata
sample_tool.tool_name = "sample_tool"  # type: ignore[attr-defined]
sample_tool.input_schema = SampleInput  # type: ignore[attr-defined]
sample_tool.output_schema = SampleOutput  # type: ignore[attr-defined]


class TestToolMetadata:
    """Test suite for ToolMetadata."""

    def test_tool_metadata_creation(self) -> None:
        """Test creating ToolMetadata directly."""
        metadata = ToolMetadata(
            name="test_tool",
            description="Test description",
            category="jira",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

        assert metadata.name == "test_tool"
        assert metadata.description == "Test description"
        assert metadata.category == "jira"
        assert metadata.input_schema == {"type": "object"}
        assert metadata.output_schema == {"type": "object"}

    def test_create_tool_metadata_from_function(self) -> None:
        """Test extracting metadata from a tool function."""
        metadata = create_tool_metadata(sample_tool, category="jira")

        assert metadata.name == "sample_tool"
        assert metadata.description == "A sample tool function for testing."
        assert metadata.category == "jira"
        assert isinstance(metadata.input_schema, dict)
        assert isinstance(metadata.output_schema, dict)

    def test_create_tool_metadata_missing_attributes(self) -> None:
        """Test that create_tool_metadata raises error for invalid tools."""

        async def invalid_tool(x: int) -> int:
            return x

        with pytest.raises(AttributeError):
            create_tool_metadata(invalid_tool, category="jira")  # type: ignore[arg-type]


class TestToolExecutionResult:
    """Test suite for ToolExecutionResult."""

    def test_success_result(self) -> None:
        """Test creating a successful execution result."""
        result = ToolExecutionResult(
            success=True,
            data={"key": "value"},
            tool_name="test_tool",
        )

        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
        assert result.tool_name == "test_tool"

    def test_error_result(self) -> None:
        """Test creating an error execution result."""
        result = ToolExecutionResult(
            success=False,
            error="Something went wrong",
            tool_name="test_tool",
        )

        assert result.success is False
        assert result.data is None
        assert result.error == "Something went wrong"
        assert result.tool_name == "test_tool"

    def test_result_serialization(self) -> None:
        """Test that results can be serialized."""
        result = ToolExecutionResult(
            success=True,
            data={"test": 123},
            tool_name="test_tool",
        )

        serialized = result.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["success"] is True
        assert serialized["data"] == {"test": 123}
        assert serialized["tool_name"] == "test_tool"
