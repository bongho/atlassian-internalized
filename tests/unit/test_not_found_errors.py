"""Test NotFoundError handling for complete coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import NotFoundError
from atlassian_tools.confluence.models import (
    ConfluenceAddCommentInput,
    ConfluenceAddLabelInput,
    ConfluenceDeletePageInput,
    ConfluenceGetPageInput,
    ConfluenceUpdatePageInput,
)
from atlassian_tools.confluence.tools import (
    confluence_add_comment,
    confluence_add_label,
    confluence_delete_page,
    confluence_get_page,
    confluence_update_page,
)
from atlassian_tools.jira.models import (
    JiraAddWorklogInput,
    JiraDeleteCommentInput,
    JiraDeleteIssueInput,
    JiraGetBoardIssuesInput,
    JiraGetEpicIssuesInput,
    JiraGetSprintIssuesInput,
    JiraGetWatchersInput,
    JiraGetWorklogInput,
    JiraLinkIssuesInput,
    JiraRemoveWatcherInput,
    JiraUnlinkIssuesInput,
    JiraUpdateCommentInput,
)
from atlassian_tools.jira.tools import (
    jira_add_worklog,
    jira_delete_comment,
    jira_delete_issue,
    jira_get_board_issues,
    jira_get_epic_issues,
    jira_get_sprint_issues,
    jira_get_watchers,
    jira_get_worklog,
    jira_link_issues,
    jira_remove_watcher,
    jira_unlink_issues,
    jira_update_comment,
)


@pytest.fixture
def mock_jira_service() -> MagicMock:
    """Create a mock JiraService."""
    service = MagicMock()
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.delete = AsyncMock()
    service._client = mock_client
    service.delete_issue = AsyncMock()
    service.update_comment = AsyncMock()
    service.delete_comment = AsyncMock()
    return service


@pytest.fixture
def mock_confluence_service() -> MagicMock:
    """Create a mock ConfluenceService."""
    service = MagicMock()
    service.get_page = AsyncMock()
    service.update_page = AsyncMock()
    service.delete_page = AsyncMock()
    service.add_label = AsyncMock()
    service.add_comment = AsyncMock()
    return service


class TestJiraNotFoundErrors:
    """Test NotFoundError handling in Jira tools."""

    @pytest.mark.asyncio
    async def test_get_worklog_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_worklog NotFoundError handling."""
        mock_jira_service._client.get.side_effect = NotFoundError("Issue not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_worklog(
                JiraGetWorklogInput(issue_key="PROJ-999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_watchers_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_watchers NotFoundError handling."""
        mock_jira_service._client.get.side_effect = NotFoundError("Issue not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_watchers(
                JiraGetWatchersInput(issue_key="PROJ-999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_sprint_issues_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_sprint_issues NotFoundError handling."""
        mock_jira_service._client.get.side_effect = NotFoundError("Sprint not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_sprint_issues(
                JiraGetSprintIssuesInput(sprint_id=999)
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_board_issues_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_board_issues NotFoundError handling."""
        mock_jira_service._client.get.side_effect = NotFoundError("Board not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_board_issues(
                JiraGetBoardIssuesInput(board_id=999)
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_epic_issues_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_epic_issues NotFoundError handling."""
        mock_jira_service._client.get.side_effect = NotFoundError("Epic not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_epic_issues(
                JiraGetEpicIssuesInput(epic_key="PROJ-999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_remove_watcher_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_remove_watcher NotFoundError handling."""
        mock_jira_service._client.delete.side_effect = NotFoundError(
            "Issue not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_remove_watcher(
                JiraRemoveWatcherInput(issue_key="PROJ-999", account_id="user123")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_add_worklog_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_add_worklog NotFoundError handling."""
        mock_jira_service._client.post.side_effect = NotFoundError("Issue not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_add_worklog(
                JiraAddWorklogInput(issue_key="PROJ-999", time_spent="1h")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_link_issues_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_link_issues NotFoundError handling."""
        mock_jira_service._client.post.side_effect = NotFoundError("Issue not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_link_issues(
                JiraLinkIssuesInput(
                    inward_issue="PROJ-999",
                    outward_issue="PROJ-998",
                    link_type="Relates",
                )
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_delete_issue_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_delete_issue NotFoundError handling."""
        mock_jira_service.delete_issue.side_effect = NotFoundError("Issue not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_delete_issue(
                JiraDeleteIssueInput(issue_key="PROJ-999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_update_comment_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_update_comment NotFoundError handling."""
        mock_jira_service.update_comment.side_effect = NotFoundError(
            "Comment not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_update_comment(
                JiraUpdateCommentInput(
                    issue_key="PROJ-1", comment_id="999", body="Updated"
                )
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_delete_comment NotFoundError handling."""
        mock_jira_service.delete_comment.side_effect = NotFoundError(
            "Comment not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_delete_comment(
                JiraDeleteCommentInput(issue_key="PROJ-1", comment_id="999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_unlink_issues_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_unlink_issues NotFoundError handling."""
        mock_jira_service._client.delete.side_effect = NotFoundError("Link not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_unlink_issues(JiraUnlinkIssuesInput(link_id="999"))

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_add_watcher_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_add_watcher NotFoundError handling."""
        mock_jira_service._client.post.side_effect = NotFoundError("Issue not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            from atlassian_tools.jira.models import JiraAddWatcherInput
            from atlassian_tools.jira.tools import jira_add_watcher

            result = await jira_add_watcher(
                JiraAddWatcherInput(issue_key="PROJ-999", account_id="user123")
            )

        assert result.success is False
        assert "not found" in result.error.lower()


class TestConfluenceNotFoundErrors:
    """Test NotFoundError handling in Confluence tools."""

    @pytest.mark.asyncio
    async def test_get_page_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_get_page NotFoundError handling."""
        mock_confluence_service.get_page.side_effect = NotFoundError("Page not found")

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_get_page(ConfluenceGetPageInput(page_id="999"))

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_page_children_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_get_page_children NotFoundError handling."""
        mock_confluence_service.get_page_children.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            from atlassian_tools.confluence.models import ConfluenceGetPageChildrenInput
            from atlassian_tools.confluence.tools import confluence_get_page_children

            result = await confluence_get_page_children(
                ConfluenceGetPageChildrenInput(page_id="999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_page_ancestors_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_get_page_ancestors NotFoundError handling."""
        mock_confluence_service.get_page_ancestors.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            from atlassian_tools.confluence.models import (
                ConfluenceGetPageAncestorsInput,
            )
            from atlassian_tools.confluence.tools import confluence_get_page_ancestors

            result = await confluence_get_page_ancestors(
                ConfluenceGetPageAncestorsInput(page_id="999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_labels_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_get_labels NotFoundError handling."""
        mock_confluence_service.get_labels.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            from atlassian_tools.confluence.models import ConfluenceGetLabelsInput
            from atlassian_tools.confluence.tools import confluence_get_labels

            result = await confluence_get_labels(
                ConfluenceGetLabelsInput(page_id="999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_comments_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_get_comments NotFoundError handling."""
        mock_confluence_service.get_comments.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            from atlassian_tools.confluence.models import ConfluenceGetCommentsInput
            from atlassian_tools.confluence.tools import confluence_get_comments

            result = await confluence_get_comments(
                ConfluenceGetCommentsInput(page_id="999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_update_page_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_update_page NotFoundError handling."""
        mock_confluence_service.update_page.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_update_page(
                ConfluenceUpdatePageInput(page_id="999", version_number=1)
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_delete_page_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_delete_page NotFoundError handling."""
        mock_confluence_service.delete_page.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_delete_page(
                ConfluenceDeletePageInput(page_id="999")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_add_label_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_add_label NotFoundError handling."""
        mock_confluence_service.add_label.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_add_label(
                ConfluenceAddLabelInput(page_id="999", label="test")
            )

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_add_comment_not_found(
        self, mock_confluence_service: MagicMock
    ) -> None:
        """Test confluence_add_comment NotFoundError handling."""
        mock_confluence_service.add_comment.side_effect = NotFoundError(
            "Page not found"
        )

        with patch(
            "atlassian_tools.confluence.tools.get_confluence_service",
            return_value=mock_confluence_service,
        ):
            result = await confluence_add_comment(
                ConfluenceAddCommentInput(page_id="999", body="<p>Comment</p>")
            )

        assert result.success is False
        assert "not found" in result.error.lower()
