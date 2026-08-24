"""Custom exceptions for the EliaAI Subworker Server."""
from __future__ import annotations


class SubworkerError(Exception):
    """Base exception for all subworker server errors."""


class OpenCodeError(SubworkerError):
    """OpenCode API returned an error response."""

    def __init__(self, message: str, status_code: int | None = None, detail: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class OpenCodeConnectionError(OpenCodeError):
    """Cannot connect to the OpenCode server."""


class OpenCodeTimeoutError(OpenCodeError):
    """OpenCode API request timed out."""


class OpenCodeSessionError(OpenCodeError):
    """OpenCode session operation failed (create, send, status)."""


class RateLimitError(OpenCodeError):
    """OpenCode API rate limit exceeded."""


class ConfigError(SubworkerError):
    """Configuration file is invalid or missing."""


class SchedulerError(SubworkerError):
    """Scheduler operation failed."""


class AlertError(SubworkerError):
    """Alert dispatch failed."""
