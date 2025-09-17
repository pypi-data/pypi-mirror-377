# vecta_backend/vecta/exceptions.py
"""Custom exceptions for the Vecta API client."""

from typing import Any, Optional


class VectaAPIError(Exception):
    """Base exception for all Vecta API SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class VectaAuthenticationError(VectaAPIError):
    """Raised when authentication fails (401 Unauthorized)."""

    pass


class VectaNotFoundError(VectaAPIError):
    """Raised when a resource is not found (404 Not Found)."""

    pass


class VectaBadRequestError(VectaAPIError):
    """Raised when the request is malformed or invalid (400 Bad Request)."""

    pass


class VectaServerError(VectaAPIError):
    """Raised when the server encounters an error (5xx status codes)."""

    pass


class VectaForbiddenError(VectaAPIError):
    """Raised when access is forbidden (403 Forbidden)."""

    pass


class VectaRateLimitError(VectaAPIError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""

    pass


class VectaInsufficientDataError(VectaBadRequestError):
    """Raised when trying to create benchmarks without enough chunks."""

    pass


class VectaNoBenchmarkError(VectaBadRequestError):
    """Raised when trying to create evaluations without a valid benchmark."""

    pass


class VectaUsageLimitError(VectaAPIError):
    """Raised when user has exceeded their token usage limit for the current billing cycle."""

    def __init__(
        self,
        message: str,
        current_usage: int,
        limit: int,
        plan: str,
        status_code: Optional[int] = 429,
    ) -> None:
        super().__init__(message, status_code)
        self.current_usage = current_usage
        self.limit = limit
        self.plan = plan
