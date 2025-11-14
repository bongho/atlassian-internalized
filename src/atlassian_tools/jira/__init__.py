"""Jira tools for Atlassian integration.

This module provides type-safe functions for interacting with Jira,
including issue management, search, projects, sprints, and more.
"""

from atlassian_tools.jira.tools import jira_get_issue

__all__ = ["jira_get_issue"]
