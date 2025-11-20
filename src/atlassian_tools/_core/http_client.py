"""HTTP client abstraction for Atlassian APIs.

This module provides an async HTTP client with automatic error handling,
retries, and connection pooling using httpx.
"""

from typing import Any

import httpx

from atlassian_tools._core.config import ConfluenceConfig, JiraConfig
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


class AtlassianHttpClient:
    """Async HTTP client for Atlassian APIs.

    Handles authentication, error mapping, retries, and connection pooling.
    """

    def __init__(self, config: JiraConfig | ConfluenceConfig) -> None:
        """Initialize the HTTP client.

        Args:
            config: Configuration object with URL and credentials.
        """
        self._config = config
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._config.url,
                auth=(self._config.username, self._config.api_token),
                timeout=httpx.Timeout(self._config.timeout),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _handle_response(self, response: httpx.Response) -> None:
        """Check response status and raise appropriate exceptions.

        Args:
            response: The HTTP response to check.

        Raises:
            AuthenticationError: For 401 responses.
            AuthorizationError: For 403 responses.
            NotFoundError: For 404 responses.
            ValidationError: For 400 responses.
            RateLimitError: For 429 responses.
            ServiceError: For 5xx responses.
        """
        if response.is_success:
            return

        status_code = response.status_code

        # Try to extract error message from response
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                error_msg = error_data.get("errorMessages", [])
                if error_msg:
                    if isinstance(error_msg, list):
                        error_msg = "; ".join(error_msg)
                    else:
                        error_msg = str(error_msg)
                else:
                    error_msg = error_data.get("message", str(error_data))
            else:
                error_msg = str(error_data)
        except Exception:
            error_msg = response.text or f"HTTP {status_code}"

        if status_code == 400:
            msg = f"Validation failed: {error_msg}"
            raise ValidationError(msg)
        elif status_code == 401:
            msg = f"Authentication failed: {error_msg}"
            raise AuthenticationError(msg)
        elif status_code == 403:
            msg = f"Permission denied: {error_msg}"
            raise AuthorizationError(msg)
        elif status_code == 404:
            msg = f"Not found: {error_msg}"
            raise NotFoundError(msg)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            msg = f"Rate limit exceeded: {error_msg}"
            raise RateLimitError(
                msg,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif status_code >= 500:
            msg = f"Server error: {error_msg}"
            raise ServiceError(msg, status_code=status_code)
        else:
            msg = f"HTTP {status_code}: {error_msg}"
            raise AtlassianError(msg, status_code=status_code)

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Perform an async GET request.

        Args:
            endpoint: API endpoint (relative to base URL).
            params: Query parameters.

        Returns:
            The HTTP response.

        Raises:
            AtlassianError: On API errors.
            NetworkError: On connection errors.
            TimeoutError: On request timeout.
        """
        try:
            client = await self._get_client()
            response = await client.get(endpoint, params=params)
            self._handle_response(response)
            return response
        except httpx.ConnectError as e:
            msg = f"Connection failed: {e}"
            raise NetworkError(msg) from e
        except httpx.TimeoutException as e:
            msg = f"Request timed out: {e}"
            raise AtlassianTimeoutError(msg) from e

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Perform an async POST request.

        Args:
            endpoint: API endpoint (relative to base URL).
            json: JSON body data.
            data: Raw string data.
            params: Query parameters.

        Returns:
            The HTTP response.

        Raises:
            AtlassianError: On API errors.
            NetworkError: On connection errors.
            TimeoutError: On request timeout.
        """
        try:
            client = await self._get_client()
            if data is not None:
                response = await client.post(
                    endpoint,
                    content=data,
                    params=params,
                )
            else:
                response = await client.post(
                    endpoint,
                    json=json,
                    params=params,
                )
            self._handle_response(response)
            return response
        except httpx.ConnectError as e:
            msg = f"Connection failed: {e}"
            raise NetworkError(msg) from e
        except httpx.TimeoutException as e:
            msg = f"Request timed out: {e}"
            raise AtlassianTimeoutError(msg) from e

    async def put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Perform an async PUT request.

        Args:
            endpoint: API endpoint (relative to base URL).
            json: JSON body data.
            params: Query parameters.

        Returns:
            The HTTP response.

        Raises:
            AtlassianError: On API errors.
            NetworkError: On connection errors.
            TimeoutError: On request timeout.
        """
        try:
            client = await self._get_client()
            response = await client.put(endpoint, json=json, params=params)
            self._handle_response(response)
            return response
        except httpx.ConnectError as e:
            msg = f"Connection failed: {e}"
            raise NetworkError(msg) from e
        except httpx.TimeoutException as e:
            msg = f"Request timed out: {e}"
            raise AtlassianTimeoutError(msg) from e

    async def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Perform an async DELETE request.

        Args:
            endpoint: API endpoint (relative to base URL).
            params: Query parameters.

        Returns:
            The HTTP response.

        Raises:
            AtlassianError: On API errors.
            NetworkError: On connection errors.
            TimeoutError: On request timeout.
        """
        try:
            client = await self._get_client()
            response = await client.delete(endpoint, params=params)
            self._handle_response(response)
            return response
        except httpx.ConnectError as e:
            msg = f"Connection failed: {e}"
            raise NetworkError(msg) from e
        except httpx.TimeoutException as e:
            msg = f"Request timed out: {e}"
            raise AtlassianTimeoutError(msg) from e


# Singleton instances for reuse
_jira_client: AtlassianHttpClient | None = None
_confluence_client: AtlassianHttpClient | None = None


def get_jira_client() -> AtlassianHttpClient:
    """Get the Jira HTTP client singleton.

    Returns:
        AtlassianHttpClient configured for Jira API.
    """
    global _jira_client
    if _jira_client is None:
        from atlassian_tools._core.config import get_jira_config
        _jira_client = AtlassianHttpClient(get_jira_config())
    return _jira_client


def get_confluence_client() -> AtlassianHttpClient:
    """Get the Confluence HTTP client singleton.

    Returns:
        AtlassianHttpClient configured for Confluence API.
    """
    global _confluence_client
    if _confluence_client is None:
        from atlassian_tools._core.config import get_confluence_config
        _confluence_client = AtlassianHttpClient(get_confluence_config())
    return _confluence_client


def clear_client_cache() -> None:
    """Clear cached clients (useful for testing)."""
    global _jira_client, _confluence_client
    _jira_client = None
    _confluence_client = None


__all__ = [
    "AtlassianHttpClient",
    "get_jira_client",
    "get_confluence_client",
    "clear_client_cache",
]
