"""Integration tests for Jira tools with registry and executor.

These tests validate the complete flow:
1. Tool discovery via registry
2. Tool loading
3. Metadata extraction
4. Tool execution via executor
"""

import pytest

from atlassian_tools._core.executor import execute_tool
from atlassian_tools._core.registry import get_registry


class TestJiraToolDiscovery:
    """Test Jira tool discovery through registry."""

    def test_discover_jira_tools(self) -> None:
        """Test that jira_get_issue is discoverable."""
        registry = get_registry()
        jira_tools = registry.discover_tools(category="jira")

        assert isinstance(jira_tools, list)
        assert "jira_get_issue" in jira_tools

    def test_discover_all_tools(self) -> None:
        """Test that jira_get_issue appears in all tools."""
        registry = get_registry()
        all_tools = registry.discover_tools()

        assert isinstance(all_tools, list)
        assert "jira_get_issue" in all_tools

    def test_search_for_issue_tools(self) -> None:
        """Test searching for issue-related tools."""
        registry = get_registry()
        results = registry.search_tools("issue")

        assert isinstance(results, list)
        assert "jira_get_issue" in results


class TestJiraToolLoading:
    """Test loading Jira tools from registry."""

    def test_load_jira_get_issue(self) -> None:
        """Test loading jira_get_issue tool."""
        registry = get_registry()
        tool = registry.load_tool("jira_get_issue")

        assert tool is not None
        assert callable(tool)
        assert hasattr(tool, "tool_name")
        assert tool.tool_name == "jira_get_issue"  # type: ignore[attr-defined]

    def test_loaded_tool_has_metadata(self) -> None:
        """Test that loaded tool has all required metadata."""
        registry = get_registry()
        tool = registry.load_tool("jira_get_issue")

        # Tool protocol requirements
        assert hasattr(tool, "tool_name")
        assert hasattr(tool, "input_schema")
        assert hasattr(tool, "output_schema")

        # Verify schemas are Pydantic models
        from pydantic import BaseModel

        assert issubclass(tool.input_schema, BaseModel)  # type: ignore[attr-defined]
        assert issubclass(tool.output_schema, BaseModel)  # type: ignore[attr-defined]

    def test_get_loaded_tools(self) -> None:
        """Test tracking of loaded tools."""
        registry = get_registry()

        # Clear cache first
        registry.clear_cache()
        assert "jira_get_issue" not in registry.get_loaded_tools()

        # Load tool
        registry.load_tool("jira_get_issue")
        assert "jira_get_issue" in registry.get_loaded_tools()


class TestJiraToolMetadata:
    """Test metadata extraction for Jira tools."""

    def test_get_tool_metadata(self) -> None:
        """Test getting metadata for jira_get_issue."""
        registry = get_registry()
        metadata = registry.get_tool_metadata("jira_get_issue")

        assert metadata.name == "jira_get_issue"
        assert metadata.category == "jira"
        assert metadata.description  # Should have docstring
        assert isinstance(metadata.input_schema, dict)
        assert isinstance(metadata.output_schema, dict)

    def test_metadata_has_input_schema(self) -> None:
        """Test that metadata includes input schema."""
        registry = get_registry()
        metadata = registry.get_tool_metadata("jira_get_issue")

        input_schema = metadata.input_schema
        assert "properties" in input_schema
        assert "issue_key" in input_schema["properties"]
        assert "comment_limit" in input_schema["properties"]

    def test_metadata_has_output_schema(self) -> None:
        """Test that metadata includes output schema."""
        registry = get_registry()
        metadata = registry.get_tool_metadata("jira_get_issue")

        output_schema = metadata.output_schema
        assert "properties" in output_schema
        assert "success" in output_schema["properties"]
        assert "issue" in output_schema["properties"]
        assert "error" in output_schema["properties"]


class TestJiraToolExecution:
    """Test tool execution through executor (with mocking)."""

    @pytest.mark.asyncio
    async def test_execute_tool_missing_env_vars(self) -> None:
        """Test executing tool without environment variables."""
        from unittest.mock import patch

        with patch.dict("os.environ", {}, clear=True):
            result = await execute_tool(
                "jira_get_issue", {"issue_key": "PROJ-123"}
            )

        # Executor succeeded (tool was called), but tool itself failed
        assert result.success is True
        assert result.data is not None
        assert result.data["success"] is False  # Tool's internal success
        assert "JIRA_URL" in result.data["error"]
        assert result.tool_name == "jira_get_issue"

    @pytest.mark.asyncio
    async def test_execute_tool_invalid_input(self) -> None:
        """Test executing tool with invalid input."""
        result = await execute_tool("jira_get_issue", {"invalid_field": "value"})

        assert result.success is False
        assert result.error is not None
        assert "validation error" in result.error.lower()
        assert result.tool_name == "jira_get_issue"

    @pytest.mark.asyncio
    async def test_execute_tool_empty_issue_key(self) -> None:
        """Test executing tool with empty issue key."""
        result = await execute_tool("jira_get_issue", {"issue_key": ""})

        assert result.success is False
        assert result.error is not None
        assert "validation error" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_tool_invalid_comment_limit(self) -> None:
        """Test executing tool with invalid comment limit."""
        result = await execute_tool(
            "jira_get_issue", {"issue_key": "PROJ-123", "comment_limit": -1}
        )

        assert result.success is False
        assert result.error is not None
        assert "validation error" in result.error.lower()


class TestEndToEndFlow:
    """Test complete end-to-end flow of tool usage."""

    @pytest.mark.asyncio
    async def test_discover_load_execute_flow(self) -> None:
        """Test the complete flow from discovery to execution."""
        from unittest.mock import patch

        registry = get_registry()

        # Step 1: Discover tools
        tools = registry.discover_tools(category="jira")
        assert "jira_get_issue" in tools

        # Step 2: Get metadata (without loading implementation)
        metadata = registry.get_tool_metadata("jira_get_issue")
        assert metadata.name == "jira_get_issue"

        # Step 3: Execute tool (will fail due to missing env vars, but tests flow)
        with patch.dict("os.environ", {}, clear=True):
            result = await execute_tool(
                "jira_get_issue", {"issue_key": "PROJ-123"}
            )

        # Should get error about missing env vars
        # Executor success but tool internal failure
        assert result.success is True
        assert result.data["success"] is False
        assert "JIRA_URL" in result.data["error"]

    def test_progressive_loading_benefit(self) -> None:
        """Test that tools aren't loaded until actually needed."""
        registry = get_registry()
        registry.clear_cache()

        # Discovery should not load tools
        tools = registry.discover_tools(category="jira")
        assert "jira_get_issue" in tools
        assert "jira_get_issue" not in registry.get_loaded_tools()

        # Getting metadata should load the tool
        metadata = registry.get_tool_metadata("jira_get_issue")
        assert metadata.name == "jira_get_issue"
        assert "jira_get_issue" in registry.get_loaded_tools()


class TestPublicAPI:
    """Test the public API functions."""

    def test_list_tools_jira(self) -> None:
        """Test public list_tools function for Jira."""
        import atlassian_tools

        tools = atlassian_tools.list_tools(category="jira")
        assert isinstance(tools, list)
        assert "jira_get_issue" in tools

    def test_search_tools(self) -> None:
        """Test public search_tools function."""
        import atlassian_tools

        results = atlassian_tools.search_tools("issue")
        assert isinstance(results, list)
        assert "jira_get_issue" in results

    def test_get_tool_info(self) -> None:
        """Test public get_tool_info function."""
        import atlassian_tools

        info = atlassian_tools.get_tool_info("jira_get_issue")
        assert isinstance(info, dict)
        assert info["name"] == "jira_get_issue"
        assert info["category"] == "jira"
        assert "input_schema" in info
        assert "output_schema" in info

    @pytest.mark.asyncio
    async def test_execute_tool_public_api(self) -> None:
        """Test public execute_tool function."""
        import atlassian_tools
        from unittest.mock import patch

        with patch.dict("os.environ", {}, clear=True):
            result = await atlassian_tools.execute_tool(
                "jira_get_issue", {"issue_key": "PROJ-123"}
            )

        assert isinstance(result, dict)
        # Result is already unwrapped by public API
        assert "success" in result
        assert "data" in result
        assert result["success"] is True  # Execution succeeded
        assert result["data"]["success"] is False  # Tool failed
        assert "JIRA_URL" in result["data"]["error"]
