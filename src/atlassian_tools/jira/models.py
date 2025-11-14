"""Pydantic models for Jira tools.

This module defines input and output schemas for all Jira operations.
"""

from typing import Any

from pydantic import BaseModel, Field


class JiraGetIssueInput(BaseModel):
    """Input schema for jira_get_issue tool.

    This tool retrieves comprehensive information about a specific Jira issue,
    including fields, comments, attachments, and optional expanded data.
    """

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123', 'BUG-456')",
        min_length=1,
        examples=["PROJ-123", "TASK-789"],
    )

    fields: str | None = Field(
        default=None,
        description=(
            "Comma-separated list of fields to return, or '*all' for all fields. "
            "If not specified, returns default fields (summary, status, assignee, etc.)"
        ),
        examples=["summary,status,assignee", "*all", "description,priority"],
    )

    expand: str | None = Field(
        default=None,
        description=(
            "Comma-separated list of fields to expand. "
            "Common values: 'changelog', 'transitions', 'renderedFields'"
        ),
        examples=["changelog", "transitions,changelog"],
    )

    comment_limit: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Maximum number of comments to include (0 for none, max 100)",
    )


class JiraGetIssueOutput(BaseModel):
    """Output schema for jira_get_issue tool.

    Returns comprehensive issue data or an error message if the operation fails.
    """

    success: bool = Field(
        description="Whether the operation succeeded"
    )

    issue: dict[str, Any] | None = Field(
        default=None,
        description="Issue data with requested fields (only present if success=True)",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed (only present if success=False)",
    )
