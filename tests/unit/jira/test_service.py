"""Unit tests for JiraService."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from atlassian_tools._core.config import JiraConfig
from atlassian_tools._core.http_client import AtlassianHttpClient
from atlassian_tools.jira.service import JiraService


@pytest.fixture
def jira_config() -> JiraConfig:
    """Create test Jira config."""
    return JiraConfig(
        url="https://test.atlassian.net",
        username="test@example.com",
        api_token="test-token",
    )


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Create mock HTTP client."""
    client = MagicMock(spec=AtlassianHttpClient)
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def jira_service(mock_http_client: MagicMock) -> JiraService:
    """Create JiraService with mock client."""
    return JiraService(mock_http_client)


class TestJiraServiceReadOperations:
    """Test read operations."""

    @pytest.mark.asyncio
    async def test_get_issue(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_issue method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
                "status": {"name": "In Progress"},
            },
        }
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_issue("PROJ-123")

        assert result["key"] == "PROJ-123"
        assert result["summary"] == "Test Issue"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/3/issue/PROJ-123",
            params={"fields": "*all"},
        )

    @pytest.mark.asyncio
    async def test_get_issue_with_expand(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_issue with expand parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "key": "PROJ-123",
            "fields": {"summary": "Test"},
        }
        mock_http_client.get.return_value = mock_response

        await jira_service.get_issue("PROJ-123", expand="changelog")

        mock_http_client.get.assert_called_once_with(
            "/rest/api/3/issue/PROJ-123",
            params={"fields": "*all", "expand": "changelog"},
        )

    @pytest.mark.asyncio
    async def test_search(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test search method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "issues": [
                {"key": "PROJ-1", "fields": {"summary": "Issue 1"}},
                {"key": "PROJ-2", "fields": {"summary": "Issue 2"}},
            ],
            "total": 2,
        }
        mock_http_client.get.return_value = mock_response

        result = await jira_service.search("project = PROJ")

        assert len(result["issues"]) == 2
        assert result["total"] == 2
        assert result["start_at"] == 0
        assert result["max_results"] == 50

    @pytest.mark.asyncio
    async def test_get_transitions(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_transitions method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "transitions": [
                {"id": "1", "name": "In Progress"},
                {"id": "2", "name": "Done"},
            ]
        }
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_transitions("PROJ-123")

        assert len(result) == 2
        assert result[0]["name"] == "In Progress"
        mock_http_client.get.assert_called_once_with(
            "/rest/api/3/issue/PROJ-123/transitions"
        )

    @pytest.mark.asyncio
    async def test_get_comments(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_comments method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "comments": [
                {
                    "id": "1",
                    "body": {
                        "type": "doc",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": "Comment 1"}],
                            }
                        ],
                    },
                    "author": {"displayName": "User 1"},
                    "created": "2024-01-01",
                },
                {
                    "id": "2",
                    "body": {
                        "type": "doc",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": "Comment 2"}],
                            }
                        ],
                    },
                    "author": {"displayName": "User 2"},
                    "created": "2024-01-02",
                },
            ]
        }
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_comments("PROJ-123")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["author"] == "User 1"

    @pytest.mark.asyncio
    async def test_get_projects(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_projects method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = [
            {"key": "PROJ1", "name": "Project 1"},
            {"key": "PROJ2", "name": "Project 2"},
        ]
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_projects()

        assert len(result) == 2
        assert result[0]["key"] == "PROJ1"

    @pytest.mark.asyncio
    async def test_get_user_profile(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_user_profile method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "accountId": "123",
            "displayName": "Test User",
            "emailAddress": "test@example.com",
            "active": True,
            "timeZone": "UTC",
        }
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_user_profile()

        assert result["account_id"] == "123"
        assert result["display_name"] == "Test User"
        assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_fields(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_fields method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = [
            {"id": "summary", "name": "Summary"},
            {"id": "status", "name": "Status"},
        ]
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_fields()

        assert len(result) == 2
        assert result[0]["id"] == "summary"

    @pytest.mark.asyncio
    async def test_get_priorities(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_priorities method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = [
            {"id": "1", "name": "High"},
            {"id": "2", "name": "Medium"},
        ]
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_priorities()

        assert len(result) == 2
        assert result[0]["name"] == "High"

    @pytest.mark.asyncio
    async def test_get_resolutions(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test get_resolutions method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = [
            {"id": "1", "name": "Fixed"},
            {"id": "2", "name": "Won't Fix"},
        ]
        mock_http_client.get.return_value = mock_response

        result = await jira_service.get_resolutions()

        assert len(result) == 2
        assert result[0]["name"] == "Fixed"


class TestJiraServiceWriteOperations:
    """Test write operations."""

    @pytest.mark.asyncio
    async def test_create_issue(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "12345",
            "key": "PROJ-123",
        }
        mock_http_client.post.return_value = mock_response

        result = await jira_service.create_issue(
            project_key="PROJ",
            summary="Test Issue",
            issue_type="Task",
        )

        assert result["key"] == "PROJ-123"
        assert result["id"] == "12345"
        mock_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_issue_with_description(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue with description."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "key": "PROJ-1"}
        mock_http_client.post.return_value = mock_response

        await jira_service.create_issue(
            project_key="PROJ",
            summary="Test",
            issue_type="Task",
            description="Description text",
        )

        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["fields"]["description"]["type"] == "doc"

    @pytest.mark.asyncio
    async def test_update_issue(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.put.return_value = mock_response

        await jira_service.update_issue(
            issue_key="PROJ-123",
            summary="Updated Summary",
        )

        mock_http_client.put.assert_called_once()
        call_args = mock_http_client.put.call_args
        assert call_args[0][0] == "/rest/api/3/issue/PROJ-123"

    @pytest.mark.asyncio
    async def test_transition_issue(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test transition_issue method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.post.return_value = mock_response

        await jira_service.transition_issue(
            issue_key="PROJ-123",
            transition_id="21",
        )

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert "transitions" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_add_comment(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test add_comment method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "10001", "body": "Test comment"}
        mock_http_client.post.return_value = mock_response

        result = await jira_service.add_comment(
            issue_key="PROJ-123",
            body="Test comment",
        )

        assert result["id"] == "10001"
        mock_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_comment(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_comment method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.put.return_value = mock_response

        await jira_service.update_comment(
            issue_key="PROJ-123",
            comment_id="10001",
            body="Updated comment",
        )

        mock_http_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_comment(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test delete_comment method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.delete.return_value = mock_response

        await jira_service.delete_comment(
            issue_key="PROJ-123",
            comment_id="10001",
        )

        mock_http_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_issue(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test assign_issue method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.put.return_value = mock_response

        await jira_service.assign_issue(
            issue_key="PROJ-123",
            account_id="user-123",
        )

        mock_http_client.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_issue(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test delete_issue method."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.delete.return_value = mock_response

        await jira_service.delete_issue(issue_key="PROJ-123")

        mock_http_client.delete.assert_called_once_with(
            "/rest/api/3/issue/PROJ-123",
            params={"deleteSubtasks": "false"},
        )

    @pytest.mark.asyncio
    async def test_delete_issue_with_subtasks(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test delete_issue with subtasks."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_http_client.delete.return_value = mock_response

        await jira_service.delete_issue(
            issue_key="PROJ-123",
            delete_subtasks=True,
        )

        mock_http_client.delete.assert_called_once_with(
            "/rest/api/3/issue/PROJ-123",
            params={"deleteSubtasks": "true"},
        )


class TestJiraServiceHelpers:
    """Test helper methods."""

    def test_simplify_issue(self, jira_service: JiraService) -> None:
        """Test _simplify_issue method."""
        raw_issue = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
                "status": {"name": "In Progress"},
                "assignee": {"displayName": "Test User"},
                "description": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "Description"}],
                        }
                    ],
                },
            },
        }

        result = jira_service._simplify_issue(raw_issue)

        assert result["key"] == "PROJ-123"
        assert result["summary"] == "Test Issue"
        assert result["status"] == "In Progress"
        assert result["assignee"] == "Test User"

    def test_simplify_issue_minimal(self, jira_service: JiraService) -> None:
        """Test _simplify_issue with minimal data."""
        raw_issue = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
            },
        }

        result = jira_service._simplify_issue(raw_issue)

        assert result["key"] == "PROJ-123"
        assert result["summary"] == "Test Issue"
        assert result["status"] is None
        assert "assignee" not in result  # Optional field not present

    def test_create_adf(self, jira_service: JiraService) -> None:
        """Test _create_adf method."""
        text = "This is a test"

        result = jira_service._create_adf(text)

        assert result["type"] == "doc"
        assert result["version"] == 1
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "paragraph"
        assert result["content"][0]["content"][0]["text"] == text

    def test_extract_text(self, jira_service: JiraService) -> None:
        """Test _extract_text method."""
        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Hello "},
                        {"type": "text", "text": "World"},
                    ],
                }
            ],
        }

        result = jira_service._extract_text(adf)

        assert result == "Hello World"

    def test_extract_text_empty(
        self, jira_service: JiraService
    ) -> None:
        """Test _extract_text with empty content."""
        adf = {"type": "doc", "content": []}

        result = jira_service._extract_text(adf)

        assert result == ""

    def test_extract_text_nested(
        self, jira_service: JiraService
    ) -> None:
        """Test _extract_text with nested structure."""
        adf = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Paragraph 1"}],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Paragraph 2"}],
                },
            ],
        }

        result = jira_service._extract_text(adf)

        assert "Paragraph 1" in result
        assert "Paragraph 2" in result
