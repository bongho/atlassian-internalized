"""Tool registry for discovery and lazy loading.

This module implements the tool discovery and loading system, enabling
progressive loading of tools to minimize token usage.
"""

import importlib
import importlib.util
from pathlib import Path

from atlassian_tools._core.base import AnyTool, ToolMetadata, create_tool_metadata


class ToolRegistry:
    """Manages tool discovery and lazy loading.

    The registry enables progressive discovery and loading of tools,
    loading only the tools needed for a specific operation.

    Example:
        >>> registry = ToolRegistry()
        >>> tools = registry.discover_tools(category='jira')
        >>> tool = registry.load_tool('jira_get_issue')
        >>> metadata = registry.get_tool_metadata('jira_get_issue')
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, AnyTool] = {}
        self._metadata_cache: dict[str, ToolMetadata] = {}
        self._loaded_modules: set[str] = set()

    def discover_tools(self, category: str | None = None) -> list[str]:
        """Discover available tools without loading them.

        This method scans the package structure to find available tools
        without actually importing and loading their implementations.

        Args:
            category: Optional category filter ('jira' or 'confluence')
                     If None, returns all tools.

        Returns:
            List of tool names (e.g., ['jira_get_issue', 'jira_create_issue'])

        Example:
            >>> registry = ToolRegistry()
            >>> jira_tools = registry.discover_tools('jira')
            >>> all_tools = registry.discover_tools()
        """
        tools: list[str] = []
        base_path = Path(__file__).parent.parent

        # Determine which categories to scan
        categories = [category] if category else ["jira", "confluence"]

        for cat in categories:
            cat_path = base_path / cat
            if not cat_path.exists():
                continue

            # Try to import the category module to get __all__
            try:
                module_name = f"atlassian_tools.{cat}"
                spec = importlib.util.find_spec(module_name)
                if spec and spec.loader:
                    module = importlib.import_module(module_name)

                    # Get exported tools from __all__
                    exported = getattr(module, "__all__", [])
                    for name in exported:
                        obj = getattr(module, name, None)
                        if obj and callable(obj) and hasattr(obj, "tool_name"):
                            tools.append(obj.tool_name)
            except (ImportError, AttributeError):
                # If module doesn't exist or has issues, skip it
                continue

        return sorted(tools)

    def load_tool(self, tool_name: str) -> AnyTool:
        """Lazily load a specific tool by name.

        Args:
            tool_name: Name of the tool to load (e.g., 'jira_get_issue')

        Returns:
            The tool function

        Raises:
            ValueError: If tool name is invalid or tool not found

        Example:
            >>> registry = ToolRegistry()
            >>> tool = registry.load_tool('jira_get_issue')
            >>> result = await tool(input_data)
        """
        # Return cached tool if already loaded
        if tool_name in self._tools:
            return self._tools[tool_name]

        # Parse tool name to determine category and function
        # Format: 'category_function_name'
        parts = tool_name.split("_", 1)
        if len(parts) < 2:
            msg = f"Invalid tool name format: {tool_name}"
            raise ValueError(msg)

        category = parts[0]
        if category not in ("jira", "confluence"):
            msg = f"Invalid tool category: {category}"
            raise ValueError(msg)

        # Import the category module
        module_name = f"atlassian_tools.{category}"
        try:
            module = importlib.import_module(module_name)
            self._loaded_modules.add(module_name)
        except ImportError as e:
            msg = f"Failed to import module {module_name}: {e}"
            raise ValueError(msg) from e

        # Find the tool function
        for attr_name in dir(module):
            obj = getattr(module, attr_name, None)
            if (
                callable(obj)
                and hasattr(obj, "tool_name")
                and obj.tool_name == tool_name
            ):
                tool_func: AnyTool = obj
                self._tools[tool_name] = tool_func
                return tool_func

        msg = f"Tool not found: {tool_name}"
        raise ValueError(msg)

    def get_tool_metadata(self, tool_name: str) -> ToolMetadata:
        """Get metadata for a tool without executing it.

        Args:
            tool_name: Name of the tool

        Returns:
            ToolMetadata containing schemas and documentation

        Raises:
            ValueError: If tool not found

        Example:
            >>> registry = ToolRegistry()
            >>> metadata = registry.get_tool_metadata('jira_get_issue')
            >>> print(metadata.description)
            >>> print(metadata.input_schema)
        """
        # Return cached metadata if available
        if tool_name in self._metadata_cache:
            return self._metadata_cache[tool_name]

        # Load the tool to get its metadata
        tool = self.load_tool(tool_name)

        # Determine category
        category = tool_name.split("_", 1)[0]

        # Create and cache metadata
        metadata = create_tool_metadata(tool, category)
        self._metadata_cache[tool_name] = metadata

        return metadata

    def search_tools(self, query: str) -> list[str]:
        """Search for tools by name or description.

        Args:
            query: Search term (case-insensitive)

        Returns:
            List of matching tool names

        Example:
            >>> registry = ToolRegistry()
            >>> results = registry.search_tools('issue')
            >>> # Returns: ['jira_get_issue', 'jira_create_issue', ...]
        """
        query_lower = query.lower()
        all_tools = self.discover_tools()

        matching_tools = []
        for tool_name in all_tools:
            # Match against tool name
            if query_lower in tool_name.lower():
                matching_tools.append(tool_name)
                continue

            # Try to match against description (requires loading metadata)
            try:
                metadata = self.get_tool_metadata(tool_name)
                if query_lower in metadata.description.lower():
                    matching_tools.append(tool_name)
            except ValueError:
                # Skip if metadata can't be loaded
                continue

        return sorted(matching_tools)

    def get_loaded_tools(self) -> list[str]:
        """Get list of currently loaded tools.

        Returns:
            List of tool names that have been loaded into memory

        Example:
            >>> registry = ToolRegistry()
            >>> registry.load_tool('jira_get_issue')
            >>> print(registry.get_loaded_tools())
            ['jira_get_issue']
        """
        return sorted(self._tools.keys())

    def clear_cache(self) -> None:
        """Clear all cached tools and metadata.

        This forces tools to be reloaded on next access,
        useful for development and testing.
        """
        self._tools.clear()
        self._metadata_cache.clear()
        self._loaded_modules.clear()


# Global singleton registry instance
_global_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Get the global tool registry instance.

    Returns:
        The singleton ToolRegistry instance

    Example:
        >>> from atlassian_tools._core.registry import get_registry
        >>> registry = get_registry()
        >>> tools = registry.discover_tools()
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
