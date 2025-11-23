"""Unit tests for ConfluenceService."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from atlassian_tools.confluence.service import ConfluenceService


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Create a mock HTTP client."""
    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def confluence_service(mock_http_client: MagicMock) -> ConfluenceService:
    """Create a ConfluenceService with mocked client."""
    return ConfluenceService(mock_http_client)


class TestGetPage:
    """Test get_page method."""

    @pytest.mark.asyncio
    async def test_get_page_basic(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test basic page retrieval."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "123",
            "type": "page",
            "title": "Test Page",
            "space": {"key": "SPACE"},
            "body": {
                "storage": {
                    "value": "<p>Content</p>",
                    "representation": "storage",
                }
            },
            "version": {"number": 1},
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.get_page("123")

        assert result["id"] == "123"
        assert result["title"] == "Test Page"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/content/123",
            params=None,
        )

    @pytest.mark.asyncio
    async def test_get_page_with_expand(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test page retrieval with expand parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "123",
            "type": "page",
            "title": "Test Page",
            "space": {"key": "SPACE"},
            "body": {"storage": {"value": "<p>Content</p>"}},
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.get_page("123", expand="body.storage")

        assert result["id"] == "123"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/content/123",
            params={"expand": "body.storage"},
        )


class TestSearch:
    """Test search method."""

    @pytest.mark.asyncio
    async def test_search_basic(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test basic CQL search."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "results": [
                {
                    "content": {
                        "id": "123",
                        "type": "page",
                        "title": "Page 1",
                        "space": {"key": "SPACE"},
                    }
                },
                {
                    "content": {
                        "id": "456",
                        "type": "page",
                        "title": "Page 2",
                        "space": {"key": "SPACE"},
                    }
                },
            ],
            "totalSize": 2,
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.search("type=page")

        assert len(result["results"]) == 2
        assert result["total"] == 2
        assert result["results"][0]["id"] == "123"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/search",
            params={"cql": "type=page", "limit": 25, "start": 0},
        )

    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test search with pagination parameters."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "results": [],
            "totalSize": 0,
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.search("type=page", limit=50, start=10)

        assert result["limit"] == 50
        assert result["start"] == 10
        mock_http_client.get.assert_called_once_with(
            "/rest/api/search",
            params={"cql": "type=page", "limit": 50, "start": 10},
        )


class TestGetPageChildren:
    """Test get_page_children method."""

    @pytest.mark.asyncio
    async def test_get_page_children(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test getting child pages."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "results": [
                {"id": "child1", "type": "page", "title": "Child 1", "space": {"key": "S"}},
                {"id": "child2", "type": "page", "title": "Child 2", "space": {"key": "S"}},
            ]
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.get_page_children("123")

        assert len(result) == 2
        assert result[0]["id"] == "child1"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/content/123/child/page",
            params={"limit": 25},
        )


class TestGetPageAncestors:
    """Test get_page_ancestors method."""

    @pytest.mark.asyncio
    async def test_get_page_ancestors(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test getting page ancestors."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "ancestors": [
                {"id": "parent", "type": "page", "title": "Parent", "space": {"key": "S"}},
                {"id": "grandparent", "type": "page", "title": "Grandparent", "space": {"key": "S"}},
            ]
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.get_page_ancestors("123")

        assert len(result) == 2
        assert result[0]["id"] == "parent"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/content/123",
            params={"expand": "ancestors"},
        )


class TestGetLabels:
    """Test get_labels method."""

    @pytest.mark.asyncio
    async def test_get_labels(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test getting page labels."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "results": [
                {"name": "label1"},
                {"name": "label2"},
            ]
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.get_labels("123")

        assert result == ["label1", "label2"]
        mock_http_client.get.assert_called_once_with(
            "/rest/api/content/123/label",
        )


class TestGetComments:
    """Test get_comments method."""

    @pytest.mark.asyncio
    async def test_get_comments(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test getting page comments."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "comment1",
                    "type": "comment",
                    "title": "",
                    "body": {"storage": {"value": "Comment 1"}},
                },
            ]
        }
        mock_http_client.get.return_value = mock_response

        result = await confluence_service.get_comments("123")

        assert len(result) == 1
        assert result[0]["id"] == "comment1"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/content/123/child/comment",
            params={"limit": 25, "expand": "body.storage"},
        )


class TestCreatePage:
    """Test create_page method."""

    @pytest.mark.asyncio
    async def test_create_page_without_parent(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test creating a page without parent."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "new123",
            "type": "page",
            "title": "New Page",
            "space": {"key": "SPACE"},
        }
        mock_http_client.post.return_value = mock_response

        result = await confluence_service.create_page(
            space_key="SPACE",
            title="New Page",
            body="<p>Content</p>",
        )

        assert result["id"] == "new123"
        assert result["title"] == "New Page"
        mock_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_with_parent(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test creating a page with parent."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "new123",
            "type": "page",
            "title": "Child Page",
            "space": {"key": "SPACE"},
        }
        mock_http_client.post.return_value = mock_response

        result = await confluence_service.create_page(
            space_key="SPACE",
            title="Child Page",
            body="<p>Content</p>",
            parent_id="parent123",
        )

        assert result["id"] == "new123"
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["ancestors"] == [{"id": "parent123"}]


class TestUpdatePage:
    """Test update_page method."""

    @pytest.mark.asyncio
    async def test_update_page_title(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating page title only."""
        # Mock get to retrieve current page
        mock_get_response = MagicMock(spec=httpx.Response)
        mock_get_response.json.return_value = {
            "id": "123",
            "type": "page",
            "title": "Old Title",
            "space": {"key": "SPACE"},
            "version": {"number": 1},
            "body": {"storage": {"value": "<p>Old content</p>"}},
        }
        # Mock put for update
        mock_put_response = MagicMock(spec=httpx.Response)
        mock_put_response.json.return_value = {
            "id": "123",
            "type": "page",
            "title": "New Title",
            "space": {"key": "SPACE"},
            "version": {"number": 2},
        }
        mock_http_client.get.return_value = mock_get_response
        mock_http_client.put.return_value = mock_put_response

        result = await confluence_service.update_page(
            page_id="123",
            version_number=1,
            title="New Title",
        )

        assert result == 2
        mock_http_client.get.assert_called_once()
        mock_http_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_page_body(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating page body only."""
        mock_get_response = MagicMock(spec=httpx.Response)
        mock_get_response.json.return_value = {
            "id": "123",
            "type": "page",
            "title": "Title",
            "space": {"key": "SPACE"},
            "version": {"number": 1},
            "body": {"storage": {"value": "<p>Old</p>"}},
        }
        mock_put_response = MagicMock(spec=httpx.Response)
        mock_put_response.json.return_value = {
            "id": "123",
            "type": "page",
            "title": "Title",
            "version": {"number": 2},
        }
        mock_http_client.get.return_value = mock_get_response
        mock_http_client.put.return_value = mock_put_response

        result = await confluence_service.update_page(
            page_id="123",
            version_number=1,
            body="<p>New content</p>",
        )

        assert result == 2
        mock_http_client.put.assert_called_once()


class TestDeletePage:
    """Test delete_page method."""

    @pytest.mark.asyncio
    async def test_delete_page(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a page."""
        mock_http_client.delete.return_value = None

        await confluence_service.delete_page("123")

        mock_http_client.delete.assert_called_once_with("/rest/api/content/123")


class TestAddLabel:
    """Test add_label method."""

    @pytest.mark.asyncio
    async def test_add_label(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test adding a label to a page."""
        mock_http_client.post.return_value = None

        await confluence_service.add_label("123", "test-label")

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"] == [{"name": "test-label"}]


class TestAddComment:
    """Test add_comment method."""

    @pytest.mark.asyncio
    async def test_add_comment(
        self,
        confluence_service: ConfluenceService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test adding a comment to a page."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "comment123",
            "type": "comment",
            "title": "",
        }
        mock_http_client.post.return_value = mock_response

        result = await confluence_service.add_comment("123", "<p>Comment text</p>")

        assert result["id"] == "comment123"
        mock_http_client.post.assert_called_once()


class TestSimplifyPage:
    """Test _simplify_page helper method."""

    def test_simplify_page_basic(self, confluence_service: ConfluenceService) -> None:
        """Test simplifying page data with basic fields."""
        page = {
            "id": "123",
            "type": "page",
            "title": "Test",
            "space": {"key": "SPACE"},
        }

        result = confluence_service._simplify_page(page)

        assert result["id"] == "123"
        assert result["title"] == "Test"
        assert result["space_key"] == "SPACE"

    def test_simplify_page_with_body(
        self, confluence_service: ConfluenceService
    ) -> None:
        """Test simplifying page with body content."""
        page = {
            "id": "123",
            "type": "page",
            "title": "Test",
            "space": {"key": "SPACE"},
            "body": {
                "storage": {
                    "value": "<p>Content</p>",
                    "representation": "storage",
                }
            },
        }

        result = confluence_service._simplify_page(page)

        assert result["body"] == "<p>Content</p>"

    def test_simplify_page_with_version(
        self, confluence_service: ConfluenceService
    ) -> None:
        """Test simplifying page with version info."""
        page = {
            "id": "123",
            "type": "page",
            "title": "Test",
            "space": {"key": "SPACE"},
            "version": {"number": 5},
        }

        result = confluence_service._simplify_page(page)

        assert result["version"] == 5
