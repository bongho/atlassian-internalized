"""Error handling tests for Jira tools to achieve full coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import AtlassianError
from atlassian_tools.jira.models import (
    JiraAddCommentInput,
    JiraAssignIssueInput,
    JiraCreateIssueInput,
    JiraGetIssueInput,
    JiraGetTransitionsInput,
    JiraSearchInput,
    JiraTransitionIssueInput,
    JiraUpdateIssueInput,
)
from atlassian_tools.jira.tools import (
    jira_add_comment,
    jira_assign_issue,
    jira_create_issue,
    jira_get_issue,
    jira_get_transitions,
    jira_search,
    jira_transition_issue,
    jira_update_issue,
)


@pytest.fixture
def mock_jira_service() -> MagicMock:
    """Create a mock JiraService."""
    service = MagicMock()
    service.get_issue = AsyncMock()
    service.search = AsyncMock()
    service.create_issue = AsyncMock()
    service.update_issue = AsyncMock()
    service.transition_issue = AsyncMock()
    service.assign_issue = AsyncMock()
    service.add_comment = AsyncMock()
    service.get_transitions = AsyncMock()
    return service


class TestToolErrorHandling:
    """Test AtlassianError handling in all tools."""

    @pytest.mark.asyncio
    async def test_get_issue_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_get_issue AtlassianError handling."""
        mock_jira_service.get_issue.side_effect = AtlassianError("API error")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_issue(JiraGetIssueInput(issue_key="PROJ-1"))

        assert result.success is False
        assert result.error == "API error"

    @pytest.mark.asyncio
    async def test_search_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_search AtlassianError handling."""
        mock_jira_service.search.side_effect = AtlassianError("Search failed")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_search(JiraSearchInput(jql="project = PROJ"))

        assert result.success is False
        assert result.error == "Search failed"

    @pytest.mark.asyncio
    async def test_create_issue_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_create_issue AtlassianError handling."""
        mock_jira_service.create_issue.side_effect = AtlassianError(
            "Creation failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_create_issue(
                JiraCreateIssueInput(
                    project_key="PROJ",
                    summary="Test",
                    issue_type="Task",
                )
            )

        assert result.success is False
        assert result.error == "Creation failed"

    @pytest.mark.asyncio
    async def test_update_issue_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_update_issue AtlassianError handling."""
        mock_jira_service.update_issue.side_effect = AtlassianError("Update failed")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_update_issue(
                JiraUpdateIssueInput(
                    issue_key="PROJ-1",
                    summary="Updated",
                )
            )

        assert result.success is False
        assert result.error == "Update failed"

    @pytest.mark.asyncio
    async def test_get_transitions_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_get_transitions AtlassianError handling."""
        mock_jira_service.get_transitions.side_effect = AtlassianError(
            "Transitions failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_transitions(
                JiraGetTransitionsInput(issue_key="PROJ-1")
            )

        assert result.success is False
        assert result.error == "Transitions failed"

    @pytest.mark.asyncio
    async def test_transition_issue_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_transition_issue AtlassianError handling."""
        mock_jira_service.transition_issue.side_effect = AtlassianError(
            "Transition failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_transition_issue(
                JiraTransitionIssueInput(
                    issue_key="PROJ-1",
                    transition_id="11",
                )
            )

        assert result.success is False
        assert result.error == "Transition failed"

    @pytest.mark.asyncio
    async def test_assign_issue_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_assign_issue AtlassianError handling."""
        mock_jira_service.assign_issue.side_effect = AtlassianError(
            "Assignment failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_assign_issue(
                JiraAssignIssueInput(
                    issue_key="PROJ-1",
                    account_id="user123",
                )
            )

        assert result.success is False
        assert result.error == "Assignment failed"

    @pytest.mark.asyncio
    async def test_add_comment_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_add_comment AtlassianError handling."""
        mock_jira_service.add_comment.side_effect = AtlassianError("Comment failed")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_add_comment(
                JiraAddCommentInput(
                    issue_key="PROJ-1",
                    body="Test comment",
                )
            )

        assert result.success is False
        assert result.error == "Comment failed"
