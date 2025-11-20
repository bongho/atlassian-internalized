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
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


class JiraSearchInput(BaseModel):
    """Input schema for jira_search tool.

    This tool searches for Jira issues using JQL (Jira Query Language)
    and returns matching issues with specified fields.
    """

    jql: str = Field(
        description=(
            "JQL (Jira Query Language) query string. "
            "Examples: 'project = PROJ AND status = Open', "
            "'assignee = currentUser() AND updated >= -7d'"
        ),
        min_length=1,
        examples=[
            "project = PROJ AND status = 'In Progress'",
            "assignee = currentUser() ORDER BY updated DESC",
            "labels = bug AND priority = High",
        ],
    )

    fields: str | None = Field(
        default=None,
        description=(
            "Comma-separated list of fields to return, or '*all' for all fields. "
            "If not specified, returns default fields. "
            "Use '*navigable' for all navigable fields."
        ),
        examples=["summary,status,assignee", "*all", "*navigable"],
    )

    expand: str | None = Field(
        default=None,
        description=(
            "Comma-separated list of fields to expand. "
            "Common values: 'changelog', 'transitions', 'renderedFields'"
        ),
        examples=["changelog", "transitions,changelog"],
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of issues to return (1-100)",
    )

    start_at: int = Field(
        default=0,
        ge=0,
        description="Index of the first result to return (for pagination)",
    )


class JiraSearchOutput(BaseModel):
    """Output schema for jira_search tool.

    Returns search results with issues and pagination info,
    or an error message if the operation fails.
    """

    success: bool = Field(
        description="Whether the operation succeeded"
    )

    issues: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of matching issues (only present if success=True)",
    )

    total: int | None = Field(
        default=None,
        description="Total number of issues matching the JQL query",
    )

    start_at: int | None = Field(
        default=None,
        description="Index of the first result returned",
    )

    max_results: int | None = Field(
        default=None,
        description="Maximum results requested",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


# Phase 1: Additional Read Tools

class JiraGetAllProjectsInput(BaseModel):
    """Input schema for jira_get_all_projects tool."""

    expand: str | None = Field(
        default=None,
        description=(
            "Comma-separated list of fields to expand. "
            "Options: 'description', 'lead', 'issueTypes', 'url'"
        ),
        examples=["description,lead", "issueTypes"],
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of projects to return",
    )


class JiraGetAllProjectsOutput(BaseModel):
    """Output schema for jira_get_all_projects tool."""

    success: bool = Field(description="Whether the operation succeeded")

    projects: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of projects (only present if success=True)",
    )

    total: int | None = Field(
        default=None,
        description="Total number of projects",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


class JiraGetTransitionsInput(BaseModel):
    """Input schema for jira_get_transitions tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
        examples=["PROJ-123", "TASK-789"],
    )


class JiraGetTransitionsOutput(BaseModel):
    """Output schema for jira_get_transitions tool."""

    success: bool = Field(description="Whether the operation succeeded")

    transitions: list[dict[str, Any]] | None = Field(
        default=None,
        description="Available transitions for the issue",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


class JiraGetUserProfileInput(BaseModel):
    """Input schema for jira_get_user_profile tool."""

    account_id: str | None = Field(
        default=None,
        description=(
            "Atlassian account ID. If not provided, "
            "returns the current user's profile."
        ),
        examples=["5b10a2844c20165700ede21g"],
    )


class JiraGetUserProfileOutput(BaseModel):
    """Output schema for jira_get_user_profile tool."""

    success: bool = Field(description="Whether the operation succeeded")

    user: dict[str, Any] | None = Field(
        default=None,
        description="User profile data (only present if success=True)",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


# Phase 2: Write Tools

class JiraCreateIssueInput(BaseModel):
    """Input schema for jira_create_issue tool."""

    project_key: str = Field(
        description="Project key (e.g., 'PROJ', 'DSD')",
        min_length=1,
        examples=["PROJ", "DSD"],
    )

    summary: str = Field(
        description="Issue summary/title",
        min_length=1,
        examples=["Fix login bug", "Add new feature"],
    )

    issue_type: str = Field(
        default="Task",
        description="Issue type (e.g., 'Task', 'Bug', 'Story', '작업')",
        examples=["Task", "Bug", "Story", "작업"],
    )

    description: str | None = Field(
        default=None,
        description="Issue description (supports markdown/ADF)",
    )

    assignee_id: str | None = Field(
        default=None,
        description="Assignee's Atlassian account ID",
    )

    priority: str | None = Field(
        default=None,
        description="Priority name (e.g., 'High', 'Medium', 'Low')",
        examples=["High", "Medium", "Low"],
    )

    labels: list[str] | None = Field(
        default=None,
        description="List of labels to add",
    )

    components: list[str] | None = Field(
        default=None,
        description="List of component names to add",
    )

    parent_key: str | None = Field(
        default=None,
        description="Parent issue key for subtasks or epic link",
    )


class JiraCreateIssueOutput(BaseModel):
    """Output schema for jira_create_issue tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issue: dict[str, Any] | None = Field(
        default=None,
        description="Created issue data with key and id",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


class JiraUpdateIssueInput(BaseModel):
    """Input schema for jira_update_issue tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    summary: str | None = Field(
        default=None,
        description="New summary/title",
    )

    description: str | None = Field(
        default=None,
        description="New description",
    )

    assignee_id: str | None = Field(
        default=None,
        description="New assignee's account ID (use empty string to unassign)",
    )

    priority: str | None = Field(
        default=None,
        description="New priority name",
    )

    labels: list[str] | None = Field(
        default=None,
        description="New labels (replaces existing)",
    )


class JiraUpdateIssueOutput(BaseModel):
    """Output schema for jira_update_issue tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issue_key: str | None = Field(
        default=None,
        description="Updated issue key",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


class JiraAddCommentInput(BaseModel):
    """Input schema for jira_add_comment tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    body: str = Field(
        description="Comment body text",
        min_length=1,
    )


class JiraAddCommentOutput(BaseModel):
    """Output schema for jira_add_comment tool."""

    success: bool = Field(description="Whether the operation succeeded")

    comment_id: str | None = Field(
        default=None,
        description="Created comment ID",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


class JiraTransitionIssueInput(BaseModel):
    """Input schema for jira_transition_issue tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    transition_id: str = Field(
        description=(
            "Transition ID to execute. "
            "Use jira_get_transitions to find available IDs."
        ),
    )

    comment: str | None = Field(
        default=None,
        description="Optional comment to add with the transition",
    )


class JiraTransitionIssueOutput(BaseModel):
    """Output schema for jira_transition_issue tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issue_key: str | None = Field(
        default=None,
        description="Transitioned issue key",
    )

    new_status: str | None = Field(
        default=None,
        description="New status after transition",
    )

    error: str | None = Field(
        default=None,
        description=(
            "Error message if the operation failed "
            "(only present if success=False)"
        ),
    )


# Phase 3: Additional Read Tools

class JiraGetCommentsInput(BaseModel):
    """Input schema for jira_get_comments tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of comments to return",
    )

    order_by: str = Field(
        default="-created",
        description="Order by field (prefix with - for descending)",
    )


class JiraGetCommentsOutput(BaseModel):
    """Output schema for jira_get_comments tool."""

    success: bool = Field(description="Whether the operation succeeded")

    comments: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of comments",
    )

    total: int | None = Field(
        default=None,
        description="Total number of comments",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetWorklogInput(BaseModel):
    """Input schema for jira_get_worklog tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of worklogs to return",
    )


class JiraGetWorklogOutput(BaseModel):
    """Output schema for jira_get_worklog tool."""

    success: bool = Field(description="Whether the operation succeeded")

    worklogs: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of worklogs",
    )

    total: int | None = Field(
        default=None,
        description="Total time spent in seconds",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetWatchersInput(BaseModel):
    """Input schema for jira_get_watchers tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )


class JiraGetWatchersOutput(BaseModel):
    """Output schema for jira_get_watchers tool."""

    success: bool = Field(description="Whether the operation succeeded")

    watchers: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of watchers",
    )

    watch_count: int | None = Field(
        default=None,
        description="Total number of watchers",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetSprintIssuesInput(BaseModel):
    """Input schema for jira_get_sprint_issues tool."""

    sprint_id: int = Field(
        description="Sprint ID",
        ge=1,
    )

    fields: str | None = Field(
        default=None,
        description="Comma-separated list of fields to return",
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of issues to return",
    )


class JiraGetSprintIssuesOutput(BaseModel):
    """Output schema for jira_get_sprint_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issues: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of issues in the sprint",
    )

    total: int | None = Field(
        default=None,
        description="Total number of issues",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetBoardIssuesInput(BaseModel):
    """Input schema for jira_get_board_issues tool."""

    board_id: int = Field(
        description="Board ID",
        ge=1,
    )

    jql: str | None = Field(
        default=None,
        description="Additional JQL filter",
    )

    fields: str | None = Field(
        default=None,
        description="Comma-separated list of fields to return",
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of issues to return",
    )


class JiraGetBoardIssuesOutput(BaseModel):
    """Output schema for jira_get_board_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issues: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of issues on the board",
    )

    total: int | None = Field(
        default=None,
        description="Total number of issues",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetEpicIssuesInput(BaseModel):
    """Input schema for jira_get_epic_issues tool."""

    epic_key: str = Field(
        description="Epic issue key (e.g., 'PROJ-100')",
        min_length=1,
    )

    fields: str | None = Field(
        default=None,
        description="Comma-separated list of fields to return",
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of issues to return",
    )


class JiraGetEpicIssuesOutput(BaseModel):
    """Output schema for jira_get_epic_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issues: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of issues in the epic",
    )

    total: int | None = Field(
        default=None,
        description="Total number of issues",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


# Phase 4: Additional Write Tools

class JiraAssignIssueInput(BaseModel):
    """Input schema for jira_assign_issue tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    account_id: str | None = Field(
        default=None,
        description="Assignee account ID (None to unassign)",
    )


class JiraAssignIssueOutput(BaseModel):
    """Output schema for jira_assign_issue tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issue_key: str | None = Field(
        default=None,
        description="Assigned issue key",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraAddWatcherInput(BaseModel):
    """Input schema for jira_add_watcher tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    account_id: str = Field(
        description="Account ID of the user to add as watcher",
        min_length=1,
    )


class JiraAddWatcherOutput(BaseModel):
    """Output schema for jira_add_watcher tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraRemoveWatcherInput(BaseModel):
    """Input schema for jira_remove_watcher tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    account_id: str = Field(
        description="Account ID of the user to remove as watcher",
        min_length=1,
    )


class JiraRemoveWatcherOutput(BaseModel):
    """Output schema for jira_remove_watcher tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraAddWorklogInput(BaseModel):
    """Input schema for jira_add_worklog tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    time_spent: str = Field(
        description="Time spent (e.g., '2h 30m', '1d')",
        min_length=1,
    )

    comment: str | None = Field(
        default=None,
        description="Worklog comment",
    )

    started: str | None = Field(
        default=None,
        description="Start datetime (ISO format)",
    )


class JiraAddWorklogOutput(BaseModel):
    """Output schema for jira_add_worklog tool."""

    success: bool = Field(description="Whether the operation succeeded")

    worklog_id: str | None = Field(
        default=None,
        description="Created worklog ID",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraLinkIssuesInput(BaseModel):
    """Input schema for jira_link_issues tool."""

    inward_issue: str = Field(
        description="Inward issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    outward_issue: str = Field(
        description="Outward issue key (e.g., 'PROJ-456')",
        min_length=1,
    )

    link_type: str = Field(
        default="Relates",
        description="Link type (e.g., 'Blocks', 'Relates', 'Duplicates')",
    )


class JiraLinkIssuesOutput(BaseModel):
    """Output schema for jira_link_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraDeleteIssueInput(BaseModel):
    """Input schema for jira_delete_issue tool."""

    issue_key: str = Field(
        description="Jira issue key to delete (e.g., 'PROJ-123')",
        min_length=1,
    )

    delete_subtasks: bool = Field(
        default=True,
        description="Whether to delete subtasks as well",
    )


class JiraDeleteIssueOutput(BaseModel):
    """Output schema for jira_delete_issue tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


# Phase 7: Remaining Tools

class JiraGetProjectIssuesInput(BaseModel):
    """Input schema for jira_get_project_issues tool."""

    project_key: str = Field(
        description="Project key (e.g., 'PROJ')",
        min_length=1,
    )

    status: str | None = Field(
        default=None,
        description="Filter by status (e.g., 'Open', 'In Progress')",
    )

    max_results: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of issues to return",
    )


class JiraGetProjectIssuesOutput(BaseModel):
    """Output schema for jira_get_project_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    issues: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of issues",
    )

    total: int | None = Field(
        default=None,
        description="Total number of issues",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetFieldsInput(BaseModel):
    """Input schema for jira_get_fields tool."""

    pass  # No input required


class JiraGetFieldsOutput(BaseModel):
    """Output schema for jira_get_fields tool."""

    success: bool = Field(description="Whether the operation succeeded")

    fields: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of available fields",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetLinkTypesInput(BaseModel):
    """Input schema for jira_get_link_types tool."""

    pass  # No input required


class JiraGetLinkTypesOutput(BaseModel):
    """Output schema for jira_get_link_types tool."""

    success: bool = Field(description="Whether the operation succeeded")

    link_types: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of available link types",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetPrioritiesInput(BaseModel):
    """Input schema for jira_get_priorities tool."""

    pass  # No input required


class JiraGetPrioritiesOutput(BaseModel):
    """Output schema for jira_get_priorities tool."""

    success: bool = Field(description="Whether the operation succeeded")

    priorities: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of available priorities",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraGetResolutionsInput(BaseModel):
    """Input schema for jira_get_resolutions tool."""

    pass  # No input required


class JiraGetResolutionsOutput(BaseModel):
    """Output schema for jira_get_resolutions tool."""

    success: bool = Field(description="Whether the operation succeeded")

    resolutions: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of available resolutions",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraBatchCreateIssuesInput(BaseModel):
    """Input schema for jira_batch_create_issues tool."""

    issues: list[dict[str, Any]] = Field(
        description="List of issue data to create",
        min_length=1,
    )


class JiraBatchCreateIssuesOutput(BaseModel):
    """Output schema for jira_batch_create_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    created_issues: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of created issues with keys",
    )

    errors: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of errors for failed issues",
    )

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraUpdateCommentInput(BaseModel):
    """Input schema for jira_update_comment tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    comment_id: str = Field(
        description="Comment ID to update",
        min_length=1,
    )

    body: str = Field(
        description="New comment body",
        min_length=1,
    )


class JiraUpdateCommentOutput(BaseModel):
    """Output schema for jira_update_comment tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraDeleteCommentInput(BaseModel):
    """Input schema for jira_delete_comment tool."""

    issue_key: str = Field(
        description="Jira issue key (e.g., 'PROJ-123')",
        min_length=1,
    )

    comment_id: str = Field(
        description="Comment ID to delete",
        min_length=1,
    )


class JiraDeleteCommentOutput(BaseModel):
    """Output schema for jira_delete_comment tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )


class JiraUnlinkIssuesInput(BaseModel):
    """Input schema for jira_unlink_issues tool."""

    link_id: str = Field(
        description="Issue link ID to delete",
        min_length=1,
    )


class JiraUnlinkIssuesOutput(BaseModel):
    """Output schema for jira_unlink_issues tool."""

    success: bool = Field(description="Whether the operation succeeded")

    error: str | None = Field(
        default=None,
        description="Error message if the operation failed",
    )
