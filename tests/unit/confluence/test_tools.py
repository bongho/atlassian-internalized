"""Unit tests for Confluence tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import AtlassianError, NotFoundError
from atlassian_tools.confluence.models import (
    ConfluenceAddCommentInput,
    ConfluenceAddLabelInput,
    ConfluenceCreatePageInput,
    ConfluenceDeletePageInput,
    ConfluenceGetCommentsInput,
    ConfluenceGetLabelsInput,
    ConfluenceGetPageAncestorsInput,
    ConfluenceGetPageChildrenInput,
    ConfluenceGetPageInput,
    ConfluenceSearchInput,
    ConfluenceUpdatePageInput,
)
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


@pytest.fixture
def mock_confluence_service() -> MagicMock:
    """Create a mock ConfluenceService."""
    service = MagicMock()
    service.get_page = AsyncMock()
    service.search = AsyncMock()
    service.get_page_children = AsyncMock()
    service.get_page_ancestors = AsyncMock()
    service.get_labels = AsyncMock()
    service.get_comments = AsyncMock()
    service.create_page = AsyncMock()
    service.update_page = AsyncMock()
    service.delete_page = AsyncMock()
    service.add_label = AsyncMock()
    service.add_comment = AsyncMock()
    return service


# =============================================================================
# Read Tools Tests
# =============================================================================


class TestConfluenceGetPage:
    """Test confluence_get_page tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful page retrieval."""
        mock_confluence_service.get_page.return_value = {
            "id": "123",
            "title": "Test Page",
            "space_key": "SPACE",
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page(
                ConfluenceGetPageInput(page_id="123")
            )

        assert result.success is True
        assert result.page["id"] == "123"
        assert result.error is None
        mock_confluence_service.get_page.assert_called_once_with(
            page_id="123", expand=None
        )

    @pytest.mark.asyncio
    async def test_with_expand(self, mock_confluence_service: MagicMock) -> None:
        """Test page retrieval with expand parameter."""
        mock_confluence_service.get_page.return_value = {
            "id": "123",
            "title": "Test",
            "body": "<p>Content</p>",
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page(
                ConfluenceGetPageInput(page_id="123", expand="body.storage")
            )

        assert result.success is True
        mock_confluence_service.get_page.assert_called_once_with(
            page_id="123", expand="body.storage"
        )

    @pytest.mark.asyncio
    async def test_not_found(self, mock_confluence_service: MagicMock) -> None:
        """Test page not found error."""
        mock_confluence_service.get_page.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page(
                ConfluenceGetPageInput(page_id="nonexistent")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test general error handling."""
        mock_confluence_service.get_page.side_effect = AtlassianError("API error")

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page(
                ConfluenceGetPageInput(page_id="123")
            )

        assert result.success is False
        assert result.error == "API error"


class TestConfluenceSearch:
    """Test confluence_search tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful search."""
        mock_confluence_service.search.return_value = {
            "results": [{"id": "1", "title": "Page 1"}],
            "total": 1,
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_search(
                ConfluenceSearchInput(cql="type=page")
            )

        assert result.success is True
        assert len(result.results) == 1
        assert result.total == 1
        mock_confluence_service.search.assert_called_once_with(
            cql="type=page", limit=25, start=0
        )

    @pytest.mark.asyncio
    async def test_with_pagination(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test search with pagination."""
        mock_confluence_service.search.return_value = {
            "results": [],
            "total": 0,
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_search(
                ConfluenceSearchInput(cql="type=page", limit=50, start=10)
            )

        assert result.success is True
        mock_confluence_service.search.assert_called_once_with(
            cql="type=page", limit=50, start=10
        )

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test search error handling."""
        mock_confluence_service.search.side_effect = AtlassianError("Search failed")

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_search(
                ConfluenceSearchInput(cql="type=page")
            )

        assert result.success is False
        assert result.error == "Search failed"


class TestConfluenceGetPageChildren:
    """Test confluence_get_page_children tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful children retrieval."""
        mock_confluence_service.get_page_children.return_value = [
            {"id": "child1", "title": "Child 1"},
            {"id": "child2", "title": "Child 2"},
        ]

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page_children(
                ConfluenceGetPageChildrenInput(page_id="123")
            )

        assert result.success is True
        assert len(result.children) == 2
        mock_confluence_service.get_page_children.assert_called_once_with(
            page_id="123", limit=25
        )

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test children retrieval error."""
        mock_confluence_service.get_page_children.side_effect = AtlassianError(
            "Failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page_children(
                ConfluenceGetPageChildrenInput(page_id="123")
            )

        assert result.success is False


class TestConfluenceGetPageAncestors:
    """Test confluence_get_page_ancestors tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful ancestors retrieval."""
        mock_confluence_service.get_page_ancestors.return_value = [
            {"id": "parent", "title": "Parent"},
            {"id": "grandparent", "title": "Grandparent"},
        ]

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page_ancestors(
                ConfluenceGetPageAncestorsInput(page_id="123")
            )

        assert result.success is True
        assert len(result.ancestors) == 2
        mock_confluence_service.get_page_ancestors.assert_called_once_with(
            page_id="123"
        )

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test ancestors retrieval error."""
        mock_confluence_service.get_page_ancestors.side_effect = AtlassianError(
            "Failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page_ancestors(
                ConfluenceGetPageAncestorsInput(page_id="123")
            )

        assert result.success is False


class TestConfluenceGetLabels:
    """Test confluence_get_labels tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful labels retrieval."""
        mock_confluence_service.get_labels.return_value = ["label1", "label2"]

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_labels(
                ConfluenceGetLabelsInput(page_id="123")
            )

        assert result.success is True
        assert result.labels == ["label1", "label2"]
        mock_confluence_service.get_labels.assert_called_once_with(page_id="123")

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test labels retrieval error."""
        mock_confluence_service.get_labels.side_effect = AtlassianError("Failed")

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_labels(
                ConfluenceGetLabelsInput(page_id="123")
            )

        assert result.success is False


class TestConfluenceGetComments:
    """Test confluence_get_comments tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful comments retrieval."""
        mock_confluence_service.get_comments.return_value = [
            {"id": "c1", "title": "", "body": "Comment 1"},
        ]

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_comments(
                ConfluenceGetCommentsInput(page_id="123")
            )

        assert result.success is True
        assert len(result.comments) == 1
        mock_confluence_service.get_comments.assert_called_once_with(
            page_id="123", limit=25
        )

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test comments retrieval error."""
        mock_confluence_service.get_comments.side_effect = AtlassianError("Failed")

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_comments(
                ConfluenceGetCommentsInput(page_id="123")
            )

        assert result.success is False


# =============================================================================
# Write Tools Tests
# =============================================================================


class TestConfluenceCreatePage:
    """Test confluence_create_page tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful page creation."""
        mock_confluence_service.create_page.return_value = {
            "id": "new123",
            "title": "New Page",
            "url": "/spaces/SPACE/pages/new123",
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_create_page(
                ConfluenceCreatePageInput(
                    space_key="SPACE",
                    title="New Page",
                    body="<p>Content</p>",
                )
            )

        assert result.success is True
        assert result.page_id == "new123"
        assert result.page_url == "/spaces/SPACE/pages/new123"
        mock_confluence_service.create_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_parent(self, mock_confluence_service: MagicMock) -> None:
        """Test page creation with parent."""
        mock_confluence_service.create_page.return_value = {
            "id": "new123",
            "title": "Child Page",
            "url": "/spaces/SPACE/pages/new123",
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_create_page(
                ConfluenceCreatePageInput(
                    space_key="SPACE",
                    title="Child Page",
                    body="<p>Content</p>",
                    parent_id="parent123",
                )
            )

        assert result.success is True
        call_args = mock_confluence_service.create_page.call_args
        assert call_args.kwargs["parent_id"] == "parent123"

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test page creation error."""
        mock_confluence_service.create_page.side_effect = AtlassianError(
            "Creation failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_create_page(
                ConfluenceCreatePageInput(
                    space_key="SPACE",
                    title="New Page",
                    body="<p>Content</p>",
                )
            )

        assert result.success is False
        assert result.error == "Creation failed"


class TestConfluenceUpdatePage:
    """Test confluence_update_page tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful page update."""
        mock_confluence_service.update_page.return_value = 2

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_update_page(
                ConfluenceUpdatePageInput(
                    page_id="123",
                    version_number=1,
                    title="Updated Title",
                )
            )

        assert result.success is True
        assert result.new_version == 2
        mock_confluence_service.update_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test page update error."""
        mock_confluence_service.update_page.side_effect = AtlassianError(
            "Update failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_update_page(
                ConfluenceUpdatePageInput(
                    page_id="123",
                    version_number=1,
                    title="Updated",
                )
            )

        assert result.success is False


class TestConfluenceDeletePage:
    """Test confluence_delete_page tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful page deletion."""
        mock_confluence_service.delete_page.return_value = None

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_delete_page(
                ConfluenceDeletePageInput(page_id="123")
            )

        assert result.success is True
        mock_confluence_service.delete_page.assert_called_once_with(page_id="123")

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test page deletion error."""
        mock_confluence_service.delete_page.side_effect = AtlassianError(
            "Deletion failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_delete_page(
                ConfluenceDeletePageInput(page_id="123")
            )

        assert result.success is False


class TestConfluenceAddLabel:
    """Test confluence_add_label tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful label addition."""
        mock_confluence_service.add_label.return_value = None

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_add_label(
                ConfluenceAddLabelInput(page_id="123", label="test-label")
            )

        assert result.success is True
        mock_confluence_service.add_label.assert_called_once_with(
            page_id="123", label="test-label"
        )

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test label addition error."""
        mock_confluence_service.add_label.side_effect = AtlassianError(
            "Label addition failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_add_label(
                ConfluenceAddLabelInput(page_id="123", label="test")
            )

        assert result.success is False


class TestConfluenceAddComment:
    """Test confluence_add_comment tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_confluence_service: MagicMock) -> None:
        """Test successful comment addition."""
        mock_confluence_service.add_comment.return_value = {
            "id": "comment123",
            "title": "",
        }

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_add_comment(
                ConfluenceAddCommentInput(
                    page_id="123", body="<p>Comment text</p>"
                )
            )

        assert result.success is True
        assert result.comment_id == "comment123"
        mock_confluence_service.add_comment.assert_called_once()

    @pytest.mark.asyncio
    async def test_error(self, mock_confluence_service: MagicMock) -> None:
        """Test comment addition error."""
        mock_confluence_service.add_comment.side_effect = AtlassianError(
            "Comment failed"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_add_comment(
                ConfluenceAddCommentInput(page_id="123", body="<p>Comment</p>")
            )

        assert result.success is False
