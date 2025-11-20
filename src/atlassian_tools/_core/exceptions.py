"""Exception hierarchy for Atlassian tools.

This module defines typed exceptions for better error handling and
more informative error messages throughout the package.
"""


class AtlassianError(Exception):
    """Base exception for all Atlassian operations."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ConfigurationError(AtlassianError):
    """Missing or invalid configuration.

    Raised when required environment variables are missing or invalid.
    """

    def __init__(self, message: str = "Missing required configuration") -> None:
        super().__init__(message)


class AuthenticationError(AtlassianError):
    """Authentication failed (HTTP 401).

    Raised when API credentials are invalid or expired.
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class AuthorizationError(AtlassianError):
    """Permission denied (HTTP 403).

    Raised when the user lacks permission for the requested operation.
    """

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, status_code=403)


class NotFoundError(AtlassianError):
    """Resource not found (HTTP 404).

    Raised when the requested resource does not exist.
    """

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ValidationError(AtlassianError):
    """Request validation failed (HTTP 400).

    Raised when the request contains invalid data.
    """

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=400)


class RateLimitError(AtlassianError):
    """Rate limit exceeded (HTTP 429).

    Raised when API rate limits are exceeded.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ServiceError(AtlassianError):
    """Server-side error (HTTP 5xx).

    Raised when the Atlassian server returns an error.
    """

    def __init__(
        self,
        message: str = "Service unavailable",
        status_code: int = 500,
    ) -> None:
        super().__init__(message, status_code=status_code)


class NetworkError(AtlassianError):
    """Network connectivity error.

    Raised when there are network issues connecting to the API.
    """

    def __init__(self, message: str = "Network error") -> None:
        super().__init__(message)


class AtlassianTimeoutError(AtlassianError):
    """Request timeout.

    Raised when the API request times out.
    """

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)


__all__ = [
    "AtlassianError",
    "ConfigurationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServiceError",
    "NetworkError",
    "AtlassianTimeoutError",
]
