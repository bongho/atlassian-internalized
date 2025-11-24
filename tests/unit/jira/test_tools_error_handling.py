"""Error handling tests for Jira tools to achieve full coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import AtlassianError
from atlassian_tools.jira.models import (
    JiraAddCommentInput,
    JiraAddWatcherInput,
    JiraAddWorklogInput,
    JiraAssignIssueInput,
    JiraBatchCreateIssuesInput,
    JiraCreateIssueInput,
    JiraDeleteCommentInput,
    JiraDeleteIssueInput,
    JiraGetAllProjectsInput,
    JiraGetBoardIssuesInput,
    JiraGetCommentsInput,
    JiraGetEpicIssuesInput,
    JiraGetFieldsInput,
    JiraGetIssueInput,
    JiraGetLinkTypesInput,
    JiraGetPrioritiesInput,
    JiraGetProjectIssuesInput,
    JiraGetResolutionsInput,
    JiraGetSprintIssuesInput,
    JiraGetTransitionsInput,
    JiraGetUserProfileInput,
    JiraGetWatchersInput,
    JiraGetWorklogInput,
    JiraLinkIssuesInput,
    JiraRemoveWatcherInput,
    JiraSearchInput,
    JiraTransitionIssueInput,
    JiraUnlinkIssuesInput,
    JiraUpdateCommentInput,
    JiraUpdateIssueInput,
)
from atlassian_tools.jira.tools import (
    jira_add_comment,
    jira_add_watcher,
    jira_add_worklog,
    jira_assign_issue,
    jira_batch_create_issues,
    jira_create_issue,
    jira_delete_comment,
    jira_delete_issue,
    jira_get_all_projects,
    jira_get_board_issues,
    jira_get_comments,
    jira_get_epic_issues,
    jira_get_fields,
    jira_get_issue,
    jira_get_link_types,
    jira_get_priorities,
    jira_get_project_issues,
    jira_get_resolutions,
    jira_get_sprint_issues,
    jira_get_transitions,
    jira_get_user_profile,
    jira_get_watchers,
    jira_get_worklog,
    jira_link_issues,
    jira_remove_watcher,
    jira_search,
    jira_transition_issue,
    jira_unlink_issues,
    jira_update_comment,
    jira_update_issue,
)


@pytest.fixture
def mock_jira_service() -> MagicMock:
    """Create a mock JiraService."""
    service = MagicMock()

    # Service methods
    service.get_issue = AsyncMock()
    service.search = AsyncMock()
    service.create_issue = AsyncMock()
    service.update_issue = AsyncMock()
    service.transition_issue = AsyncMock()
    service.assign_issue = AsyncMock()
    service.add_comment = AsyncMock()
    service.get_transitions = AsyncMock()
    service.get_projects = AsyncMock()
    service.get_user_profile = AsyncMock()
    service.get_comments = AsyncMock()
    service.get_fields = AsyncMock()
    service.get_priorities = AsyncMock()
    service.get_resolutions = AsyncMock()
    service.delete_issue = AsyncMock()
    service.update_comment = AsyncMock()
    service.delete_comment = AsyncMock()

    # HTTP client (for tools that use service._client directly)
    mock_client = MagicMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.delete = AsyncMock()
    service._client = mock_client

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

    @pytest.mark.asyncio
    async def test_get_all_projects_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_all_projects AtlassianError handling."""
        mock_jira_service.get_projects.side_effect = AtlassianError("Projects failed")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_all_projects(JiraGetAllProjectsInput())

        assert result.success is False
        assert result.error == "Projects failed"

    @pytest.mark.asyncio
    async def test_get_user_profile_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_user_profile AtlassianError handling."""
        mock_jira_service.get_user_profile.side_effect = AtlassianError(
            "Profile failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_user_profile(JiraGetUserProfileInput())

        assert result.success is False
        assert result.error == "Profile failed"

    @pytest.mark.asyncio
    async def test_get_comments_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_get_comments AtlassianError handling."""
        mock_jira_service.get_comments.side_effect = AtlassianError(
            "Comments failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_comments(
                JiraGetCommentsInput(issue_key="PROJ-1")
            )

        assert result.success is False
        assert result.error == "Comments failed"

    @pytest.mark.asyncio
    async def test_get_worklog_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_get_worklog AtlassianError handling."""
        mock_jira_service._client.get.side_effect = AtlassianError("Worklog failed")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_worklog(
                JiraGetWorklogInput(issue_key="PROJ-1")
            )

        assert result.success is False
        assert result.error == "Worklog failed"

    @pytest.mark.asyncio
    async def test_get_watchers_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_get_watchers AtlassianError handling."""
        mock_jira_service._client.get.side_effect = AtlassianError(
            "Watchers failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_watchers(
                JiraGetWatchersInput(issue_key="PROJ-1")
            )

        assert result.success is False
        assert result.error == "Watchers failed"

    @pytest.mark.asyncio
    async def test_get_sprint_issues_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_sprint_issues AtlassianError handling."""
        mock_jira_service._client.get.side_effect = AtlassianError(
            "Sprint issues failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_sprint_issues(
                JiraGetSprintIssuesInput(sprint_id=1)
            )

        assert result.success is False
        assert result.error == "Sprint issues failed"

    @pytest.mark.asyncio
    async def test_get_board_issues_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_board_issues AtlassianError handling."""
        mock_jira_service._client.get.side_effect = AtlassianError(
            "Board issues failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_board_issues(JiraGetBoardIssuesInput(board_id=1))

        assert result.success is False
        assert result.error == "Board issues failed"

    @pytest.mark.asyncio
    async def test_get_epic_issues_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_epic_issues AtlassianError handling."""
        mock_jira_service._client.get.side_effect = AtlassianError(
            "Epic issues failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_epic_issues(
                JiraGetEpicIssuesInput(epic_key="PROJ-1")
            )

        assert result.success is False
        assert result.error == "Epic issues failed"

    @pytest.mark.asyncio
    async def test_get_project_issues_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_project_issues AtlassianError handling."""
        mock_jira_service.search.side_effect = AtlassianError(
            "Project issues failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_project_issues(
                JiraGetProjectIssuesInput(project_key="PROJ")
            )

        assert result.success is False
        assert result.error == "Project issues failed"

    @pytest.mark.asyncio
    async def test_get_fields_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_get_fields AtlassianError handling."""
        mock_jira_service.get_fields.side_effect = AtlassianError("Fields failed")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_fields(JiraGetFieldsInput())

        assert result.success is False
        assert result.error == "Fields failed"

    @pytest.mark.asyncio
    async def test_get_link_types_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_link_types AtlassianError handling."""
        mock_jira_service._client.get.side_effect = AtlassianError(
            "Link types failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_link_types(JiraGetLinkTypesInput())

        assert result.success is False
        assert result.error == "Link types failed"

    @pytest.mark.asyncio
    async def test_get_priorities_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_priorities AtlassianError handling."""
        mock_jira_service.get_priorities.side_effect = AtlassianError(
            "Priorities failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_priorities(JiraGetPrioritiesInput())

        assert result.success is False
        assert result.error == "Priorities failed"

    @pytest.mark.asyncio
    async def test_get_resolutions_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_get_resolutions AtlassianError handling."""
        mock_jira_service.get_resolutions.side_effect = AtlassianError(
            "Resolutions failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_get_resolutions(JiraGetResolutionsInput())

        assert result.success is False
        assert result.error == "Resolutions failed"

    @pytest.mark.asyncio
    async def test_add_watcher_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_add_watcher AtlassianError handling."""
        mock_jira_service._client.post.side_effect = AtlassianError(
            "Add watcher failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_add_watcher(
                JiraAddWatcherInput(issue_key="PROJ-1", account_id="user123")
            )

        assert result.success is False
        assert result.error == "Add watcher failed"

    @pytest.mark.asyncio
    async def test_remove_watcher_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_remove_watcher AtlassianError handling."""
        mock_jira_service._client.delete.side_effect = AtlassianError(
            "Remove watcher failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_remove_watcher(
                JiraRemoveWatcherInput(issue_key="PROJ-1", account_id="user123")
            )

        assert result.success is False
        assert result.error == "Remove watcher failed"

    @pytest.mark.asyncio
    async def test_add_worklog_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_add_worklog AtlassianError handling."""
        mock_jira_service._client.post.side_effect = AtlassianError(
            "Add worklog failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_add_worklog(
                JiraAddWorklogInput(issue_key="PROJ-1", time_spent="1h")
            )

        assert result.success is False
        assert result.error == "Add worklog failed"

    @pytest.mark.asyncio
    async def test_link_issues_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_link_issues AtlassianError handling."""
        mock_jira_service._client.post.side_effect = AtlassianError(
            "Link issues failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_link_issues(
                JiraLinkIssuesInput(
                    inward_issue="PROJ-1",
                    outward_issue="PROJ-2",
                    link_type="Relates",
                )
            )

        assert result.success is False
        assert result.error == "Link issues failed"

    @pytest.mark.asyncio
    async def test_delete_issue_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_delete_issue AtlassianError handling."""
        mock_jira_service.delete_issue.side_effect = AtlassianError(
            "Delete issue failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_delete_issue(
                JiraDeleteIssueInput(issue_key="PROJ-1")
            )

        assert result.success is False
        assert result.error == "Delete issue failed"

    @pytest.mark.asyncio
    async def test_batch_create_issues_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_batch_create_issues AtlassianError handling."""
        mock_jira_service.create_issue.side_effect = AtlassianError(
            "Batch create failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_batch_create_issues(
                JiraBatchCreateIssuesInput(
                    issues=[
                        {
                            "project_key": "PROJ",
                            "summary": "Test",
                            "issue_type": "Task",
                        }
                    ]
                )
            )

        assert result.success is False
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_update_comment_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_update_comment AtlassianError handling."""
        mock_jira_service.update_comment.side_effect = AtlassianError(
            "Update comment failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_update_comment(
                JiraUpdateCommentInput(
                    issue_key="PROJ-1", comment_id="123", body="Updated"
                )
            )

        assert result.success is False
        assert result.error == "Update comment failed"

    @pytest.mark.asyncio
    async def test_delete_comment_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test jira_delete_comment AtlassianError handling."""
        mock_jira_service.delete_comment.side_effect = AtlassianError(
            "Delete comment failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_delete_comment(
                JiraDeleteCommentInput(issue_key="PROJ-1", comment_id="123")
            )

        assert result.success is False
        assert result.error == "Delete comment failed"

    @pytest.mark.asyncio
    async def test_unlink_issues_error(self, mock_jira_service: MagicMock) -> None:
        """Test jira_unlink_issues AtlassianError handling."""
        mock_jira_service._client.delete.side_effect = AtlassianError(
            "Unlink issues failed"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            result = await jira_unlink_issues(
                JiraUnlinkIssuesInput(link_id="123")
            )

        assert result.success is False
        assert result.error == "Unlink issues failed"
