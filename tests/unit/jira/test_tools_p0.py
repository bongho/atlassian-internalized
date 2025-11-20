"""Unit tests for Priority 0 Jira tools (search, create, update, delete)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import (
    AtlassianError,
    NotFoundError,
    ValidationError,
)
from atlassian_tools.jira.models import (
    JiraCreateIssueInput,
    JiraCreateIssueOutput,
    JiraDeleteIssueInput,
    JiraDeleteIssueOutput,
    JiraSearchInput,
    JiraSearchOutput,
    JiraUpdateIssueInput,
    JiraUpdateIssueOutput,
)
from atlassian_tools.jira.tools import (
    jira_create_issue,
    jira_delete_issue,
    jira_search,
    jira_update_issue,
)


@pytest.fixture
def mock_jira_service() -> MagicMock:
    """Create a mock Jira service."""
    service = MagicMock()
    service.search = AsyncMock()
    service.create_issue = AsyncMock()
    service.update_issue = AsyncMock()
    service.delete_issue = AsyncMock()
    return service


class TestJiraSearch:
    """Test jira_search tool."""

    @pytest.mark.asyncio
    async def test_search_success_basic(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test successful basic JQL search."""
        mock_jira_service.search.return_value = {
            "issues": [
                {"key": "PROJ-1", "summary": "Test Issue 1"},
                {"key": "PROJ-2", "summary": "Test Issue 2"},
            ],
            "total": 2,
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraSearchInput(jql="project = PROJ")
            result = await jira_search(input_data)

        assert result.success is True
        assert len(result.issues) == 2
        assert result.total == 2
        assert result.issues[0]["key"] == "PROJ-1"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test search with no results."""
        mock_jira_service.search.return_value = {
            "issues": [],
            "total": 0,
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraSearchInput(jql="project = INVALID")
            result = await jira_search(input_data)

        assert result.success is True
        assert len(result.issues) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test search with pagination parameters."""
        mock_jira_service.search.return_value = {
            "issues": [{"key": f"PROJ-{i}"} for i in range(1, 21)],
            "total": 100,
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraSearchInput(
                jql="project = PROJ",
                max_results=20,
                start_at=0,
            )
            result = await jira_search(input_data)

        assert result.success is True
        assert len(result.issues) == 20
        assert result.total == 100
        mock_jira_service.search.assert_called_once_with(
            jql="project = PROJ",
            max_results=20,
            start_at=0,
            fields="*navigable",
        )

    @pytest.mark.asyncio
    async def test_search_with_custom_fields(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test search with custom fields parameter."""
        mock_jira_service.search.return_value = {
            "issues": [{"key": "PROJ-1", "fields": {"summary": "Test"}}],
            "total": 1,
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraSearchInput(
                jql="project = PROJ",
                fields="summary,status,assignee",
            )
            result = await jira_search(input_data)

        mock_jira_service.search.assert_called_once_with(
            jql="project = PROJ",
            max_results=50,
            start_at=0,
            fields="summary,status,assignee",
        )

    @pytest.mark.asyncio
    async def test_search_invalid_jql(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test search with invalid JQL syntax."""
        mock_jira_service.search.side_effect = ValidationError(
            "Invalid JQL syntax"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraSearchInput(jql="INVALID JQL {{")
            result = await jira_search(input_data)

        assert result.success is False
        assert "Invalid JQL syntax" in result.error

    @pytest.mark.asyncio
    async def test_search_api_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test search handling API errors."""
        mock_jira_service.search.side_effect = AtlassianError("API Error")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraSearchInput(jql="project = PROJ")
            result = await jira_search(input_data)

        assert result.success is False
        assert "API Error" in result.error


class TestJiraCreateIssue:
    """Test jira_create_issue tool."""

    @pytest.mark.asyncio
    async def test_create_issue_minimal(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test creating issue with required fields only."""
        mock_jira_service.create_issue.return_value = {
            "id": "12345",
            "key": "PROJ-123",
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraCreateIssueInput(
                project_key="PROJ",
                summary="Test Issue",
                issue_type="Task",
            )
            result = await jira_create_issue(input_data)

        assert result.success is True
        assert result.issue_key == "PROJ-123"
        assert result.issue_id == "12345"
        assert result.error is None

        mock_jira_service.create_issue.assert_called_once_with(
            project_key="PROJ",
            summary="Test Issue",
            issue_type="Task",
            description=None,
            priority=None,
            assignee=None,
            labels=None,
            components=None,
        )

    @pytest.mark.asyncio
    async def test_create_issue_full(self, mock_jira_service: MagicMock) -> None:
        """Test creating issue with all optional fields."""
        mock_jira_service.create_issue.return_value = {
            "id": "12345",
            "key": "PROJ-123",
        }

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraCreateIssueInput(
                project_key="PROJ",
                summary="Test Issue",
                issue_type="Bug",
                description="Detailed description",
                priority="High",
                assignee="user@example.com",
                labels=["bug", "urgent"],
                components=["Backend", "API"],
            )
            result = await jira_create_issue(input_data)

        assert result.success is True
        assert result.issue_key == "PROJ-123"

        mock_jira_service.create_issue.assert_called_once_with(
            project_key="PROJ",
            summary="Test Issue",
            issue_type="Bug",
            description="Detailed description",
            priority="High",
            assignee="user@example.com",
            labels=["bug", "urgent"],
            components=["Backend", "API"],
        )

    @pytest.mark.asyncio
    async def test_create_issue_invalid_project(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test creating issue in non-existent project."""
        mock_jira_service.create_issue.side_effect = NotFoundError(
            "Project not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraCreateIssueInput(
                project_key="INVALID",
                summary="Test Issue",
                issue_type="Task",
            )
            result = await jira_create_issue(input_data)

        assert result.success is False
        assert "Project not found" in result.error

    @pytest.mark.asyncio
    async def test_create_issue_validation_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test creating issue with invalid data."""
        mock_jira_service.create_issue.side_effect = ValidationError(
            "Field 'summary' is required"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraCreateIssueInput(
                project_key="PROJ",
                summary="",  # Empty summary
                issue_type="Task",
            )
            result = await jira_create_issue(input_data)

        assert result.success is False
        assert "Field 'summary' is required" in result.error


class TestJiraUpdateIssue:
    """Test jira_update_issue tool."""

    @pytest.mark.asyncio
    async def test_update_issue_success(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test successful issue update."""
        mock_jira_service.update_issue.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraUpdateIssueInput(
                issue_key="PROJ-123",
                summary="Updated Summary",
            )
            result = await jira_update_issue(input_data)

        assert result.success is True
        assert result.error is None

        mock_jira_service.update_issue.assert_called_once_with(
            issue_key="PROJ-123",
            summary="Updated Summary",
            description=None,
            priority=None,
            assignee=None,
            labels=None,
        )

    @pytest.mark.asyncio
    async def test_update_issue_multiple_fields(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test updating multiple fields."""
        mock_jira_service.update_issue.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraUpdateIssueInput(
                issue_key="PROJ-123",
                summary="New Summary",
                description="New Description",
                priority="High",
                assignee="user@example.com",
                labels=["updated", "reviewed"],
            )
            result = await jira_update_issue(input_data)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_update_issue_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test updating non-existent issue."""
        mock_jira_service.update_issue.side_effect = NotFoundError(
            "Issue not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraUpdateIssueInput(
                issue_key="INVALID-999",
                summary="Updated",
            )
            result = await jira_update_issue(input_data)

        assert result.success is False
        assert "Issue INVALID-999 not found" in result.error

    @pytest.mark.asyncio
    async def test_update_issue_validation_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test update with invalid data."""
        mock_jira_service.update_issue.side_effect = ValidationError(
            "Invalid priority value"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraUpdateIssueInput(
                issue_key="PROJ-123",
                priority="InvalidPriority",
            )
            result = await jira_update_issue(input_data)

        assert result.success is False
        assert "Invalid priority value" in result.error


class TestJiraDeleteIssue:
    """Test jira_delete_issue tool."""

    @pytest.mark.asyncio
    async def test_delete_issue_success(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test successful issue deletion."""
        mock_jira_service.delete_issue.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteIssueInput(issue_key="PROJ-123")
            result = await jira_delete_issue(input_data)

        assert result.success is True
        assert result.error is None

        mock_jira_service.delete_issue.assert_called_once_with(
            issue_key="PROJ-123",
            delete_subtasks=False,
        )

    @pytest.mark.asyncio
    async def test_delete_issue_with_subtasks(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test deleting issue with subtasks."""
        mock_jira_service.delete_issue.return_value = None

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteIssueInput(
                issue_key="PROJ-123",
                delete_subtasks=True,
            )
            result = await jira_delete_issue(input_data)

        assert result.success is True

        mock_jira_service.delete_issue.assert_called_once_with(
            issue_key="PROJ-123",
            delete_subtasks=True,
        )

    @pytest.mark.asyncio
    async def test_delete_issue_not_found(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test deleting non-existent issue."""
        mock_jira_service.delete_issue.side_effect = NotFoundError(
            "Issue not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteIssueInput(issue_key="INVALID-999")
            result = await jira_delete_issue(input_data)

        assert result.success is False
        assert "Issue INVALID-999 not found" in result.error

    @pytest.mark.asyncio
    async def test_delete_issue_permission_denied(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test deleting issue without permission."""
        from atlassian_tools._core.exceptions import AuthorizationError

        mock_jira_service.delete_issue.side_effect = AuthorizationError(
            "Permission denied"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteIssueInput(issue_key="PROJ-123")
            result = await jira_delete_issue(input_data)

        assert result.success is False
        assert "Permission denied" in result.error

    @pytest.mark.asyncio
    async def test_delete_issue_with_subtask_error(
        self, mock_jira_service: MagicMock
    ) -> None:
        """Test deleting issue with subtasks when flag is False."""
        mock_jira_service.delete_issue.side_effect = ValidationError(
            "Issue has subtasks, use delete_subtasks=True"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraDeleteIssueInput(
                issue_key="PROJ-123",
                delete_subtasks=False,
            )
            result = await jira_delete_issue(input_data)

        assert result.success is False
        assert "subtasks" in result.error.lower()
