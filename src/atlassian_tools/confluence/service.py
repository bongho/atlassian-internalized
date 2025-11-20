"""Confluence Service Layer.

This module provides the ConfluenceService class that encapsulates all
Confluence API operations with proper error handling and data transformation.
"""

from typing import Any

from atlassian_tools._core.http_client import AtlassianHttpClient


class ConfluenceService:
    """Service class for Confluence API operations.

    Encapsulates business logic and data transformation for Confluence operations.
    Uses AtlassianHttpClient for HTTP communication.
    """

    def __init__(self, client: AtlassianHttpClient) -> None:
        """Initialize the Confluence service.

        Args:
            client: HTTP client configured for Confluence API.
        """
        self._client = client

    # =========================================================================
    # Read Operations
    # =========================================================================

    async def get_page(
        self,
        page_id: str,
        expand: str | None = None,
    ) -> dict[str, Any]:
        """Get a Confluence page by ID.

        Args:
            page_id: Page ID.
            expand: Comma-separated fields to expand.

        Returns:
            Page data.
        """
        params: dict[str, Any] = {}
        if expand:
            params["expand"] = expand

        response = await self._client.get(
            f"/rest/api/content/{page_id}",
            params=params if params else None,
        )
        return self._simplify_page(response.json())

    async def search(
        self,
        cql: str,
        limit: int = 25,
        start: int = 0,
    ) -> dict[str, Any]:
        """Search for content using CQL.

        Args:
            cql: Confluence Query Language query.
            limit: Maximum results to return.
            start: Starting index for pagination.

        Returns:
            Search results with content items.
        """
        response = await self._client.get(
            "/rest/api/search",
            params={
                "cql": cql,
                "limit": limit,
                "start": start,
            },
        )
        data = response.json()

        # Search API returns results with content nested
        results = []
        for item in data.get("results", []):
            # Extract content from search result
            content = item.get("content", item)
            results.append(self._simplify_page(content))

        return {
            "results": results,
            "total": data.get("totalSize", len(results)),
            "start": start,
            "limit": limit,
        }

    async def get_page_children(
        self,
        page_id: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get child pages of a page.

        Args:
            page_id: Parent page ID.
            limit: Maximum children to return.

        Returns:
            List of child pages.
        """
        response = await self._client.get(
            f"/rest/api/content/{page_id}/child/page",
            params={"limit": limit},
        )
        data = response.json()

        return [
            self._simplify_page(child) for child in data.get("results", [])
        ]

    async def get_page_ancestors(self, page_id: str) -> list[dict[str, Any]]:
        """Get ancestor pages of a page.

        Args:
            page_id: Page ID.

        Returns:
            List of ancestor pages.
        """
        response = await self._client.get(
            f"/rest/api/content/{page_id}",
            params={"expand": "ancestors"},
        )
        data = response.json()

        return [
            {
                "id": a.get("id"),
                "title": a.get("title"),
                "type": a.get("type"),
            }
            for a in data.get("ancestors", [])
        ]

    async def get_labels(self, page_id: str) -> list[str]:
        """Get labels for a page.

        Args:
            page_id: Page ID.

        Returns:
            List of label names.
        """
        response = await self._client.get(
            f"/rest/api/content/{page_id}/label"
        )
        data = response.json()

        return [label.get("name") for label in data.get("results", [])]

    async def get_comments(
        self,
        page_id: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get comments for a page.

        Args:
            page_id: Page ID.
            limit: Maximum comments to return.

        Returns:
            List of comments.
        """
        response = await self._client.get(
            f"/rest/api/content/{page_id}/child/comment",
            params={"limit": limit, "expand": "body.storage"},
        )
        data = response.json()

        return [
            {
                "id": c.get("id"),
                "title": c.get("title"),
                "body": c.get("body", {}).get("storage", {}).get("value", ""),
            }
            for c in data.get("results", [])
        ]

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def create_page(
        self,
        space_key: str,
        title: str,
        body: str,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a new page.

        Args:
            space_key: Space key.
            title: Page title.
            body: Page body content (HTML or storage format).
            parent_id: Parent page ID.

        Returns:
            Created page data with id and URL.
        """
        payload: dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage",
                }
            },
        }

        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]

        response = await self._client.post(
            "/rest/api/content",
            json=payload,
        )
        data = response.json()

        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "url": data.get("_links", {}).get("webui", ""),
        }

    async def update_page(
        self,
        page_id: str,
        version_number: int,
        title: str | None = None,
        body: str | None = None,
    ) -> int:
        """Update an existing page.

        Args:
            page_id: Page ID to update.
            version_number: Current version number.
            title: New title (optional).
            body: New body content (optional).

        Returns:
            New version number.
        """
        # Get current page data if we need defaults
        if not title or not body:
            current = await self.get_page(page_id, expand="body.storage")
            if not title:
                title = current.get("title", "")
            if not body:
                body = current.get("body", "")

        payload: dict[str, Any] = {
            "version": {"number": version_number + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage",
                }
            },
        }

        response = await self._client.put(
            f"/rest/api/content/{page_id}",
            json=payload,
        )
        data = response.json()

        return data.get("version", {}).get("number", version_number + 1)

    async def delete_page(self, page_id: str) -> None:
        """Delete a page.

        Args:
            page_id: Page ID to delete.
        """
        await self._client.delete(f"/rest/api/content/{page_id}")

    async def add_label(self, page_id: str, label: str) -> None:
        """Add a label to a page.

        Args:
            page_id: Page ID.
            label: Label name to add.
        """
        await self._client.post(
            f"/rest/api/content/{page_id}/label",
            json=[{"name": label}],
        )

    async def add_comment(
        self,
        page_id: str,
        body: str,
    ) -> dict[str, Any]:
        """Add a comment to a page.

        Args:
            page_id: Page ID.
            body: Comment body content.

        Returns:
            Created comment data.
        """
        payload: dict[str, Any] = {
            "type": "comment",
            "container": {"id": page_id, "type": "page"},
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage",
                }
            },
        }

        response = await self._client.post(
            "/rest/api/content",
            json=payload,
        )
        data = response.json()

        return {
            "id": data.get("id"),
            "title": data.get("title"),
        }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _simplify_page(self, page: dict[str, Any]) -> dict[str, Any]:
        """Simplify page data to essential fields.

        Args:
            page: Raw page data from API.

        Returns:
            Simplified page dictionary.
        """
        result: dict[str, Any] = {
            "id": page.get("id"),
            "title": page.get("title"),
            "type": page.get("type"),
        }

        # Space info
        if page.get("space"):
            result["space_key"] = page["space"].get("key")

        # Version info
        if page.get("version"):
            result["version"] = page["version"].get("number")

        # Body content
        if page.get("body"):
            storage = page["body"].get("storage", {})
            result["body"] = storage.get("value", "")

        # Links
        if page.get("_links"):
            result["url"] = page["_links"].get("webui", "")

        return result


__all__ = ["ConfluenceService"]
