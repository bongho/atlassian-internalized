"""Final tests to achieve 100% coverage."""

from unittest.mock import MagicMock, patch

import pytest


class TestPublicAPI:
    """Test public API functions in __init__.py."""

    def test_validate_input(self) -> None:
        """Test validate_input function."""
        from atlassian_tools import validate_input

        # Valid input
        is_valid, error = validate_input(
            "jira_get_issue", {"issue_key": "PROJ-123"}
        )
        assert is_valid is True
        assert error is None

        # Invalid input (missing required field)
        is_valid, error = validate_input("jira_get_issue", {})
        assert is_valid is False
        assert error is not None


class TestRegistry:
    """Test registry edge cases."""

    def test_search_tools_with_metadata_error(self) -> None:
        """Test search_tools when get_tool_metadata raises ValueError."""
        from atlassian_tools._core.registry import ToolRegistry

        registry = ToolRegistry()

        # First discover some tools
        tools = registry.discover_tools("jira")
        assert len(tools) > 0

        # Mock get_tool_metadata to raise ValueError for tools that don't
        # match the query in their name (forcing description lookup which fails)
        original_get_metadata = registry.get_tool_metadata

        def mock_get_metadata(tool_name: str):
            # Only raise for tools that would need description search
            if "issue" in tool_name.lower():
                # Return normally for these - they match the query in name
                return original_get_metadata(tool_name)
            else:
                # Raise ValueError for others to trigger the exception handler
                raise ValueError("Metadata loading failed")

        with patch.object(registry, "get_tool_metadata", side_effect=mock_get_metadata):
            # Search for "issue" - some tools match in name, some would need
            # description lookup which will fail and be caught
            results = registry.search_tools("issue")
            # Should still return results for tools that matched in name
            assert isinstance(results, list)
            assert len(results) > 0
