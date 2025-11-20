"""Configuration management for Atlassian tools.

This module provides centralized configuration handling using pydantic-settings
for automatic environment variable loading and validation.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class JiraConfig(BaseSettings):
    """Configuration for Jira API connection."""

    url: str = Field(description="Jira instance URL")
    username: str = Field(description="Jira username (email)")
    api_token: str = Field(description="Jira API token")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    model_config = {
        "env_prefix": "JIRA_",
        "env_file": ".env",
        "extra": "ignore",
    }


class ConfluenceConfig(BaseSettings):
    """Configuration for Confluence API connection."""

    url: str = Field(description="Confluence instance URL")
    username: str = Field(description="Confluence username (email)")
    api_token: str = Field(description="Confluence API token")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    model_config = {
        "env_prefix": "CONFLUENCE_",
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache
def get_jira_config() -> JiraConfig:
    """Get Jira configuration (cached).

    Returns:
        JiraConfig instance with values from environment variables.

    Raises:
        ValidationError: If required environment variables are missing.
    """
    return JiraConfig()


@lru_cache
def get_confluence_config() -> ConfluenceConfig:
    """Get Confluence configuration (cached).

    Returns:
        ConfluenceConfig instance with values from environment variables.

    Raises:
        ValidationError: If required environment variables are missing.
    """
    return ConfluenceConfig()


def clear_config_cache() -> None:
    """Clear cached configurations (useful for testing)."""
    get_jira_config.cache_clear()
    get_confluence_config.cache_clear()


__all__ = [
    "JiraConfig",
    "ConfluenceConfig",
    "get_jira_config",
    "get_confluence_config",
    "clear_config_cache",
]
