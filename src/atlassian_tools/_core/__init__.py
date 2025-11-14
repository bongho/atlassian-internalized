"""Core infrastructure for atlassian_tools.

This module contains the base protocols, registry, and execution engine
for the internalized Atlassian tools.
"""

from atlassian_tools._core.base import (
    Tool,
    ToolExecutionResult,
    ToolMetadata,
    create_tool_metadata,
)
from atlassian_tools._core.executor import execute_tool, validate_input
from atlassian_tools._core.registry import ToolRegistry, get_registry

__all__ = [
    "Tool",
    "ToolMetadata",
    "ToolExecutionResult",
    "create_tool_metadata",
    "ToolRegistry",
    "get_registry",
    "execute_tool",
    "validate_input",
]
