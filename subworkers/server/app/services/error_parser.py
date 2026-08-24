"""Error classification for API responses, exit codes, and log patterns."""
from __future__ import annotations

import enum
import random
import re
from dataclasses import dataclass


class ErrorType(enum.Enum):
    """Classified error types for subworker failures."""

    RATE_LIMIT = "rate_limit"
    AUTH_FAILURE = "auth_failure"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"
    MODEL_UNAVAILABLE = "model_unavailable"
    SSE_DISCONNECT = "sse_disconnect"
    IDLE_TIMEOUT = "idle_timeout"
    UNKNOWN = "unknown"


# ── Retriability rules ────────────────────────────────────────────────

_RETRIABLE: frozenset[ErrorType] = frozenset(
    {
        ErrorType.RATE_LIMIT,
        ErrorType.SERVER_ERROR,
        ErrorType.TIMEOUT,
        ErrorType.MODEL_UNAVAILABLE,
        ErrorType.SSE_DISCONNECT,
        ErrorType.IDLE_TIMEOUT,
    }
)

# ── Backoff schedules (seconds) ──────────────────────────────────────

_BACKOFF_SCHEDULES: dict[ErrorType, list[int]] = {
    ErrorType.RATE_LIMIT: [300, 600, 1800],          # 5m, 10m, 30m
    ErrorType.SERVER_ERROR: [2, 4, 8, 16, 32, 60],   # exponential
    ErrorType.TIMEOUT: [5, 10, 30, 60],
    ErrorType.MODEL_UNAVAILABLE: [30, 60, 120],
    ErrorType.SSE_DISCONNECT: [5, 10, 30],
    ErrorType.IDLE_TIMEOUT: [10, 30, 60],
}

# ── Log pattern regexes ──────────────────────────────────────────────

_LOG_PATTERNS: list[tuple[re.Pattern[str], ErrorType]] = [
    (re.compile(r"no\s+events?\s+received", re.IGNORECASE), ErrorType.IDLE_TIMEOUT),
    (re.compile(r"idle\s+timeout", re.IGNORECASE), ErrorType.IDLE_TIMEOUT),
    (re.compile(r"sse\s+disconnect", re.IGNORECASE), ErrorType.SSE_DISCONNECT),
    (re.compile(r"connection\s+reset\s+by\s+peer", re.IGNORECASE), ErrorType.SSE_DISCONNECT),
    (re.compile(r"upstream\s+timed?\s*out", re.IGNORECASE), ErrorType.TIMEOUT),
    (re.compile(r"read\s+timed?\s*out", re.IGNORECASE), ErrorType.TIMEOUT),
    (re.compile(r"rate\s+limit", re.IGNORECASE), ErrorType.RATE_LIMIT),
    (re.compile(r"429", re.IGNORECASE), ErrorType.RATE_LIMIT),
    (re.compile(r"model\s+unavailable", re.IGNORECASE), ErrorType.MODEL_UNAVAILABLE),
    (re.compile(r"overloaded", re.IGNORECASE), ErrorType.MODEL_UNAVAILABLE),
]

# ── HTTP status → ErrorType ──────────────────────────────────────────

_STATUS_MAP: dict[int, ErrorType] = {
    401: ErrorType.AUTH_FAILURE,
    403: ErrorType.AUTH_FAILURE,
    404: ErrorType.NOT_FOUND,
    429: ErrorType.RATE_LIMIT,
}

# ── API message keywords → ErrorType ─────────────────────────────────

_MESSAGE_KEYWORDS: list[tuple[str, ErrorType]] = [
    ("rate limit", ErrorType.RATE_LIMIT),
    ("quota exceeded", ErrorType.RATE_LIMIT),
    ("too many requests", ErrorType.RATE_LIMIT),
    ("unauthorized", ErrorType.AUTH_FAILURE),
    ("invalid api key", ErrorType.AUTH_FAILURE),
    ("forbidden", ErrorType.AUTH_FAILURE),
    ("model unavailable", ErrorType.MODEL_UNAVAILABLE),
    ("model not found", ErrorType.MODEL_UNAVAILABLE),
    ("overloaded", ErrorType.MODEL_UNAVAILABLE),
    ("upstream timeout", ErrorType.TIMEOUT),
    ("gateway timeout", ErrorType.TIMEOUT),
    ("request timeout", ErrorType.TIMEOUT),
]


# ── Parsed error result ──────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ParsedError:
    """Result of parsing an error from any source."""

    error_type: ErrorType
    message: str
    retriable: bool = True


class ErrorParser:
    """Classify errors from HTTP responses, exit codes, and logs."""

    # ── HTTP status codes ────────────────────────────────────────────

    @staticmethod
    def parse_http_status(status_code: int, body: str = "") -> ParsedError:
        """Parse an HTTP status code into a classified error."""
        if status_code in _STATUS_MAP:
            error_type = _STATUS_MAP[status_code]
            msg = f"HTTP {status_code}: {body}" if body else f"HTTP {status_code}"
            return ParsedError(error_type=error_type, message=msg, retriable=error_type in _RETRIABLE)

        if 500 <= status_code < 600:
            msg = f"HTTP {status_code}: {body}" if body else f"HTTP {status_code}"
            return ParsedError(error_type=ErrorType.SERVER_ERROR, message=msg, retriable=True)

        msg = f"HTTP {status_code}: {body}" if body else f"HTTP {status_code}"
        return ParsedError(error_type=ErrorType.UNKNOWN, message=msg, retriable=False)

    # ── API error messages ───────────────────────────────────────────

    @staticmethod
    def parse_api_message(message: str) -> ParsedError:
        """Parse an API error message string for known keywords."""
        lower = message.lower()
        for keyword, error_type in _MESSAGE_KEYWORDS:
            if keyword in lower:
                return ParsedError(
                    error_type=error_type,
                    message=message,
                    retriable=error_type in _RETRIABLE,
                )
        return ParsedError(error_type=ErrorType.UNKNOWN, message=message, retriable=False)

    # ── Exit codes ───────────────────────────────────────────────────

    @staticmethod
    def parse_exit_code(code: int) -> ParsedError:
        """Classify a subprocess exit code."""
        if code == 0:
            return ParsedError(error_type=ErrorType.UNKNOWN, message="exit 0 (success)", retriable=False)
        if code == 124:
            return ParsedError(error_type=ErrorType.TIMEOUT, message="exit 124 (timeout)", retriable=True)
        if code == 137:
            return ParsedError(error_type=ErrorType.TIMEOUT, message="exit 137 (killed/OOM)", retriable=True)
        return ParsedError(
            error_type=ErrorType.UNKNOWN,
            message=f"exit {code}",
            retriable=False,
        )

    # ── Log content patterns ─────────────────────────────────────────

    @staticmethod
    def parse_log_content(content: str) -> ParsedError:
        """Scan log text for known error patterns."""
        for pattern, error_type in _LOG_PATTERNS:
            if pattern.search(content):
                return ParsedError(
                    error_type=error_type,
                    message=content[:200],
                    retriable=error_type in _RETRIABLE,
                )
        return ParsedError(error_type=ErrorType.UNKNOWN, message=content[:200], retriable=False)

    # ── Retriability ────────────────────────────────────────────────

    @staticmethod
    def is_retriable(error_type: ErrorType) -> bool:
        """Check if the given error type is retriable."""
        return error_type in _RETRIABLE

    # ── Retriability ────────────────────────────────────────────────

    @staticmethod
    def is_retriable(error_type: ErrorType) -> bool:
        """Return True if the error type is worth retrying."""
        return error_type in _RETRIABLE

    # ── Backoff calculation ──────────────────────────────────────────

    @staticmethod
    def get_backoff_seconds(error_type: ErrorType, attempt: int) -> float:
        """Calculate backoff seconds with jitter for a given error type and attempt number.

        Attempt is 1-indexed. Uses the schedule for the error type, extending
        with exponential growth when attempts exceed the predefined list.
        Adds ±20% jitter to avoid thundering herd.
        """
        schedule = _BACKOFF_SCHEDULES.get(error_type)
        if not schedule:
            return 0.0

        if attempt <= len(schedule):
            base = float(schedule[attempt - 1])
        else:
            # Exponential extension beyond the defined schedule
            base = float(schedule[-1]) * (2 ** (attempt - len(schedule)))

        jitter = base * 0.2
        return max(0.0, base + random.uniform(-jitter, jitter))
