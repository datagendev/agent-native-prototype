"""Custom exceptions for the webhook service."""

from .base import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    RateLimitExceededException,
    UnauthorizedException,
    WebhookServiceException,
)

__all__ = [
    "WebhookServiceException",
    "NotFoundException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "RateLimitExceededException",
    "ConflictException",
]
