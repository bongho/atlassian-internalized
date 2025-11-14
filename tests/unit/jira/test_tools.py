"""Tests for Jira tool functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlassian_tools.jira.models import JiraGetIssueInput
from atlassian_tools.jira.tools import jira_get_issue


@pytest.fixture
def mock_jira_client() -> MagicMock:
    """Create a mock Jira client."""
    return MagicMock()


@pytest.fixture
def sample_jira_response() -> dict:
    """Sample Jira API response."""
    return {
        "id": "10001",
        "key": "PROJ-123",
        "self": "https://example.atlassian.net/rest/api/2/issue/10001",
        "fields": {
            "summary": "Test issue summary",
            "description": "Test issue description",
            "status": {
                "name": "In Progress",
                "statusCategory": {"name": "In Progress"},
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": "High"},
            "assignee": {
                "displayName": "John Doe",
                "emailAddress": "john@example.com",
            },
            "reporter": {
                "displayName": "Jane Smith",
                "emailAddress": "jane@example.com",
            },
            "created": "2025-01-14T10:00:00.000+0000",
            "updated": "2025-01-14T12:00:00.000+0000",
            "labels": ["backend", "api"],
            "components": [{"name": "Core"}],
            "comment": {
                "comments": [
                    {
                        "author": {"displayName": "Alice"},
                        "body": "First comment",
                        "created": "2025-01-14T10:30:00.000+0000",
                    },
                    {
                        "author": {"displayName": "Bob"},
                        "body": "Second comment",
                        "created": "2025-01-14T11:00:00.000+0000",
                    },
                ]
            },
            "attachment": [
                {
                    "filename": "test.pdf",
                    "size": 1024,
                    "mimeType": "application/pdf",
                    "content": "https://example.com/attachment/test.pdf",
                }
            ],
        },
    }


class TestJiraGetIssue:
    """Test suite for jira_get_issue function."""

    @pytest.mark.asyncio
    async def test_success_minimal(
        self, mock_jira_client: MagicMock, sample_jira_response: dict
    ) -> None:
        """Test successful issue retrieval with minimal input."""
        mock_jira_client.issue.return_value = sample_jira_response

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.error is None
        assert result.issue is not None
        assert result.issue["key"] == "PROJ-123"
        assert result.issue["fields"]["summary"] == "Test issue summary"

        # Verify API was called correctly
        mock_jira_client.issue.assert_called_once_with(
            key="PROJ-123", fields="*all", expand=None
        )

    @pytest.mark.asyncio
    async def test_success_with_fields(
        self, mock_jira_client: MagicMock, sample_jira_response: dict
    ) -> None:
        """Test successful issue retrieval with specific fields."""
        mock_jira_client.issue.return_value = sample_jira_response

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(
                issue_key="PROJ-123", fields="summary,status", comment_limit=5
            )
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.issue is not None

        # Verify API was called with specified fields
        mock_jira_client.issue.assert_called_once_with(
            key="PROJ-123", fields="summary,status", expand=None
        )

    @pytest.mark.asyncio
    async def test_success_with_expand(
        self, mock_jira_client: MagicMock, sample_jira_response: dict
    ) -> None:
        """Test successful issue retrieval with expanded fields."""
        response_with_changelog = {
            **sample_jira_response,
            "changelog": {"histories": []},
        }
        mock_jira_client.issue.return_value = response_with_changelog

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(
                issue_key="PROJ-123", expand="changelog"
            )
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.issue is not None
        assert "changelog" in result.issue

        # Verify API was called with expand
        mock_jira_client.issue.assert_called_once_with(
            key="PROJ-123", fields="*all", expand="changelog"
        )

    @pytest.mark.asyncio
    async def test_comments_limit(
        self, mock_jira_client: MagicMock, sample_jira_response: dict
    ) -> None:
        """Test that comment limit is respected."""
        mock_jira_client.issue.return_value = sample_jira_response

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123", comment_limit=1)
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.issue is not None

        # Should only include 1 comment despite 2 in response
        comments = result.issue["fields"].get("comments", [])
        assert len(comments) == 1

    @pytest.mark.asyncio
    async def test_no_comments_when_limit_zero(
        self, mock_jira_client: MagicMock, sample_jira_response: dict
    ) -> None:
        """Test that no comments are included when limit is 0."""
        mock_jira_client.issue.return_value = sample_jira_response

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123", comment_limit=0)
            result = await jira_get_issue(input_data)

        assert result.success is True
        assert result.issue is not None

        # Should have no comments
        assert "comments" not in result.issue["fields"]

    @pytest.mark.asyncio
    async def test_issue_not_found(self, mock_jira_client: MagicMock) -> None:
        """Test handling of non-existent issue."""
        mock_jira_client.issue.side_effect = Exception("Issue PROJ-999 does not exist")

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-999")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "PROJ-999 not found" in result.error

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_jira_client: MagicMock) -> None:
        """Test handling of authentication errors."""
        mock_jira_client.issue.side_effect = Exception("401 Unauthorized")

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "Authentication failed" in result.error

    @pytest.mark.asyncio
    async def test_missing_env_vars(self) -> None:
        """Test error when environment variables are missing."""
        with patch.dict("os.environ", {}, clear=True):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "JIRA_URL" in result.error

    @pytest.mark.asyncio
    async def test_invalid_api_response(self, mock_jira_client: MagicMock) -> None:
        """Test handling of invalid API response."""
        mock_jira_client.issue.return_value = "Invalid response"

        with patch(
            "atlassian_tools.jira.tools._get_jira_client",
            return_value=mock_jira_client,
        ):
            input_data = JiraGetIssueInput(issue_key="PROJ-123")
            result = await jira_get_issue(input_data)

        assert result.success is False
        assert result.issue is None
        assert "Invalid response" in result.error


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
