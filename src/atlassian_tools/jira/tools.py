"""Jira tool implementations.

This module contains the actual implementation of Jira tools that interact
with the Jira API through the atlassian-python-api library.
"""

import os
from typing import Any

from atlassian import Jira

from atlassian_tools.jira.models import JiraGetIssueInput, JiraGetIssueOutput


def _get_jira_client() -> Jira:
    """Get configured Jira client from environment variables.

    Returns:
        Configured Jira client instance

    Raises:
        ValueError: If required environment variables are not set
    """
    jira_url = os.environ.get("JIRA_URL")
    jira_username = os.environ.get("JIRA_USERNAME")
    jira_api_token = os.environ.get("JIRA_API_TOKEN")

    if not jira_url:
        msg = "JIRA_URL environment variable is required"
        raise ValueError(msg)

    if not jira_username:
        msg = "JIRA_USERNAME environment variable is required"
        raise ValueError(msg)

    if not jira_api_token:
        msg = "JIRA_API_TOKEN environment variable is required"
        raise ValueError(msg)

    return Jira(url=jira_url, username=jira_username, password=jira_api_token)


async def jira_get_issue(input: JiraGetIssueInput) -> JiraGetIssueOutput:
    """Get details of a specific Jira issue.

    Retrieves comprehensive information about a Jira issue including
    fields, comments, attachments, and optional expanded data.

    Args:
        input: Validated input containing issue_key and optional parameters

    Returns:
        JiraGetIssueOutput with success status and issue data or error

    Example:
        >>> from atlassian_tools.jira.models import JiraGetIssueInput
        >>> input_data = JiraGetIssueInput(issue_key="PROJ-123", comment_limit=5)
        >>> result = await jira_get_issue(input_data)
        >>> if result.success:
        ...     print(result.issue["summary"])

    Note:
        Requires JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment
        variables to be set.
    """
    try:
        # Initialize Jira client
        jira = _get_jira_client()

        # Determine fields to request
        fields = input.fields if input.fields else "*all"

        # Fetch issue from Jira API
        issue_data = jira.issue(key=input.issue_key, fields=fields, expand=input.expand)

        if not isinstance(issue_data, dict):
            return JiraGetIssueOutput(
                success=False, error="Invalid response from Jira API"
            )

        # Simplify the issue data for response
        simplified_issue = _simplify_issue_data(issue_data, input)

        return JiraGetIssueOutput(success=True, issue=simplified_issue)

    except Exception as e:
        error_message = str(e)

        # Provide more specific error messages
        if "404" in error_message or "does not exist" in error_message.lower():
            error_message = f"Issue {input.issue_key} not found"
        elif "401" in error_message or "403" in error_message:
            error_message = "Authentication failed. Check your credentials"
        elif "JIRA_" in error_message:
            # Environment variable error - pass through as is
            pass
        else:
            # Generic error
            error_message = f"Error fetching issue: {error_message}"

        return JiraGetIssueOutput(success=False, error=error_message)


def _simplify_issue_data(
    issue_data: dict[str, Any], input: JiraGetIssueInput
) -> dict[str, Any]:
    """Simplify raw Jira issue data for cleaner output.

    Args:
        issue_data: Raw issue data from Jira API
        input: Original input to determine what to include

    Returns:
        Simplified issue dictionary
    """
    result: dict[str, Any] = {
        "key": issue_data.get("key"),
        "id": issue_data.get("id"),
        "self": issue_data.get("self"),
    }

    fields = issue_data.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}

    # Always include core fields
    simplified_fields: dict[str, Any] = {}

    if "summary" in fields:
        simplified_fields["summary"] = fields["summary"]

    if "description" in fields:
        simplified_fields["description"] = fields["description"]

    if "status" in fields and isinstance(fields["status"], dict):
        simplified_fields["status"] = {
            "name": fields["status"].get("name"),
            "category": fields["status"]
            .get("statusCategory", {})
            .get("name"),
        }

    if "issuetype" in fields and isinstance(fields["issuetype"], dict):
        simplified_fields["issue_type"] = {
            "name": fields["issuetype"].get("name")
        }

    if "priority" in fields and fields["priority"]:
        if isinstance(fields["priority"], dict):
            simplified_fields["priority"] = {
                "name": fields["priority"].get("name")
            }

    if "assignee" in fields:
        assignee = fields["assignee"]
        if assignee and isinstance(assignee, dict):
            simplified_fields["assignee"] = {
                "display_name": assignee.get("displayName"),
                "email": assignee.get("emailAddress"),
            }
        else:
            simplified_fields["assignee"] = None

    if "reporter" in fields and isinstance(fields["reporter"], dict):
        simplified_fields["reporter"] = {
            "display_name": fields["reporter"].get("displayName"),
            "email": fields["reporter"].get("emailAddress"),
        }

    if "created" in fields:
        simplified_fields["created"] = fields["created"]

    if "updated" in fields:
        simplified_fields["updated"] = fields["updated"]

    if "labels" in fields:
        simplified_fields["labels"] = fields["labels"]

    if "components" in fields and isinstance(fields["components"], list):
        simplified_fields["components"] = [
            comp.get("name") for comp in fields["components"] if isinstance(comp, dict)
        ]

    # Handle comments based on comment_limit
    if input.comment_limit > 0 and "comment" in fields:
        comment_data = fields["comment"]
        if isinstance(comment_data, dict) and "comments" in comment_data:
            comments = comment_data["comments"][: input.comment_limit]
            simplified_fields["comments"] = [
                {
                    "author": (
                        comment.get("author", {}).get("displayName")
                        if isinstance(comment.get("author"), dict)
                        else None
                    ),
                    "body": comment.get("body"),
                    "created": comment.get("created"),
                }
                for comment in comments
                if isinstance(comment, dict)
            ]

    # Handle attachments
    if "attachment" in fields and isinstance(fields["attachment"], list):
        simplified_fields["attachments"] = [
            {
                "filename": att.get("filename"),
                "size": att.get("size"),
                "content_type": att.get("mimeType"),
                "url": att.get("content"),
            }
            for att in fields["attachment"]
            if isinstance(att, dict)
        ]

    result["fields"] = simplified_fields

    # Include expanded data if requested
    if input.expand:
        if "changelog" in issue_data:
            result["changelog"] = issue_data["changelog"]
        if "transitions" in issue_data:
            result["transitions"] = issue_data["transitions"]

    return result


# Attach Tool protocol metadata
jira_get_issue.tool_name = "jira_get_issue"  # type: ignore[attr-defined]
jira_get_issue.input_schema = JiraGetIssueInput  # type: ignore[attr-defined]
jira_get_issue.output_schema = JiraGetIssueOutput  # type: ignore[attr-defined]
