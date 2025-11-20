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
from atlassian_tools._core.config import (
    ConfluenceConfig,
    JiraConfig,
    clear_config_cache,
    get_confluence_config,
    get_jira_config,
)
from atlassian_tools._core.container import (
    clear_service_cache,
    get_confluence_service,
    get_jira_service,
)
from atlassian_tools._core.exceptions import (
    AtlassianError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServiceError,
    TimeoutError,
    ValidationError,
)
from atlassian_tools._core.executor import execute_tool, validate_input
from atlassian_tools._core.http_client import (
    AtlassianHttpClient,
    clear_client_cache,
    get_confluence_client,
    get_jira_client,
)
from atlassian_tools._core.registry import ToolRegistry, get_registry

__all__ = [
    # Base
    "Tool",
    "ToolMetadata",
    "ToolExecutionResult",
    "create_tool_metadata",
    # Registry
    "ToolRegistry",
    "get_registry",
    # Executor
    "execute_tool",
    "validate_input",
    # Config
    "JiraConfig",
    "ConfluenceConfig",
    "get_jira_config",
    "get_confluence_config",
    "clear_config_cache",
    # HTTP Client
    "AtlassianHttpClient",
    "get_jira_client",
    "get_confluence_client",
    "clear_client_cache",
    # Exceptions
    "AtlassianError",
    "ConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServiceError",
    "NetworkError",
    "TimeoutError",
    # Service Container
    "get_jira_service",
    "get_confluence_service",
    "clear_service_cache",
]
