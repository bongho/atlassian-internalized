"""Base protocols and types for atlassian_tools.

This module defines the core Tool protocol that all internalized tools follow,
providing type safety and a consistent interface across Jira and Confluence operations.
"""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

# Type variables for generic tool inputs and outputs
InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class Tool(Protocol[InputT, OutputT]):
    """Protocol defining the interface for an internalized tool.

    All tools must conform to this protocol to ensure type safety and
    consistent behavior across the internalized Atlassian API.

    Example:
        >>> async def my_tool(input: MyInput) -> MyOutput:
        ...     # Implementation
        ...     pass
        >>> my_tool.tool_name = "my_tool"
        >>> my_tool.input_schema = MyInput
        >>> my_tool.output_schema = MyOutput
    """

    tool_name: str
    """Unique identifier for the tool (e.g., 'jira_get_issue')"""

    input_schema: type[InputT]
    """Pydantic model class for validating input"""

    output_schema: type[OutputT]
    """Pydantic model class for output"""

    def __call__(self, input: InputT) -> Awaitable[OutputT]:
        """Execute the tool with validated input.

        Args:
            input: Validated input conforming to input_schema

        Returns:
            Tool output conforming to output_schema
        """
        ...


# Type alias for any tool function
AnyTool = Callable[[Any], Awaitable[Any]]


class ToolMetadata(BaseModel):
    """Metadata about a tool for discovery and documentation."""

    name: str
    """Tool name (e.g., 'jira_get_issue')"""

    description: str
    """Human-readable description of what the tool does"""

    category: str
    """Category: 'jira' or 'confluence'"""

    input_schema: dict[str, Any]
    """JSON schema for input validation"""

    output_schema: dict[str, Any]
    """JSON schema for output structure"""

    examples: list[dict[str, Any]] | None = None
    """Optional usage examples"""


class ToolExecutionResult(BaseModel):
    """Result of executing a tool."""

    success: bool
    """Whether the tool executed successfully"""

    data: dict[str, Any] | None = None
    """Output data if successful"""

    error: str | None = None
    """Error message if failed"""

    tool_name: str
    """Name of the tool that was executed"""


def create_tool_metadata(
    tool: AnyTool,
    category: str,
) -> ToolMetadata:
    """Extract metadata from a tool function.

    Args:
        tool: Tool function with attached metadata
        category: Tool category ('jira' or 'confluence')

    Returns:
        ToolMetadata object for discovery and documentation

    Raises:
        AttributeError: If tool is missing required metadata
    """
    return ToolMetadata(
        name=tool.tool_name,  # type: ignore[attr-defined]
        description=tool.__doc__ or "",
        category=category,
        input_schema=tool.input_schema.model_json_schema(),  # type: ignore[attr-defined]
        output_schema=tool.output_schema.model_json_schema(),  # type: ignore[attr-defined]
    )
