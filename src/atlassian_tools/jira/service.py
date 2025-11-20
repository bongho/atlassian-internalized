"""Jira Service Layer.

This module provides the JiraService class that encapsulates all Jira API
operations with proper error handling and data transformation.
"""

from typing import Any

from atlassian_tools._core.http_client import AtlassianHttpClient


class JiraService:
    """Service class for Jira API operations.

    Encapsulates business logic and data transformation for Jira operations.
    Uses AtlassianHttpClient for HTTP communication.
    """

    def __init__(self, client: AtlassianHttpClient) -> None:
        """Initialize the Jira service.

        Args:
            client: HTTP client configured for Jira API.
        """
        self._client = client

    # =========================================================================
    # Read Operations
    # =========================================================================

    async def get_issue(
        self,
        issue_key: str,
        fields: str = "*all",
        expand: str | None = None,
    ) -> dict[str, Any]:
        """Get a Jira issue by key.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123').
            fields: Comma-separated fields to return.
            expand: Fields to expand.

        Returns:
            Simplified issue data.
        """
        params: dict[str, Any] = {"fields": fields}
        if expand:
            params["expand"] = expand

        response = await self._client.get(
            f"/rest/api/3/issue/{issue_key}",
            params=params,
        )
        return self._simplify_issue(response.json())

    async def search(
        self,
        jql: str,
        max_results: int = 50,
        start_at: int = 0,
        fields: str = "*navigable",
    ) -> dict[str, Any]:
        """Search for issues using JQL.

        Args:
            jql: JQL query string.
            max_results: Maximum results to return.
            start_at: Starting index for pagination.
            fields: Fields to return.

        Returns:
            Search results with issues and metadata.
        """
        response = await self._client.get(
            "/rest/api/3/search/jql",
            params={
                "jql": jql,
                "maxResults": max_results,
                "startAt": start_at,
                "fields": fields.split(",") if fields else None,
            },
        )
        data = response.json()

        return {
            "issues": [self._simplify_issue(issue) for issue in data.get("issues", [])],
            "total": data.get("total", 0),
            "start_at": start_at,
            "max_results": max_results,
        }

    async def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        """Get available transitions for an issue.

        Args:
            issue_key: Issue key.

        Returns:
            List of available transitions.
        """
        response = await self._client.get(
            f"/rest/api/3/issue/{issue_key}/transitions"
        )
        data = response.json()

        return [
            {
                "id": t.get("id"),
                "name": t.get("name"),
                "to": {
                    "id": t.get("to", {}).get("id"),
                    "name": t.get("to", {}).get("name"),
                    "category": t.get("to", {}).get("statusCategory", {}).get("name"),
                },
            }
            for t in data.get("transitions", [])
        ]

    async def get_comments(
        self,
        issue_key: str,
        max_results: int = 50,
    ) -> list[dict[str, Any]]:
        """Get comments for an issue.

        Args:
            issue_key: Issue key.
            max_results: Maximum comments to return.

        Returns:
            List of comments.
        """
        response = await self._client.get(
            f"/rest/api/3/issue/{issue_key}/comment",
            params={"maxResults": max_results},
        )
        data = response.json()

        return [
            {
                "id": c.get("id"),
                "author": c.get("author", {}).get("displayName"),
                "body": self._extract_text(c.get("body", {})),
                "created": c.get("created"),
                "updated": c.get("updated"),
            }
            for c in data.get("comments", [])
        ]

    async def get_projects(self) -> list[dict[str, Any]]:
        """Get all accessible projects.

        Returns:
            List of projects.
        """
        response = await self._client.get("/rest/api/3/project")
        data = response.json()

        return [
            {
                "id": p.get("id"),
                "key": p.get("key"),
                "name": p.get("name"),
                "project_type": p.get("projectTypeKey"),
            }
            for p in data
        ]

    async def get_user_profile(self) -> dict[str, Any]:
        """Get current user's profile.

        Returns:
            User profile data.
        """
        response = await self._client.get("/rest/api/3/myself")
        data = response.json()

        return {
            "account_id": data.get("accountId"),
            "display_name": data.get("displayName"),
            "email": data.get("emailAddress"),
            "active": data.get("active"),
            "timezone": data.get("timeZone"),
        }

    async def get_fields(self) -> list[dict[str, Any]]:
        """Get all available fields.

        Returns:
            List of field definitions.
        """
        response = await self._client.get("/rest/api/3/field")
        data = response.json()

        return [
            {
                "id": f.get("id"),
                "name": f.get("name"),
                "custom": f.get("custom", False),
                "schema": f.get("schema"),
            }
            for f in data
        ]

    async def get_priorities(self) -> list[dict[str, Any]]:
        """Get all available priorities.

        Returns:
            List of priorities.
        """
        response = await self._client.get("/rest/api/3/priority")
        data = response.json()

        return [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "description": p.get("description"),
            }
            for p in data
        ]

    async def get_resolutions(self) -> list[dict[str, Any]]:
        """Get all available resolutions.

        Returns:
            List of resolutions.
        """
        response = await self._client.get("/rest/api/3/resolution")
        data = response.json()

        return [
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "description": r.get("description"),
            }
            for r in data
        ]

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        labels: list[str] | None = None,
        components: list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new issue.

        Args:
            project_key: Project key.
            summary: Issue summary.
            issue_type: Issue type name.
            description: Issue description.
            priority: Priority name.
            assignee: Assignee account ID.
            labels: List of labels.
            components: List of component names.
            custom_fields: Custom field values.

        Returns:
            Created issue data with key and id.
        """
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }

        if description:
            fields["description"] = self._create_adf(description)

        if priority:
            fields["priority"] = {"name": priority}

        if assignee:
            fields["assignee"] = {"accountId": assignee}

        if labels:
            fields["labels"] = labels

        if components:
            fields["components"] = [{"name": c} for c in components]

        if custom_fields:
            fields.update(custom_fields)

        response = await self._client.post(
            "/rest/api/3/issue",
            json={"fields": fields},
        )
        data = response.json()

        return {
            "id": data.get("id"),
            "key": data.get("key"),
            "self": data.get("self"),
        }

    async def update_issue(
        self,
        issue_key: str,
        summary: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        labels: list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> None:
        """Update an existing issue.

        Args:
            issue_key: Issue key to update.
            summary: New summary.
            description: New description.
            priority: New priority name.
            assignee: New assignee account ID.
            labels: New labels.
            custom_fields: Custom field updates.
        """
        fields: dict[str, Any] = {}

        if summary:
            fields["summary"] = summary

        if description:
            fields["description"] = self._create_adf(description)

        if priority:
            fields["priority"] = {"name": priority}

        if assignee:
            fields["assignee"] = {"accountId": assignee}

        if labels:
            fields["labels"] = labels

        if custom_fields:
            fields.update(custom_fields)

        await self._client.put(
            f"/rest/api/3/issue/{issue_key}",
            json={"fields": fields},
        )

    async def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
        comment: str | None = None,
    ) -> None:
        """Transition an issue to a new status.

        Args:
            issue_key: Issue key.
            transition_id: Transition ID.
            comment: Optional comment for the transition.
        """
        payload: dict[str, Any] = {
            "transition": {"id": transition_id}
        }

        if comment:
            payload["update"] = {
                "comment": [{"add": {"body": self._create_adf(comment)}}]
            }

        await self._client.post(
            f"/rest/api/3/issue/{issue_key}/transitions",
            json=payload,
        )

    async def add_comment(
        self,
        issue_key: str,
        body: str,
    ) -> dict[str, Any]:
        """Add a comment to an issue.

        Args:
            issue_key: Issue key.
            body: Comment body text.

        Returns:
            Created comment data.
        """
        response = await self._client.post(
            f"/rest/api/3/issue/{issue_key}/comment",
            json={"body": self._create_adf(body)},
        )
        data = response.json()

        return {
            "id": data.get("id"),
            "author": data.get("author", {}).get("displayName"),
            "created": data.get("created"),
        }

    async def update_comment(
        self,
        issue_key: str,
        comment_id: str,
        body: str,
    ) -> None:
        """Update a comment.

        Args:
            issue_key: Issue key.
            comment_id: Comment ID to update.
            body: New comment body.
        """
        await self._client.put(
            f"/rest/api/3/issue/{issue_key}/comment/{comment_id}",
            json={"body": self._create_adf(body)},
        )

    async def delete_comment(
        self,
        issue_key: str,
        comment_id: str,
    ) -> None:
        """Delete a comment.

        Args:
            issue_key: Issue key.
            comment_id: Comment ID to delete.
        """
        await self._client.delete(
            f"/rest/api/3/issue/{issue_key}/comment/{comment_id}"
        )

    async def assign_issue(
        self,
        issue_key: str,
        account_id: str | None,
    ) -> None:
        """Assign an issue to a user.

        Args:
            issue_key: Issue key.
            account_id: User account ID, or None to unassign.
        """
        await self._client.put(
            f"/rest/api/3/issue/{issue_key}/assignee",
            json={"accountId": account_id},
        )

    async def delete_issue(
        self,
        issue_key: str,
        delete_subtasks: bool = False,
    ) -> None:
        """Delete an issue.

        Args:
            issue_key: Issue key to delete.
            delete_subtasks: Whether to delete subtasks.
        """
        await self._client.delete(
            f"/rest/api/3/issue/{issue_key}",
            params={"deleteSubtasks": str(delete_subtasks).lower()},
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _simplify_issue(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Simplify issue data to essential fields.

        Args:
            issue: Raw issue data from API.

        Returns:
            Simplified issue dictionary.
        """
        fields = issue.get("fields", {})

        result: dict[str, Any] = {
            "id": issue.get("id"),
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name"),
            "issue_type": fields.get("issuetype", {}).get("name"),
        }

        # Optional fields
        if fields.get("assignee"):
            result["assignee"] = fields["assignee"].get("displayName")

        if fields.get("reporter"):
            result["reporter"] = fields["reporter"].get("displayName")

        if fields.get("priority"):
            result["priority"] = fields["priority"].get("name")

        if fields.get("description"):
            result["description"] = self._extract_text(fields["description"])

        if fields.get("labels"):
            result["labels"] = fields["labels"]

        if fields.get("created"):
            result["created"] = fields["created"]

        if fields.get("updated"):
            result["updated"] = fields["updated"]

        return result

    def _create_adf(self, text: str) -> dict[str, Any]:
        """Create Atlassian Document Format from plain text.

        Args:
            text: Plain text content.

        Returns:
            ADF document structure.
        """
        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}],
                }
            ],
        }

    def _extract_text(self, adf: dict[str, Any]) -> str:
        """Extract plain text from ADF document.

        Args:
            adf: ADF document structure.

        Returns:
            Extracted plain text.
        """
        if not adf or not isinstance(adf, dict):
            return ""

        texts: list[str] = []

        def extract(node: dict[str, Any]) -> None:
            if node.get("type") == "text":
                texts.append(node.get("text", ""))
            for child in node.get("content", []):
                if isinstance(child, dict):
                    extract(child)

        extract(adf)
        return "".join(texts)


__all__ = ["JiraService"]
