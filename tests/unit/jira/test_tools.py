"""Tests for Jira tool functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools._core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
)
from atlassian_tools.jira.models import JiraGetIssueInput
from atlassian_tools.jira.tools import jira_get_issue


@pytest.fixture
def mock_jira_service() -> MagicMock:
    """Create a mock Jira service."""
    service = MagicMock()
    service.get_issue = AsyncMock()
    return service


@pytest.fixture
def sample_simplified_issue() -> dict:
    """Sample simplified issue data (as returned by service layer)."""
    return {
        "id": "10001",
        "key": "PROJ-123",
        "summary": "Test issue summary",
        "status": "In Progress",
        "issue_type": "Task",
        "priority": "High",
        "assignee": "John Doe",
        "reporter": "Jane Smith",
        "description": "Test issue description",
        "labels": ["backend", "api"],
        "created": "2025-01-14T10:00:00.000+0000",
        "updated": "2025-01-14T12:00:00.000+0000",
    }


class TestJiraGetIssue:
    """Test suite for jira_get_issue function."""

    @pytest.mark.asyncio
    async def test_success_minimal(
        self, mock_jira_service: MagicMock, sample_simplified_issue: dict
    ) -> None:
        """Test successful issue retrieval with minimal input."""
        mock_jira_service.get_issue.return_value = sample_simplified_issue

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.error is None
        assert result.issue is not None
        assert result.issue["key"] == "PROJ-123"
        assert result.issue["summary"] == "Test issue summary"

        # Verify service was called correctly
        mock_jira_service.get_issue.assert_called_once_with(
            issue_key="PROJ-123", fields="*all", expand=None
        )

    @pytest.mark.asyncio
    async def test_success_with_fields(
        self, mock_jira_service: MagicMock, sample_simplified_issue: dict
    ) -> None:
        """Test successful issue retrieval with specific fields."""
        mock_jira_service.get_issue.return_value = sample_simplified_issue

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetIssueInput(
                issue_key="PROJ-123", fields="summary,status"
            )
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.issue is not None

        # Verify service was called with specified fields
        mock_jira_service.get_issue.assert_called_once_with(
            issue_key="PROJ-123", fields="summary,status", expand=None
        )

    @pytest.mark.asyncio
    async def test_success_with_expand(
        self, mock_jira_service: MagicMock, sample_simplified_issue: dict
    ) -> None:
        """Test successful issue retrieval with expanded fields."""
        mock_jira_service.get_issue.return_value = sample_simplified_issue

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetIssueInput(
                issue_key="PROJ-123", expand="changelog"
            )
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.issue is not None

        # Verify service was called with expand
        mock_jira_service.get_issue.assert_called_once_with(
            issue_key="PROJ-123", fields="*all", expand="changelog"
        )

    @pytest.mark.asyncio
    async def test_issue_not_found(self, mock_jira_service: MagicMock) -> None:
        """Test handling of non-existent issue."""
        mock_jira_service.get_issue.side_effect = NotFoundError(
            "Issue PROJ-999 not found"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-999")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "PROJ-999 not found" in result.error

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_jira_service: MagicMock) -> None:
        """Test handling of authentication errors."""
        mock_jira_service.get_issue.side_effect = AuthenticationError(
            "Invalid credentials"
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "Invalid credentials" in result.error

    @pytest.mark.asyncio
    async def test_missing_env_vars(self) -> None:
        """Test error when configuration is missing."""
        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            side_effect=ConfigurationError("JIRA_URL is required"),
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "JIRA_URL" in result.error

    @pytest.mark.asyncio
    async def test_general_error(self, mock_jira_service: MagicMock) -> None:
        """Test handling of general errors."""
        mock_jira_service.get_issue.side_effect = Exception("Unexpected error")

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_jira_service,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "Unexpected error" in result.error


class TestToolMetadata:
    """Test that tool has correct metadata for Tool protocol."""

    def test_tool_name_attribute(self) -> None:
        """Test that tool has tool_name attribute."""
        assert hasattr(jira_get_issue, "tool_name")
        assert jira_get_issue.tool_name == "jira_get_issue"  # type: ignore[attr-defined]

    def test_input_schema_attribute(self) -> None:
        """Test that tool has input_schema attribute."""
        assert hasattr(jira_get_issue, "input_schema")
        assert jira_get_issue.input_schema == JiraGetIssueInput  # type: ignore[attr-defined]

    def test_output_schema_attribute(self) -> None:
        """Test that tool has output_schema attribute."""
        assert hasattr(jira_get_issue, "output_schema")
        from atlassian_tools.jira.models import JiraGetIssueOutput

        assert jira_get_issue.output_schema == JiraGetIssueOutput  # type: ignore[attr-defined]
