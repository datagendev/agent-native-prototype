"""Custom exception classes for the webhook service."""

from typing import Any


class WebhookServiceException(Exception):
    """Base exception for all webhook service errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(WebhookServiceException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str | None = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=message, status_code=404)


class BadRequestException(WebhookServiceException):
    """Bad request / validation error."""

    def __init__(self, message: str = "Bad request", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=400, details=details)


class UnauthorizedException(WebhookServiceException):
    """Unauthorized access."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(WebhookServiceException):
    """Forbidden access."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)


class RateLimitExceededException(WebhookServiceException):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            details={"retry_after": retry_after},
        )
        self.retry_after = retry_after


class ConflictException(WebhookServiceException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)
