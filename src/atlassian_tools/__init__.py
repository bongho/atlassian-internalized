"""Atlassian Tools - Internalized MCP tools for Jira and Confluence.

This package provides type-safe, importable Python functions for interacting
with Atlassian products (Jira and Confluence) following Anthropic's code
execution pattern for maximum token efficiency.

Example:
    >>> import atlassian_tools
    >>> tools = atlassian_tools.list_tools(category='jira')
    >>> result = await atlassian_tools.execute_tool('jira_get_issue', {'issue_key': 'PROJ-123'})
"""

from typing import Any

from atlassian_tools._core.executor import execute_tool as _execute_tool
from atlassian_tools._core.executor import validate_input as _validate_input
from atlassian_tools._core.registry import get_registry

__version__ = "0.1.0"


def list_tools(category: str | None = None) -> list[str]:
    """List available tools without loading them.

    Args:
        category: Optional filter ('jira' or 'confluence')

    Returns:
        List of tool names

    Example:
        >>> tools = list_tools(category='jira')
        >>> all_tools = list_tools()
    """
    registry = get_registry()
    return registry.discover_tools(category)


def search_tools(query: str) -> list[str]:
    """Search for tools by name or description.

    Args:
        query: Search term (case-insensitive)

    Returns:
        Matching tool names

    Example:
        >>> results = search_tools('issue')
    """
    registry = get_registry()
    return registry.search_tools(query)


def get_tool_info(tool_name: str) -> dict[str, Any]:
    """Get tool metadata without executing it.

    Args:
        tool_name: Tool to inspect

    Returns:
        Tool schema and documentation

    Example:
        >>> info = get_tool_info('jira_get_issue')
        >>> print(info['description'])
    """
    registry = get_registry()
    metadata = registry.get_tool_metadata(tool_name)
    return metadata.model_dump()


async def execute_tool(tool_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool with the given input.

    Args:
        tool_name: Tool to execute
        input_data: Input parameters as dict

    Returns:
        Tool execution result

    Example:
        >>> result = await execute_tool('jira_get_issue', {'issue_key': 'PROJ-123'})
        >>> if result['success']:
        ...     print(result['data'])
    """
    result = await _execute_tool(tool_name, input_data)
    return result.model_dump()


def validate_input(tool_name: str, input_data: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate input without executing the tool.

    Args:
        tool_name: Tool name
        input_data: Input to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_input('jira_get_issue', {'issue_key': 'PROJ-123'})
    """
    return _validate_input(tool_name, input_data)


__all__ = [
    "__version__",
    "list_tools",
    "search_tools",
    "get_tool_info",
    "execute_tool",
    "validate_input",
]
