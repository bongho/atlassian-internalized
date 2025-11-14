"""Tool execution engine.

This module provides the execution layer for running tools with
validated inputs and structured error handling.
"""

from typing import Any

from pydantic import ValidationError

from atlassian_tools._core.base import ToolExecutionResult
from atlassian_tools._core.registry import get_registry


async def execute_tool(
    tool_name: str,
    input_data: dict[str, Any],
) -> ToolExecutionResult:
    """Execute a tool with validated input.

    This function handles the complete execution flow:
    1. Load the tool from the registry
    2. Validate input against the tool's schema
    3. Execute the tool
    4. Return structured results

    Args:
        tool_name: Name of the tool to execute
        input_data: Input parameters as a dictionary

    Returns:
        ToolExecutionResult with success status and data/error

    Example:
        >>> result = await execute_tool(
        ...     'jira_get_issue',
        ...     {'issue_key': 'PROJ-123'}
        ... )
        >>> if result.success:
        ...     print(result.data)
        ... else:
        ...     print(result.error)
    """
    registry = get_registry()

    try:
        # Load the tool
        tool = registry.load_tool(tool_name)

        # Validate input
        input_schema = tool.input_schema  # type: ignore[attr-defined]
        validated_input = input_schema(**input_data)

        # Execute the tool
        output = await tool(validated_input)

        # Return success result
        return ToolExecutionResult(
            success=True,
            data=output.model_dump() if hasattr(output, "model_dump") else output,
            tool_name=tool_name,
        )

    except ValidationError as e:
        # Input validation failed
        return ToolExecutionResult(
            success=False,
            error=f"Input validation error: {e}",
            tool_name=tool_name,
        )

    except ValueError as e:
        # Tool not found or loading error
        return ToolExecutionResult(
            success=False,
            error=f"Tool error: {e}",
            tool_name=tool_name,
        )

    except Exception as e:
        # Execution error
        return ToolExecutionResult(
            success=False,
            error=f"Execution error: {type(e).__name__}: {e}",
            tool_name=tool_name,
        )


def validate_input(
    tool_name: str,
    input_data: dict[str, Any],
) -> tuple[bool, str | None]:
    """Validate input data against a tool's schema without executing.

    Args:
        tool_name: Name of the tool
        input_data: Input parameters to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None

    Example:
        >>> is_valid, error = validate_input(
        ...     'jira_get_issue',
        ...     {'issue_key': 'PROJ-123'}
        ... )
        >>> if not is_valid:
        ...     print(f"Validation error: {error}")
    """
    registry = get_registry()

    try:
        # Load the tool
        tool = registry.load_tool(tool_name)

        # Validate input
        input_schema = tool.input_schema  # type: ignore[attr-defined]
        input_schema(**input_data)

        return (True, None)

    except ValidationError as e:
        return (False, f"Input validation error: {e}")

    except ValueError as e:
        return (False, f"Tool error: {e}")

    except Exception as e:
        return (False, f"Unexpected error: {type(e).__name__}: {e}")
