"""Tests for the tool registry."""

import pytest
from pydantic import BaseModel, Field

from atlassian_tools._core.registry import ToolRegistry, get_registry


# Dummy tool for testing
class DummyInput(BaseModel):
    """Test input schema."""

    value: str = Field(description="Test value")


class DummyOutput(BaseModel):
    """Test output schema."""

    result: str = Field(description="Test result")


async def dummy_tool(input: DummyInput) -> DummyOutput:
    """A dummy tool for testing."""
    return DummyOutput(result=f"processed: {input.value}")


# Attach metadata
dummy_tool.tool_name = "test_dummy_tool"  # type: ignore[attr-defined]
dummy_tool.input_schema = DummyInput  # type: ignore[attr-defined]
dummy_tool.output_schema = DummyOutput  # type: ignore[attr-defined]


class TestToolRegistry:
    """Test suite for ToolRegistry."""

    def test_registry_initialization(self) -> None:
        """Test that registry can be initialized."""
        registry = ToolRegistry()
        assert registry is not None
        assert isinstance(registry, ToolRegistry)

    def test_get_global_registry(self) -> None:
        """Test that global registry is a singleton."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_discover_tools_empty(self) -> None:
        """Test discovering tools when none are available."""
        registry = ToolRegistry()
        tools = registry.discover_tools()
        assert isinstance(tools, list)
        # May be empty since we haven't added any real tools yet

    def test_discover_tools_by_category(self) -> None:
        """Test discovering tools filtered by category."""
        registry = ToolRegistry()
        jira_tools = registry.discover_tools(category="jira")
        confluence_tools = registry.discover_tools(category="confluence")

        assert isinstance(jira_tools, list)
        assert isinstance(confluence_tools, list)

    def test_load_tool_invalid_name(self) -> None:
        """Test loading a tool with invalid name format."""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Invalid tool name format"):
            registry.load_tool("invalid")

    def test_load_tool_invalid_category(self) -> None:
        """Test loading a tool with invalid category."""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Invalid tool category"):
            registry.load_tool("invalid_tool_name")

    def test_load_tool_not_found(self) -> None:
        """Test loading a non-existent tool."""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Tool not found"):
            registry.load_tool("jira_nonexistent_tool")

    def test_search_tools_empty_query(self) -> None:
        """Test searching with empty results."""
        registry = ToolRegistry()
        results = registry.search_tools("nonexistent_xyz_123")
        assert results == []

    def test_get_loaded_tools_empty(self) -> None:
        """Test getting loaded tools when none are loaded."""
        registry = ToolRegistry()
        loaded = registry.get_loaded_tools()
        assert loaded == []

    def test_clear_cache(self) -> None:
        """Test clearing the registry cache."""
        registry = ToolRegistry()
        registry.clear_cache()
        assert registry.get_loaded_tools() == []


@pytest.mark.asyncio
async def test_dummy_tool_execution() -> None:
    """Test that our dummy tool works correctly."""
    input_data = DummyInput(value="test")
    output = await dummy_tool(input_data)

    assert isinstance(output, DummyOutput)
    assert output.result == "processed: test"
