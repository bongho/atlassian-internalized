"""Confluence tools for Atlassian integration.

This module provides type-safe functions for interacting with Confluence,
including page management, search, spaces, and comments.
"""

from atlassian_tools.confluence.tools import (
    confluence_add_comment,
    confluence_add_label,
    confluence_create_page,
    confluence_delete_page,
    confluence_get_comments,
    confluence_get_labels,
    confluence_get_page,
    confluence_get_page_ancestors,
    confluence_get_page_children,
    confluence_search,
    confluence_update_page,
)

__all__ = [
    "confluence_add_comment",
    "confluence_add_label",
    "confluence_create_page",
    "confluence_delete_page",
    "confluence_get_comments",
    "confluence_get_labels",
    "confluence_get_page",
    "confluence_get_page_ancestors",
    "confluence_get_page_children",
    "confluence_search",
    "confluence_update_page",
]
