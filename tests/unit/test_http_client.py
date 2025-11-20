"""Unit tests for AtlassianHttpClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from atlassian_tools._core.config import JiraConfig
from atlassian_tools._core.exceptions import (
    AtlassianError,
    AtlassianTimeoutError,
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServiceError,
    ValidationError,
)
from atlassian_tools._core.http_client import AtlassianHttpClient


@pytest.fixture
def jira_config() -> JiraConfig:
    """Create a test Jira configuration."""
    return JiraConfig(
        url="https://test.atlassian.net",
        username="test@example.com",
        api_token="test-token",
        timeout=30,
        max_retries=3,
    )


@pytest.fixture
async def http_client(jira_config: JiraConfig) -> AtlassianHttpClient:
    """Create an HTTP client for testing."""
    client = AtlassianHttpClient(jira_config)
    yield client
    await client.close()


class TestAtlassianHttpClientInitialization:
    """Test HTTP client initialization and lifecycle."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, jira_config: JiraConfig) -> None:
        """Test client initializes with config."""
        client = AtlassianHttpClient(jira_config)
        assert client._config == jira_config
        assert client._client is None

    @pytest.mark.asyncio
    async def test_client_get_or_create(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test _get_client creates client on first call."""
        assert http_client._client is None
        client = await http_client._get_client()
        assert isinstance(client, httpx.AsyncClient)
        assert http_client._client is not None

        # Second call returns same instance
        client2 = await http_client._get_client()
        assert client is client2

    @pytest.mark.asyncio
    async def test_client_close(self, http_client: AtlassianHttpClient) -> None:
        """Test client closes and releases resources."""
        await http_client._get_client()
        assert http_client._client is not None

        await http_client.close()
        assert http_client._client is None


class TestAtlassianHttpClientHTTPMethods:
    """Test HTTP methods (GET, POST, PUT, DELETE)."""

    @pytest.mark.asyncio
    async def test_get_success(self, http_client: AtlassianHttpClient) -> None:
        """Test successful GET request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"key": "PROJ-123"}

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = await http_client.get("/rest/api/3/issue/PROJ-123")
            assert response.status_code == 200
            assert response.json() == {"key": "PROJ-123"}

    @pytest.mark.asyncio
    async def test_get_with_params(self, http_client: AtlassianHttpClient) -> None:
        """Test GET request with query parameters."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.is_success = True

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_get:
            await http_client.get(
                "/rest/api/3/search",
                params={"jql": "project = PROJ", "maxResults": 20},
            )
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_success(self, http_client: AtlassianHttpClient) -> None:
        """Test successful POST request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "12345", "key": "PROJ-123"}

        with patch.object(
            httpx.AsyncClient,
            "post",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = await http_client.post(
                "/rest/api/3/issue",
                json={"fields": {"summary": "Test Issue"}},
            )
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_post_with_data(self, http_client: AtlassianHttpClient) -> None:
        """Test POST request with raw data."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 204
        mock_response.is_success = True

        with patch.object(
            httpx.AsyncClient,
            "post",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_post:
            await http_client.post(
                "/rest/api/3/issue/PROJ-123/watchers",
                data='"account-id-123"',
            )
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_put_success(self, http_client: AtlassianHttpClient) -> None:
        """Test successful PUT request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 204
        mock_response.is_success = True

        with patch.object(
            httpx.AsyncClient,
            "put",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = await http_client.put(
                "/rest/api/3/issue/PROJ-123",
                json={"fields": {"summary": "Updated"}},
            )
            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_success(self, http_client: AtlassianHttpClient) -> None:
        """Test successful DELETE request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 204
        mock_response.is_success = True

        with patch.object(
            httpx.AsyncClient,
            "delete",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = await http_client.delete("/rest/api/3/issue/PROJ-123")
            assert response.status_code == 204


class TestAtlassianHttpClientErrorHandling:
    """Test HTTP error status code handling."""

    @pytest.mark.asyncio
    async def test_handle_400_validation_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 400 response raises ValidationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Field 'summary' is required"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ValidationError, match="Validation failed"):
                await http_client.get("/rest/api/3/issue")

    @pytest.mark.asyncio
    async def test_handle_401_authentication_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 401 response raises AuthenticationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Authentication failed"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(AuthenticationError, match="Authentication failed"):
                await http_client.get("/rest/api/3/myself")

    @pytest.mark.asyncio
    async def test_handle_403_authorization_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 403 response raises AuthorizationError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["You do not have permission"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(AuthorizationError, match="Permission denied"):
                await http_client.get("/rest/api/3/issue/PROJ-123")

    @pytest.mark.asyncio
    async def test_handle_404_not_found_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 404 response raises NotFoundError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Issue does not exist"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(NotFoundError, match="Not found"):
                await http_client.get("/rest/api/3/issue/INVALID-123")

    @pytest.mark.asyncio
    async def test_handle_429_rate_limit_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 429 response raises RateLimitError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Rate limit exceeded"]
        }
        mock_response.headers = {}

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                await http_client.get("/rest/api/3/search")

    @pytest.mark.asyncio
    async def test_handle_429_with_retry_after_header(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 429 response with Retry-After header."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Rate limit exceeded"]
        }
        mock_response.headers = {"Retry-After": "60"}

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(RateLimitError) as exc_info:
                await http_client.get("/rest/api/3/search")
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_handle_500_service_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 500 response raises ServiceError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Internal server error"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ServiceError, match="Server error"):
                await http_client.get("/rest/api/3/issue/PROJ-123")

    @pytest.mark.asyncio
    async def test_handle_502_bad_gateway(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 502 response raises ServiceError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 502
        mock_response.is_success = False
        mock_response.text = "Bad Gateway"
        mock_response.json.side_effect = Exception()

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ServiceError, match="Server error"):
                await http_client.get("/rest/api/3/issue/PROJ-123")

    @pytest.mark.asyncio
    async def test_handle_503_service_unavailable(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test 503 response raises ServiceError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 503
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Service unavailable"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ServiceError, match="Server error"):
                await http_client.get("/rest/api/3/issue/PROJ-123")


class TestAtlassianHttpClientNetworkErrors:
    """Test network error handling."""

    @pytest.mark.asyncio
    async def test_connection_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test connection failure raises NetworkError."""
        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError, match="Connection failed"):
                await http_client.get("/rest/api/3/issue/PROJ-123")

    @pytest.mark.asyncio
    async def test_timeout_error(self, http_client: AtlassianHttpClient) -> None:
        """Test request timeout raises TimeoutError."""
        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(AtlassianTimeoutError, match="Request timed out"):
                await http_client.get("/rest/api/3/issue/PROJ-123")

    @pytest.mark.asyncio
    async def test_post_connection_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test POST connection failure raises NetworkError."""
        with patch.object(
            httpx.AsyncClient,
            "post",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError):
                await http_client.post("/rest/api/3/issue", json={})

    @pytest.mark.asyncio
    async def test_put_timeout_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test PUT timeout raises TimeoutError."""
        with patch.object(
            httpx.AsyncClient,
            "put",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(AtlassianTimeoutError):
                await http_client.put("/rest/api/3/issue/PROJ-123", json={})

    @pytest.mark.asyncio
    async def test_delete_connection_error(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test DELETE connection failure raises NetworkError."""
        with patch.object(
            httpx.AsyncClient,
            "delete",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(NetworkError):
                await http_client.delete("/rest/api/3/issue/PROJ-123")


class TestAtlassianHttpClientEdgeCases:
    """Test edge cases and error response parsing."""

    @pytest.mark.asyncio
    async def test_empty_response_body(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test error with empty response body."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.json.side_effect = Exception()
        mock_response.text = ""

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(NotFoundError, match="HTTP 404"):
                await http_client.get("/rest/api/3/issue/INVALID")

    @pytest.mark.asyncio
    async def test_malformed_json_error_response(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test error with malformed JSON response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.json.side_effect = Exception()
        mock_response.text = "<html>Internal Server Error</html>"

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ServiceError, match="Server error"):
                await http_client.get("/rest/api/3/issue/PROJ-123")

    @pytest.mark.asyncio
    async def test_non_standard_error_format(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test error response with non-standard format."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.is_success = False
        mock_response.json.return_value = {
            "message": "Invalid request"
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ValidationError, match="Invalid request"):
                await http_client.get("/rest/api/3/issue")

    @pytest.mark.asyncio
    async def test_error_messages_list(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test error response with list of messages."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.is_success = False
        mock_response.json.return_value = {
            "errorMessages": ["Error 1", "Error 2", "Error 3"]
        }

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(ValidationError, match="Error 1; Error 2; Error 3"):
                await http_client.get("/rest/api/3/issue")

    @pytest.mark.asyncio
    async def test_unhandled_status_code(
        self, http_client: AtlassianHttpClient
    ) -> None:
        """Test unhandled status code raises generic AtlassianError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 418  # I'm a teapot
        mock_response.is_success = False
        mock_response.json.return_value = {"errorMessages": ["I'm a teapot"]}

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            with pytest.raises(AtlassianError, match="HTTP 418"):
                await http_client.get("/rest/api/3/issue/PROJ-123")
