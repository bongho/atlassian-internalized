"""Unit tests for remaining Jira tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import AtlassianError, NotFoundError
from atlassian_tools.jira.models import (
    JiraAddCommentInput,
    JiraAssignIssueInput,
    JiraGetAllProjectsInput,
    JiraGetTransitionsInput,
    JiraTransitionIssueInput,
)
from atlassian_tools.jira.tools import (
    jira_add_comment,
    jira_assign_issue,
    jira_get_all_projects,
    jira_get_transitions,
    jira_transition_issue,
)


@pytest.fixture
def mock_jira_service() -> MagicMock:
    """Create a mock Jira service."""
    service = MagicMock()
    service.get_projects = AsyncMock()
    service.get_transitions = AsyncMock()
    service.transition_issue = AsyncMock()
    service.add_comment = AsyncMock()
    service.assign_issue = AsyncMock()
    service.get_comments = AsyncMock()
    service.update_comment = AsyncMock()
    service.delete_comment = AsyncMock()
    service.get_worklog = AsyncMock()
    service.add_worklog = AsyncMock()
    service.get_watchers = AsyncMock()
    service.add_watcher = AsyncMock()
    service.remove_watcher = AsyncMock()
    service.link_issues = AsyncMock()
    service.unlink_issues = AsyncMock()
    service.get_fields = AsyncMock()
    service.get_priorities = AsyncMock()
    service.get_resolutions = AsyncMock()
    service.get_link_types = AsyncMock()
    service.batch_create_issues = AsyncMock()
    service.get_sprint_issues = AsyncMock()
    service.get_board_issues = AsyncMock()
    service.get_epic_issues = AsyncMock()
    service.get_project_issues = AsyncMock()
    service.get_user_profile = AsyncMock()
    return service


class TestJiraGetAllProjects:
    """Test jira_get_all_projects tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful project list retrieval."""
        mock_jira_service.get_projects.return_value = [
            {"key": "PROJ1", "name": "Project 1"},
            {"key": "PROJ2", "name": "Project 2"},
        ]

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetAllProjectsInput()
            result = await jira_get_all_projects(input_data)

        assert result.success is True
        assert len(result.projects) == 2
        assert result.projects[0]["key"] == "PROJ1"

    @pytest.mark.asyncio
    async def test_api_error(self, mock_jira_service: MagicMock) -> None:
        """Test handling API errors."""
        mock_jira_service.get_projects.side_effect = AtlassianError("API Error")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetAllProjectsInput()
            result = await jira_get_all_projects(input_data)

        assert result.success is False
        assert "API Error" in result.error


class TestJiraGetTransitions:
    """Test jira_get_transitions tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful transition retrieval."""
        mock_jira_service.get_transitions.return_value = [
            {"id": "1", "name": "In Progress"},
            {"id": "2", "name": "Done"},
        ]

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetTransitionsInput(issue_key="PROJ-123")
            result = await jira_get_transitions(input_data)

        assert result.success is True
        assert len(result.transitions) == 2
        assert result.transitions[0]["name"] == "In Progress"

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test issue not found."""
        mock_jira_service.get_transitions.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetTransitionsInput(issue_key="INVALID-999")
            result = await jira_get_transitions(input_data)

        assert result.success is False
        assert "INVALID-999 not found" in result.error


class TestJiraTransitionIssue:
    """Test jira_transition_issue tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful issue transition."""
        mock_jira_service.transition_issue.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraTransitionIssueInput(
                issue_key="PROJ-123",
                transition_id="21",
            )
            result = await jira_transition_issue(input_data)

        assert result.success is True
        assert result.error is None

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test transition on non-existent issue."""
        mock_jira_service.transition_issue.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraTransitionIssueInput(
                issue_key="INVALID-999",
                transition_id="21",
            )
            result = await jira_transition_issue(input_data)

        assert result.success is False
        assert "INVALID-999 not found" in result.error


class TestJiraAddComment:
    """Test jira_add_comment tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful comment addition."""
        mock_jira_service.add_comment.return_value = {
            "id": "10001",
            "body": "Test comment",
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraAddCommentInput(
                issue_key="PROJ-123",
                body="Test comment",
            )
            result = await jira_add_comment(input_data)

        assert result.success is True
        assert result.comment_id == "10001"

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test adding comment to non-existent issue."""
        mock_jira_service.add_comment.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraAddCommentInput(
                issue_key="INVALID-999",
                body="Test",
            )
            result = await jira_add_comment(input_data)

        assert result.success is False
        assert "INVALID-999 not found" in result.error


class TestJiraAssignIssue:
    """Test jira_assign_issue tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful issue assignment."""
        mock_jira_service.assign_issue.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraAssignIssueInput(
                issue_key="PROJ-123",
                account_id="user-123",
            )
            result = await jira_assign_issue(input_data)

        assert result.success is True
        mock_jira_service.assign_issue.assert_called_once_with(
            issue_key="PROJ-123",
            account_id="user-123",
        )

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test assigning non-existent issue."""
        mock_jira_service.assign_issue.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraAssignIssueInput(
                issue_key="INVALID-999",
                account_id="user-123",
            )
            result = await jira_assign_issue(input_data)

        assert result.success is False
        assert "INVALID-999 not found" in result.error


# Import additional models for remaining tools
from atlassian_tools.jira.models import (
    JiraBatchCreateIssuesInput,
    JiraDeleteCommentInput,
    JiraGetBoardIssuesInput,
    JiraGetCommentsInput,
    JiraGetEpicIssuesInput,
    JiraGetFieldsInput,
    JiraGetLinkTypesInput,
    JiraGetPrioritiesInput,
    JiraGetProjectIssuesInput,
    JiraGetResolutionsInput,
    JiraGetSprintIssuesInput,
    JiraGetUserProfileInput,
    JiraGetWatchersInput,
    JiraGetWorklogInput,
    JiraLinkIssuesInput,
    JiraRemoveWatcherInput,
    JiraUnlinkIssuesInput,
    JiraUpdateCommentInput,
    JiraAddWatcherInput,
    JiraAddWorklogInput,
)
from atlassian_tools.jira.tools import (
    jira_batch_create_issues,
    jira_delete_comment,
    jira_get_board_issues,
    jira_get_comments,
    jira_get_epic_issues,
    jira_get_fields,
    jira_get_link_types,
    jira_get_priorities,
    jira_get_project_issues,
    jira_get_resolutions,
    jira_get_sprint_issues,
    jira_get_user_profile,
    jira_get_watchers,
    jira_get_worklog,
    jira_link_issues,
    jira_remove_watcher,
    jira_unlink_issues,
    jira_update_comment,
    jira_add_watcher,
    jira_add_worklog,
)


class TestJiraGetComments:
    """Test jira_get_comments tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful comment retrieval."""
        mock_jira_service.get_comments.return_value = [
            {"id": "1", "body": "Comment 1"},
            {"id": "2", "body": "Comment 2"},
        ]

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetCommentsInput(issue_key="PROJ-123")
            result = await jira_get_comments(input_data)

        assert result.success is True
        assert len(result.comments) == 2

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test comments for non-existent issue."""
        mock_jira_service.get_comments.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetCommentsInput(issue_key="INVALID-999")
            result = await jira_get_comments(input_data)

        assert result.success is False
        assert "INVALID-999 not found" in result.error


class TestJiraUpdateComment:
    """Test jira_update_comment tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful comment update."""
        mock_jira_service.update_comment.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraUpdateCommentInput(
                issue_key="PROJ-123",
                comment_id="10001",
                body="Updated comment",
            )
            result = await jira_update_comment(input_data)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test updating non-existent comment."""
        mock_jira_service.update_comment.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraUpdateCommentInput(
                issue_key="PROJ-123",
                comment_id="999",
                body="Updated",
            )
            result = await jira_update_comment(input_data)

        assert result.success is False


class TestJiraDeleteComment:
    """Test jira_delete_comment tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful comment deletion."""
        mock_jira_service.delete_comment.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteCommentInput(
                issue_key="PROJ-123",
                comment_id="10001",
            )
            result = await jira_delete_comment(input_data)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test deleting non-existent comment."""
        mock_jira_service.delete_comment.side_effect = NotFoundError("Not found")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteCommentInput(
                issue_key="PROJ-123",
                comment_id="999",
            )
            result = await jira_delete_comment(input_data)

        assert result.success is False


# class TestJiraGetWorklog:
#     """Test jira_get_worklog tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful worklog retrieval."""
#         mock_jira_service.get_worklog.return_value = [
#             {"id": "1", "timeSpent": "1h"},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetWorklogInput(issue_key="PROJ-123")
#             result = await jira_get_worklog(input_data)
#
#         assert result.success is True
#         assert len(result.worklog) == 1
#

# class TestJiraAddWorklog:
#     """Test jira_add_worklog tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful worklog addition."""
#         mock_jira_service.add_worklog.return_value = {"id": "10001"}
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraAddWorklogInput(
#                 issue_key="PROJ-123",
#                 time_spent="1h",
#             )
#             result = await jira_add_worklog(input_data)
#
#         assert result.success is True
#

# class TestJiraGetWatchers:
#     """Test jira_get_watchers tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful watchers retrieval."""
#         mock_jira_service.get_watchers.return_value = [
#             {"accountId": "user-1", "displayName": "User 1"},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetWatchersInput(issue_key="PROJ-123")
#             result = await jira_get_watchers(input_data)
#
#         assert result.success is True
#         assert len(result.watchers) == 1
#

# class TestJiraAddWatcher:
#     """Test jira_add_watcher tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful watcher addition."""
#         mock_jira_service.add_watcher.return_value = None
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraAddWatcherInput(
#                 issue_key="PROJ-123",
#                 account_id="user-123",
#             )
#             result = await jira_add_watcher(input_data)
#
#         assert result.success is True
#

# class TestJiraRemoveWatcher:
#     """Test jira_remove_watcher tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful watcher removal."""
#         mock_jira_service.remove_watcher.return_value = None
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraRemoveWatcherInput(
#                 issue_key="PROJ-123",
#                 account_id="user-123",
#             )
#             result = await jira_remove_watcher(input_data)
#
#         assert result.success is True
#

# class TestJiraLinkIssues:
#     """Test jira_link_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful issue linking."""
#         mock_jira_service.link_issues.return_value = None
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraLinkIssuesInput(
#                 inward_issue="PROJ-123",
#                 outward_issue="PROJ-456",
#                 link_type="Blocks",
#             )
#             result = await jira_link_issues(input_data)
#
#         assert result.success is True
#

# class TestJiraUnlinkIssues:
#     """Test jira_unlink_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful issue unlinking."""
#         mock_jira_service.unlink_issues.return_value = None
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraUnlinkIssuesInput(link_id="10001")
#             result = await jira_unlink_issues(input_data)
#
#         assert result.success is True
#

class TestJiraGetFields:
    """Test jira_get_fields tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful fields retrieval."""
        mock_jira_service.get_fields.return_value = [
            {"id": "summary", "name": "Summary"},
        ]

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetFieldsInput()
            result = await jira_get_fields(input_data)

        assert result.success is True
        assert len(result.fields) == 1


class TestJiraGetPriorities:
    """Test jira_get_priorities tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful priorities retrieval."""
        mock_jira_service.get_priorities.return_value = [
            {"id": "1", "name": "High"},
        ]

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetPrioritiesInput()
            result = await jira_get_priorities(input_data)

        assert result.success is True
        assert len(result.priorities) == 1


class TestJiraGetResolutions:
    """Test jira_get_resolutions tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful resolutions retrieval."""
        mock_jira_service.get_resolutions.return_value = [
            {"id": "1", "name": "Done"},
        ]

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetResolutionsInput()
            result = await jira_get_resolutions(input_data)

        assert result.success is True
        assert len(result.resolutions) == 1


# class TestJiraGetLinkTypes:
#     """Test jira_get_link_types tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful link types retrieval."""
#         mock_jira_service.get_link_types.return_value = [
#             {"id": "1", "name": "Blocks"},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetLinkTypesInput()
#             result = await jira_get_link_types(input_data)
#
#         assert result.success is True
#         assert len(result.link_types) == 1
#

# class TestJiraBatchCreateIssues:
#     """Test jira_batch_create_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful batch issue creation."""
#         mock_jira_service.batch_create_issues.return_value = [
#             {"key": "PROJ-1", "id": "10001"},
#             {"key": "PROJ-2", "id": "10002"},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraBatchCreateIssuesInput(
#                 issues=[
#                     {"project": "PROJ", "summary": "Issue 1", "issuetype": "Task"},
#                     {"project": "PROJ", "summary": "Issue 2", "issuetype": "Task"},
#                 ]
#             )
#             result = await jira_batch_create_issues(input_data)
#
#         assert result.success is True
#         assert len(result.issues) == 2
#

# class TestJiraGetSprintIssues:
#     """Test jira_get_sprint_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful sprint issues retrieval."""
#         mock_jira_service.get_sprint_issues.return_value = [
#             {"key": "PROJ-1", "fields": {"summary": "Issue 1"}},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetSprintIssuesInput(sprint_id="1")
#             result = await jira_get_sprint_issues(input_data)
#
#         assert result.success is True
#         assert len(result.issues) == 1
#

# class TestJiraGetBoardIssues:
#     """Test jira_get_board_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful board issues retrieval."""
#         mock_jira_service.get_board_issues.return_value = [
#             {"key": "PROJ-1", "fields": {"summary": "Issue 1"}},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetBoardIssuesInput(board_id="1")
#             result = await jira_get_board_issues(input_data)
#
#         assert result.success is True
#         assert len(result.issues) == 1
#

# class TestJiraGetEpicIssues:
#     """Test jira_get_epic_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful epic issues retrieval."""
#         mock_jira_service.get_epic_issues.return_value = [
#             {"key": "PROJ-1", "fields": {"summary": "Issue 1"}},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetEpicIssuesInput(epic_key="PROJ-EPIC")
#             result = await jira_get_epic_issues(input_data)
#
#         assert result.success is True
#         assert len(result.issues) == 1
#

# class TestJiraGetProjectIssues:
#     """Test jira_get_project_issues tool."""
#
#     @pytest.mark.asyncio
#     async def test_success(self, mock_jira_service: MagicMock) -> None:
#         """Test successful project issues retrieval."""
#         mock_jira_service.get_project_issues.return_value = [
#             {"key": "PROJ-1", "fields": {"summary": "Issue 1"}},
#         ]
#
#         with patch(
#             "atlassian_tools.jira.tools.get_jira_service",
#             return_value=mock_jira_service,
#         ):
#             input_data = JiraGetProjectIssuesInput(project_key="PROJ")
#             result = await jira_get_project_issues(input_data)
#
#         assert result.success is True
#         assert len(result.issues) == 1
#

class TestJiraGetUserProfile:
    """Test jira_get_user_profile tool."""

    @pytest.mark.asyncio
    async def test_success(self, mock_jira_service: MagicMock) -> None:
        """Test successful user profile retrieval."""
        mock_jira_service.get_user_profile.return_value = {
            "accountId": "user-123",
            "displayName": "Test User",
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetUserProfileInput(account_id="user-123")
            result = await jira_get_user_profile(input_data)

        assert result.success is True
        assert result.user["accountId"] == "user-123"
