#!/usr/bin/env python3
"""Execution script for Atlassian Jira tools from Skills.

This script provides a command-line interface for discovering and executing
Jira tools through the internalized atlassian_tools package.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add project src to path for development
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from atlassian_tools._core.executor import execute_tool as _execute_tool
    from atlassian_tools._core.registry import get_registry
except ImportError as e:
    print(
        json.dumps(
            {
                "success": False,
                "error": f"Failed to import atlassian_tools: {e}. "
                "Please install the package: pip install -e .",
            },
            indent=2,
        ),
        file=sys.stderr,
    )
    sys.exit(1)


def format_output(data: dict) -> str:
    """Format output as pretty JSON.

    Args:
        data: Dictionary to format

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


async def list_tools() -> dict:
    """List all available Jira tools.

    Returns:
        Dictionary with success status and tool list
    """
    try:
        registry = get_registry()
        tools = registry.discover_tools(category="jira")

        return {"success": True, "tools": tools, "count": len(tools)}
    except Exception as e:
        return {"success": False, "error": f"Failed to list tools: {e}"}


async def get_tool_schema(tool_name: str) -> dict:
    """Get schema for a specific tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Dictionary with tool schema information
    """
    try:
        registry = get_registry()
        metadata = registry.get_tool_metadata(tool_name)

        return {
            "success": True,
            "tool": tool_name,
            "description": metadata.description,
            "category": metadata.category,
            "input_schema": metadata.input_schema,
            "output_schema": metadata.output_schema,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get schema for '{tool_name}': {e}",
        }


async def execute_tool(tool_name: str, input_data: dict) -> dict:
    """Execute a tool with given input.

    Args:
        tool_name: Name of the tool to execute
        input_data: Input parameters as dictionary

    Returns:
        Dictionary with execution results
    """
    try:
        result = await _execute_tool(tool_name, input_data)

        # Return the complete result structure
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "tool_name": result.tool_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute '{tool_name}': {e}",
            "tool_name": tool_name,
        }


async def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Execute Atlassian Jira tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available tools
  %(prog)s --list-tools

  # Get schema for a specific tool
  %(prog)s jira_get_issue --schema

  # Execute a tool
  %(prog)s jira_get_issue --input '{"issue_key": "PROJ-123"}'

  # Execute with specific fields
  %(prog)s jira_get_issue --input '{
    "issue_key": "PROJ-123",
    "fields": "summary,status,assignee",
    "comment_limit": 5
  }'
        """,
    )

    parser.add_argument("tool_name", nargs="?", help="Name of the tool to execute")

    parser.add_argument(
        "--input", type=str, help="JSON input for the tool (as a string)"
    )

    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available Jira tools",
    )

    parser.add_argument(
        "--schema",
        action="store_true",
        help="Show input/output schema for the specified tool",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True)",
    )

    args = parser.parse_args()

    # Handle --list-tools
    if args.list_tools:
        result = await list_tools()
        print(format_output(result))
        sys.exit(0 if result["success"] else 1)

    # Require tool_name for other operations
    if not args.tool_name:
        parser.print_help()
        sys.exit(1)

    # Handle --schema
    if args.schema:
        result = await get_tool_schema(args.tool_name)
        print(format_output(result))
        sys.exit(0 if result["success"] else 1)

    # Handle tool execution
    if args.input:
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError as e:
            error_result = {
                "success": False,
                "error": f"Invalid JSON input: {e}",
                "tool_name": args.tool_name,
            }
            print(format_output(error_result), file=sys.stderr)
            sys.exit(1)

        result = await execute_tool(args.tool_name, input_data)
        print(format_output(result))
        sys.exit(0 if result["success"] else 1)

    # No valid operation specified
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        error_result = {"success": False, "error": f"Unexpected error: {e}"}
        print(format_output(error_result), file=sys.stderr)
        sys.exit(1)
