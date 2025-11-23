"""Edge case tests for JiraService to achieve 100% coverage."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from atlassian_tools.jira.service import JiraService


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
def jira_service(mock_http_client: MagicMock) -> JiraService:
    """Create a JiraService with mocked client."""
    return JiraService(mock_http_client)


class TestCreateIssueEdgeCases:
    """Test create_issue with all optional parameters."""

    @pytest.mark.asyncio
    async def test_create_issue_with_priority(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue with priority parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "key": "PROJ-1"}
        mock_http_client.post.return_value = mock_response

        await jira_service.create_issue(
            project_key="PROJ",
            summary="Test",
            issue_type="Task",
            priority="High",
        )

        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["fields"]["priority"] == {"name": "High"}

    @pytest.mark.asyncio
    async def test_create_issue_with_assignee(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue with assignee parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "key": "PROJ-1"}
        mock_http_client.post.return_value = mock_response

        await jira_service.create_issue(
            project_key="PROJ",
            summary="Test",
            issue_type="Task",
            assignee="user-123",
        )

        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["fields"]["assignee"] == {"accountId": "user-123"}

    @pytest.mark.asyncio
    async def test_create_issue_with_labels(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue with labels parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "key": "PROJ-1"}
        mock_http_client.post.return_value = mock_response

        await jira_service.create_issue(
            project_key="PROJ",
            summary="Test",
            issue_type="Task",
            labels=["label1", "label2"],
        )

        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["fields"]["labels"] == ["label1", "label2"]

    @pytest.mark.asyncio
    async def test_create_issue_with_components(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue with components parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "key": "PROJ-1"}
        mock_http_client.post.return_value = mock_response

        await jira_service.create_issue(
            project_key="PROJ",
            summary="Test",
            issue_type="Task",
            components=["Backend", "API"],
        )

        call_args = mock_http_client.post.call_args
        expected_components = [{"name": "Backend"}, {"name": "API"}]
        assert call_args[1]["json"]["fields"]["components"] == expected_components

    @pytest.mark.asyncio
    async def test_create_issue_with_custom_fields(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test create_issue with custom_fields parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "123", "key": "PROJ-1"}
        mock_http_client.post.return_value = mock_response

        await jira_service.create_issue(
            project_key="PROJ",
            summary="Test",
            issue_type="Task",
            custom_fields={"customfield_10001": "value1"},
        )

        call_args = mock_http_client.post.call_args
        assert call_args[1]["json"]["fields"]["customfield_10001"] == "value1"


class TestUpdateIssueEdgeCases:
    """Test update_issue with all optional parameters."""

    @pytest.mark.asyncio
    async def test_update_issue_with_summary(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue with summary parameter."""
        mock_http_client.put.return_value = MagicMock(spec=httpx.Response)

        await jira_service.update_issue(
            issue_key="PROJ-123",
            summary="Updated Summary",
        )

        call_args = mock_http_client.put.call_args
        assert call_args[1]["json"]["fields"]["summary"] == "Updated Summary"

    @pytest.mark.asyncio
    async def test_update_issue_with_description(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue with description parameter."""
        mock_http_client.put.return_value = MagicMock(spec=httpx.Response)

        await jira_service.update_issue(
            issue_key="PROJ-123",
            description="New description",
        )

        call_args = mock_http_client.put.call_args
        assert call_args[1]["json"]["fields"]["description"]["type"] == "doc"

    @pytest.mark.asyncio
    async def test_update_issue_with_priority(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue with priority parameter."""
        mock_http_client.put.return_value = MagicMock(spec=httpx.Response)

        await jira_service.update_issue(
            issue_key="PROJ-123",
            priority="Critical",
        )

        call_args = mock_http_client.put.call_args
        assert call_args[1]["json"]["fields"]["priority"] == {"name": "Critical"}

    @pytest.mark.asyncio
    async def test_update_issue_with_assignee(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue with assignee parameter."""
        mock_http_client.put.return_value = MagicMock(spec=httpx.Response)

        await jira_service.update_issue(
            issue_key="PROJ-123",
            assignee="user-456",
        )

        call_args = mock_http_client.put.call_args
        assert call_args[1]["json"]["fields"]["assignee"] == {"accountId": "user-456"}

    @pytest.mark.asyncio
    async def test_update_issue_with_labels(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue with labels parameter."""
        mock_http_client.put.return_value = MagicMock(spec=httpx.Response)

        await jira_service.update_issue(
            issue_key="PROJ-123",
            labels=["updated", "tags"],
        )

        call_args = mock_http_client.put.call_args
        assert call_args[1]["json"]["fields"]["labels"] == ["updated", "tags"]

    @pytest.mark.asyncio
    async def test_update_issue_with_custom_fields(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test update_issue with custom_fields parameter."""
        mock_http_client.put.return_value = MagicMock(spec=httpx.Response)

        await jira_service.update_issue(
            issue_key="PROJ-123",
            custom_fields={"customfield_10002": "updated_value"},
        )

        call_args = mock_http_client.put.call_args
        assert call_args[1]["json"]["fields"]["customfield_10002"] == "updated_value"


class TestSearchEdgeCases:
    """Test search with all optional parameters."""

    @pytest.mark.asyncio
    async def test_search_with_fields(
        self, jira_service: JiraService, mock_http_client: MagicMock
    ) -> None:
        """Test search with fields parameter."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "total": 0,
            "issues": [],
        }
        mock_http_client.get.return_value = mock_response

        await jira_service.search(
            jql="project = PROJ",
            fields="summary,status",
        )

        call_args = mock_http_client.get.call_args
        assert "summary" in call_args[1]["params"]["fields"]
