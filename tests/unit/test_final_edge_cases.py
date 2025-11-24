"""Final edge case tests to achieve 100% coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from atlassian_tools._core.exceptions import (
    AtlassianError,
    AtlassianTimeoutError,
    NetworkError,
)


class TestJiraToolsEdgeCases:
    """Test edge cases in Jira tools."""

    @pytest.mark.asyncio
    async def test_get_project_issues_with_status(self) -> None:
        """Test jira_get_project_issues with status parameter."""
        mock_service = MagicMock()
        mock_service.search = AsyncMock(
            return_value={
                "issues": [{"key": "PROJ-1", "fields": {"summary": "Test"}}],
                "total": 1,
            }
        )

        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            return_value=mock_service,
        ):
            from atlassian_tools.jira.models import JiraGetProjectIssuesInput
            from atlassian_tools.jira.tools import jira_get_project_issues

            result = await jira_get_project_issues(
                JiraGetProjectIssuesInput(project_key="PROJ", status="Done")
            )

        assert result.success is True
        # Verify that status was included in JQL
        call_args = mock_service.search.call_args
        jql = call_args[1]["jql"]
        assert "status = 'Done'" in jql

    @pytest.mark.asyncio
    async def test_batch_create_issues_outer_error(self) -> None:
        """Test jira_batch_create_issues outer AtlassianError handler."""
        # Outer handler catches errors from get_jira_service()
        with patch(
            "atlassian_tools.jira.tools.get_jira_service",
            side_effect=AtlassianError("Service initialization failed"),
        ):
            from atlassian_tools.jira.models import JiraBatchCreateIssuesInput
            from atlassian_tools.jira.tools import jira_batch_create_issues

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
        assert "Service initialization failed" in result.error


class TestJiraServiceEdgeCases:
    """Test edge cases in JiraService."""

    @pytest.mark.asyncio
    async def test_transition_issue_with_comment(self) -> None:
        """Test transition_issue with comment parameter."""
        from atlassian_tools.jira.service import JiraService

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=MagicMock(spec=httpx.Response))
        service = JiraService(mock_client)

        await service.transition_issue(
            issue_key="PROJ-1",
            transition_id="21",
            comment="Transition comment",
        )

        call_args = mock_client.post.call_args
        assert "update" in call_args[1]["json"]
        assert "comment" in call_args[1]["json"]["update"]

    def test_simplify_issue_with_optional_fields(self) -> None:
        """Test _simplify_issue with all optional fields."""
        from atlassian_tools.jira.service import JiraService

        service = JiraService(MagicMock())
        issue = {
            "key": "PROJ-1",
            "fields": {
                "summary": "Test",
                "status": {"name": "Done"},
                "issuetype": {"name": "Task"},
                "reporter": {"displayName": "John Doe"},
                "priority": {"name": "High"},
                "description": {"type": "doc", "content": [{"type": "text", "text": "Desc"}]},
                "labels": ["label1", "label2"],
                "created": "2023-01-01T00:00:00.000Z",
                "updated": "2023-01-02T00:00:00.000Z",
            },
        }

        result = service._simplify_issue(issue)

        assert result["reporter"] == "John Doe"
        assert result["priority"] == "High"
        assert result["labels"] == ["label1", "label2"]
        assert result["created"] == "2023-01-01T00:00:00.000Z"
        assert result["updated"] == "2023-01-02T00:00:00.000Z"

    def test_extract_text_with_invalid_adf(self) -> None:
        """Test _extract_text with None and non-dict ADF."""
        from atlassian_tools.jira.service import JiraService

        service = JiraService(MagicMock())

        # Test with None
        assert service._extract_text(None) == ""

        # Test with non-dict
        assert service._extract_text("not a dict") == ""

        # Test with empty dict
        assert service._extract_text({}) == ""


class TestConfluenceServiceEdgeCases:
    """Test edge cases in ConfluenceService."""

    def test_simplify_page_with_links(self) -> None:
        """Test _simplify_page with _links field."""
        from atlassian_tools.confluence.service import ConfluenceService

        service = ConfluenceService(MagicMock())
        page = {
            "id": "123",
            "type": "page",
            "title": "Test",
            "space": {"key": "SPACE"},
            "_links": {"webui": "/pages/123"},
        }

        result = service._simplify_page(page)

        assert result["url"] == "/pages/123"


class TestHttpClientErrorHandling:
    """Test HTTP client network and timeout error handling."""

    @pytest.mark.asyncio
    async def test_error_message_extraction_string(self) -> None:
        """Test error message extraction when errorMessages is a string."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.exceptions import ValidationError
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "errorMessages": "Single error message"
        }

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ValidationError) as exc_info:
                await client.get("/test")
            assert "Single error message" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_error_message_extraction_non_dict(self) -> None:
        """Test error message extraction when response is not a dict."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.exceptions import ValidationError
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.json.return_value = "String response"

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ValidationError) as exc_info:
                await client.get("/test")
            assert "String response" in str(exc_info.value)

    def test_client_singletons(self) -> None:
        """Test client singleton getters and cache clearing."""
        from atlassian_tools._core.http_client import (
            clear_client_cache,
            get_confluence_client,
            get_jira_client,
        )

        # Clear cache first
        clear_client_cache()

        # Get Jira client
        jira_client1 = get_jira_client()
        jira_client2 = get_jira_client()
        assert jira_client1 is jira_client2  # Should be same instance

        # Get Confluence client
        confluence_client1 = get_confluence_client()
        confluence_client2 = get_confluence_client()
        assert confluence_client1 is confluence_client2  # Should be same instance

        # Clear and verify new instances
        clear_client_cache()
        jira_client3 = get_jira_client()
        assert jira_client3 is not jira_client1  # Should be different after clear

    @pytest.mark.asyncio
    async def test_get_network_error(self) -> None:
        """Test GET with network error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.get",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError) as exc_info:
                await client.get("/test")
            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_timeout_error(self) -> None:
        """Test GET with timeout error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.get",
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(AtlassianTimeoutError) as exc_info:
                await client.get("/test")
            assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_post_network_error(self) -> None:
        """Test POST with network error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError) as exc_info:
                await client.post("/test", json={"key": "value"})
            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_post_timeout_error(self) -> None:
        """Test POST with timeout error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.post",
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(AtlassianTimeoutError) as exc_info:
                await client.post("/test", json={"key": "value"})
            assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_put_network_error(self) -> None:
        """Test PUT with network error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.put",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError) as exc_info:
                await client.put("/test", json={"key": "value"})
            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_put_timeout_error(self) -> None:
        """Test PUT with timeout error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.put",
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(AtlassianTimeoutError) as exc_info:
                await client.put("/test", json={"key": "value"})
            assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_network_error(self) -> None:
        """Test DELETE with network error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.delete",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError) as exc_info:
                await client.delete("/test")
            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_timeout_error(self) -> None:
        """Test DELETE with timeout error."""
        from atlassian_tools._core.config import JiraConfig
        from atlassian_tools._core.http_client import AtlassianHttpClient

        config = JiraConfig(
            url="https://test.atlassian.net",
            username="test@example.com",
            api_token="token",
        )
        client = AtlassianHttpClient(config)

        with patch(
            "httpx.AsyncClient.delete",
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(AtlassianTimeoutError) as exc_info:
                await client.delete("/test")
            assert "timed out" in str(exc_info.value)
