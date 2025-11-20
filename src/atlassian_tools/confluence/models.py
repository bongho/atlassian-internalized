"""Pydantic models for Confluence tools.

This module defines input and output schemas for all Confluence operations.
"""

from typing import Any

from pydantic import BaseModel, Field

# Phase 5: Read Tools

class ConfluenceGetPageInput(BaseModel):
    """Input schema for confluence_get_page tool."""

    page_id: str = Field(
        description="Confluence page ID",
        min_length=1,
    )

    expand: str | None = Field(
        default=None,
        description="Comma-separated fields to expand (e.g., 'body.storage,version')",
    )


class ConfluenceGetPageOutput(BaseModel):
    """Output schema for confluence_get_page tool."""

    success: bool = Field(description="Whether the operation succeeded")

    page: dict[str, Any] | None = Field(
        default=None,
        description="Page data",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceSearchInput(BaseModel):
    """Input schema for confluence_search tool."""

    cql: str = Field(
        description="Confluence Query Language (CQL) query",
        min_length=1,
    )

    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    )

    start: int = Field(
        default=0,
        ge=0,
        description="Starting index for pagination",
    )


class ConfluenceSearchOutput(BaseModel):
    """Output schema for confluence_search tool."""

    success: bool = Field(description="Whether the operation succeeded")

    results: list[dict[str, Any]] | None = Field(
        default=None,
        description="Search results",
    )

    total: int | None = Field(
        default=None,
        description="Total number of results",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceGetPageChildrenInput(BaseModel):
    """Input schema for confluence_get_page_children tool."""

    page_id: str = Field(
        description="Parent page ID",
        min_length=1,
    )

    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum number of children to return",
    )


class ConfluenceGetPageChildrenOutput(BaseModel):
    """Output schema for confluence_get_page_children tool."""

    success: bool = Field(description="Whether the operation succeeded")

    children: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of child pages",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceGetPageAncestorsInput(BaseModel):
    """Input schema for confluence_get_page_ancestors tool."""

    page_id: str = Field(
        description="Page ID to get ancestors for",
        min_length=1,
    )


class ConfluenceGetPageAncestorsOutput(BaseModel):
    """Output schema for confluence_get_page_ancestors tool."""

    success: bool = Field(description="Whether the operation succeeded")

    ancestors: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of ancestor pages",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceGetLabelsInput(BaseModel):
    """Input schema for confluence_get_labels tool."""

    page_id: str = Field(
        description="Page ID to get labels for",
        min_length=1,
    )


class ConfluenceGetLabelsOutput(BaseModel):
    """Output schema for confluence_get_labels tool."""

    success: bool = Field(description="Whether the operation succeeded")

    labels: list[str] | None = Field(
        default=None,
        description="List of label names",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceGetCommentsInput(BaseModel):
    """Input schema for confluence_get_comments tool."""

    page_id: str = Field(
        description="Page ID to get comments for",
        min_length=1,
    )

    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum number of comments to return",
    )


class ConfluenceGetCommentsOutput(BaseModel):
    """Output schema for confluence_get_comments tool."""

    success: bool = Field(description="Whether the operation succeeded")

    comments: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of comments",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


# Phase 6: Write Tools

class ConfluenceCreatePageInput(BaseModel):
    """Input schema for confluence_create_page tool."""

    space_key: str = Field(
        description="Space key where the page will be created",
        min_length=1,
    )

    title: str = Field(
        description="Page title",
        min_length=1,
    )

    body: str = Field(
        description="Page body content (HTML or storage format)",
    )

    parent_id: str | None = Field(
        default=None,
        description="Parent page ID",
    )


class ConfluenceCreatePageOutput(BaseModel):
    """Output schema for confluence_create_page tool."""

    success: bool = Field(description="Whether the operation succeeded")

    page_id: str | None = Field(
        default=None,
        description="Created page ID",
    )

    page_url: str | None = Field(
        default=None,
        description="URL to the created page",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceUpdatePageInput(BaseModel):
    """Input schema for confluence_update_page tool."""

    page_id: str = Field(
        description="Page ID to update",
        min_length=1,
    )

    title: str | None = Field(
        default=None,
        description="New page title",
    )

    body: str | None = Field(
        default=None,
        description="New page body content",
    )

    version_number: int = Field(
        description="Current version number (required for update)",
        ge=1,
    )


class ConfluenceUpdatePageOutput(BaseModel):
    """Output schema for confluence_update_page tool."""

    success: bool = Field(description="Whether the operation succeeded")

    new_version: int | None = Field(
        default=None,
        description="New version number after update",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceDeletePageInput(BaseModel):
    """Input schema for confluence_delete_page tool."""

    page_id: str = Field(
        description="Page ID to delete",
        min_length=1,
    )


class ConfluenceDeletePageOutput(BaseModel):
    """Output schema for confluence_delete_page tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceAddLabelInput(BaseModel):
    """Input schema for confluence_add_label tool."""

    page_id: str = Field(
        description="Page ID to add label to",
        min_length=1,
    )

    label: str = Field(
        description="Label name to add",
        min_length=1,
    )


class ConfluenceAddLabelOutput(BaseModel):
    """Output schema for confluence_add_label tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class ConfluenceAddCommentInput(BaseModel):
    """Input schema for confluence_add_comment tool."""

    page_id: str = Field(
        description="Page ID to add comment to",
        min_length=1,
    )

    body: str = Field(
        description="Comment body content",
        min_length=1,
    )


class ConfluenceAddCommentOutput(BaseModel):
    """Output schema for confluence_add_comment tool."""

    success: bool = Field(description="Whether the operation succeeded")

    comment_id: str | None = Field(
        default=None,
        description="Created comment ID",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )
