"""Service container for dependency injection.

This module provides singleton access to service instances,
enabling easy dependency injection and testing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from atlassian_tools.confluence.service import ConfluenceService
    from atlassian_tools.jira.service import JiraService

# Singleton service instances
_jira_service: JiraService | None = None
_confluence_service: ConfluenceService | None = None


def get_jira_service() -> JiraService:
    """Get the Jira service singleton.

    Returns:
        JiraService instance configured with the default client.
    """
    global _jira_service
    if _jira_service is None:
        from atlassian_tools._core.http_client import get_jira_client
        from atlassian_tools.jira.service import JiraService

        client = get_jira_client()
        _jira_service = JiraService(client)
    return _jira_service


def get_confluence_service() -> ConfluenceService:
    """Get the Confluence service singleton.

    Returns:
        ConfluenceService instance configured with the default client.
    """
    global _confluence_service
    if _confluence_service is None:
        from atlassian_tools._core.http_client import get_confluence_client
        from atlassian_tools.confluence.service import ConfluenceService

        client = get_confluence_client()
        _confluence_service = ConfluenceService(client)
    return _confluence_service


def clear_service_cache() -> None:
    """Clear cached services (useful for testing)."""
    global _jira_service, _confluence_service
    _jira_service = None
    _confluence_service = None


__all__ = [
    "get_jira_service",
    "get_confluence_service",
    "clear_service_cache",
]
