"""Unit tests for ErrorParser (TASK-203)."""
from __future__ import annotations

import pytest

from app.services.error_parser import (
    ErrorParser,
    ErrorType,
    ParsedError,
)


# ── ErrorType enum ──────────────────────────────────────────────────────


class TestErrorType:
    def test_nine_types(self) -> None:
        assert len(ErrorType) == 9

    def test_all_values_unique(self) -> None:
        values = [e.value for e in ErrorType]
        assert len(values) == len(set(values))

    def test_expected_members(self) -> None:
        expected = {
            "rate_limit",
            "auth_failure",
            "server_error",
            "timeout",
            "not_found",
            "model_unavailable",
            "sse_disconnect",
            "idle_timeout",
            "unknown",
        }
        assert {e.value for e in ErrorType} == expected


# ── ParsedError dataclass ───────────────────────────────────────────────


class TestParsedError:
    def test_frozen(self) -> None:
        e = ParsedError(error_type=ErrorType.TIMEOUT, message="boom")
        with pytest.raises(AttributeError):
            e.message = "nope"  # type: ignore[misc]

    def test_default_retriable(self) -> None:
        e = ParsedError(error_type=ErrorType.RATE_LIMIT, message="x")
        assert e.retriable is True

    def test_repr(self) -> None:
        e = ParsedError(error_type=ErrorType.AUTH_FAILURE, message="bad key")
        assert "auth_failure" in repr(e)


# ── parse_http_status ───────────────────────────────────────────────────


class TestParseHttpStatus:
    def test_429_rate_limit(self) -> None:
        r = ErrorParser.parse_http_status(429)
        assert r.error_type == ErrorType.RATE_LIMIT
        assert r.retriable is True

    def test_429_with_body(self) -> None:
        r = ErrorParser.parse_http_status(429, "slow down")
        assert "slow down" in r.message

    def test_401_auth_failure(self) -> None:
        r = ErrorParser.parse_http_status(401)
        assert r.error_type == ErrorType.AUTH_FAILURE
        assert r.retriable is False

    def test_403_auth_failure(self) -> None:
        r = ErrorParser.parse_http_status(403)
        assert r.error_type == ErrorType.AUTH_FAILURE

    def test_404_not_found(self) -> None:
        r = ErrorParser.parse_http_status(404)
        assert r.error_type == ErrorType.NOT_FOUND
        assert r.retriable is False

    def test_500_server_error(self) -> None:
        r = ErrorParser.parse_http_status(500)
        assert r.error_type == ErrorType.SERVER_ERROR
        assert r.retriable is True

    def test_502_server_error(self) -> None:
        r = ErrorParser.parse_http_status(502)
        assert r.error_type == ErrorType.SERVER_ERROR

    def test_503_server_error(self) -> None:
        r = ErrorParser.parse_http_status(503)
        assert r.error_type == ErrorType.SERVER_ERROR

    def test_599_server_error(self) -> None:
        r = ErrorParser.parse_http_status(599)
        assert r.error_type == ErrorType.SERVER_ERROR

    def test_unknown_status(self) -> None:
        r = ErrorParser.parse_http_status(418)
        assert r.error_type == ErrorType.UNKNOWN
        assert r.retriable is False

    def test_200_is_unknown(self) -> None:
        r = ErrorParser.parse_http_status(200)
        assert r.error_type == ErrorType.UNKNOWN

    def test_body_in_message(self) -> None:
        r = ErrorParser.parse_http_status(500, "internal error")
        assert "internal error" in r.message
        assert "500" in r.message


# ── parse_api_message ───────────────────────────────────────────────────


class TestParseApiMessage:
    def test_rate_limit_keyword(self) -> None:
        r = ErrorParser.parse_api_message("rate limit exceeded")
        assert r.error_type == ErrorType.RATE_LIMIT
        assert r.retriable is True

    def test_quota_exceeded(self) -> None:
        r = ErrorParser.parse_api_message("quota exceeded for this key")
        assert r.error_type == ErrorType.RATE_LIMIT

    def test_too_many_requests(self) -> None:
        r = ErrorParser.parse_api_message("Too Many Requests")
        assert r.error_type == ErrorType.RATE_LIMIT

    def test_unauthorized(self) -> None:
        r = ErrorParser.parse_api_message("unauthorized access")
        assert r.error_type == ErrorType.AUTH_FAILURE
        assert r.retriable is False

    def test_invalid_api_key(self) -> None:
        r = ErrorParser.parse_api_message("Invalid API key provided")
        assert r.error_type == ErrorType.AUTH_FAILURE

    def test_forbidden(self) -> None:
        r = ErrorParser.parse_api_message("forbidden: insufficient scope")
        assert r.error_type == ErrorType.AUTH_FAILURE

    def test_model_unavailable(self) -> None:
        r = ErrorParser.parse_api_message("model unavailable for this region")
        assert r.error_type == ErrorType.MODEL_UNAVAILABLE
        assert r.retriable is True

    def test_model_not_found(self) -> None:
        r = ErrorParser.parse_api_message("model not found")
        assert r.error_type == ErrorType.MODEL_UNAVAILABLE

    def test_overloaded(self) -> None:
        r = ErrorParser.parse_api_message("service overloaded")
        assert r.error_type == ErrorType.MODEL_UNAVAILABLE

    def test_upstream_timeout(self) -> None:
        r = ErrorParser.parse_api_message("upstream timeout")
        assert r.error_type == ErrorType.TIMEOUT
        assert r.retriable is True

    def test_gateway_timeout(self) -> None:
        r = ErrorParser.parse_api_message("gateway timeout")
        assert r.error_type == ErrorType.TIMEOUT

    def test_request_timeout(self) -> None:
        r = ErrorParser.parse_api_message("request timeout after 30s")
        assert r.error_type == ErrorType.TIMEOUT

    def test_unknown_message(self) -> None:
        r = ErrorParser.parse_api_message("something weird happened")
        assert r.error_type == ErrorType.UNKNOWN
        assert r.retriable is False

    def test_case_insensitive(self) -> None:
        r = ErrorParser.parse_api_message("RATE LIMIT EXCEEDED")
        assert r.error_type == ErrorType.RATE_LIMIT

    def test_preserves_original_message(self) -> None:
        r = ErrorParser.parse_api_message("rate limit hit")
        assert r.message == "rate limit hit"


# ── parse_exit_code ─────────────────────────────────────────────────────


class TestParseExitCode:
    def test_zero(self) -> None:
        r = ErrorParser.parse_exit_code(0)
        assert r.error_type == ErrorType.UNKNOWN
        assert r.retriable is False

    def test_124_timeout(self) -> None:
        r = ErrorParser.parse_exit_code(124)
        assert r.error_type == ErrorType.TIMEOUT
        assert r.retriable is True

    def test_137_killed(self) -> None:
        r = ErrorParser.parse_exit_code(137)
        assert r.error_type == ErrorType.TIMEOUT
        assert r.retriable is True

    def test_1_generic(self) -> None:
        r = ErrorParser.parse_exit_code(1)
        assert r.error_type == ErrorType.UNKNOWN
        assert r.retriable is False

    def test_130_sigint(self) -> None:
        r = ErrorParser.parse_exit_code(130)
        assert r.error_type == ErrorType.UNKNOWN

    def test_large_code(self) -> None:
        r = ErrorParser.parse_exit_code(255)
        assert r.error_type == ErrorType.UNKNOWN

    def test_negative_code(self) -> None:
        r = ErrorParser.parse_exit_code(-1)
        assert r.error_type == ErrorType.UNKNOWN


# ── parse_log_content ───────────────────────────────────────────────────


class TestParseLogContent:
    def test_no_events_received(self) -> None:
        r = ErrorParser.parse_log_content("ERROR: no events received for 60s")
        assert r.error_type == ErrorType.IDLE_TIMEOUT
        assert r.retriable is True

    def test_idle_timeout(self) -> None:
        r = ErrorParser.parse_log_content("session idle timeout triggered")
        assert r.error_type == ErrorType.IDLE_TIMEOUT

    def test_sse_disconnect(self) -> None:
        r = ErrorParser.parse_log_content("sse disconnect from upstream")
        assert r.error_type == ErrorType.SSE_DISCONNECT
        assert r.retriable is True

    def test_connection_reset(self) -> None:
        r = ErrorParser.parse_log_content("connection reset by peer")
        assert r.error_type == ErrorType.SSE_DISCONNECT

    def test_upstream_timed_out(self) -> None:
        r = ErrorParser.parse_log_content("upstream timed out (110: Connection timed out)")
        assert r.error_type == ErrorType.TIMEOUT
        assert r.retriable is True

    def test_read_timed_out(self) -> None:
        r = ErrorParser.parse_log_content("read timed out")
        assert r.error_type == ErrorType.TIMEOUT

    def test_rate_limit_in_log(self) -> None:
        r = ErrorParser.parse_log_content("ERROR rate limit exceeded, retry later")
        assert r.error_type == ErrorType.RATE_LIMIT

    def test_model_unavailable_in_log(self) -> None:
        r = ErrorParser.parse_log_content("model unavailable due to capacity")
        assert r.error_type == ErrorType.MODEL_UNAVAILABLE

    def test_overloaded_in_log(self) -> None:
        r = ErrorParser.parse_log_content("service overloaded")
        assert r.error_type == ErrorType.MODEL_UNAVAILABLE

    def test_unknown_log(self) -> None:
        r = ErrorParser.parse_log_content("INFO everything is fine")
        assert r.error_type == ErrorType.UNKNOWN
        assert r.retriable is False

    def test_empty_log(self) -> None:
        r = ErrorParser.parse_log_content("")
        assert r.error_type == ErrorType.UNKNOWN

    def test_message_truncated_to_200(self) -> None:
        long_msg = "x" * 500
        r = ErrorParser.parse_log_content(long_msg)
        assert len(r.message) <= 200


# ── is_retriable ────────────────────────────────────────────────────────


class TestIsRetriable:
    def test_retriable_types(self) -> None:
        for t in (ErrorType.RATE_LIMIT, ErrorType.SERVER_ERROR, ErrorType.TIMEOUT, ErrorType.MODEL_UNAVAILABLE):
            assert ErrorParser.is_retriable(t) is True

    def test_non_retriable_types(self) -> None:
        for t in (ErrorType.AUTH_FAILURE, ErrorType.NOT_FOUND, ErrorType.UNKNOWN):
            assert ErrorParser.is_retriable(t) is False


# ── get_backoff_seconds ─────────────────────────────────────────────────


class TestGetBackoffSeconds:
    def test_rate_limit_schedule(self) -> None:
        b1 = ErrorParser.get_backoff_seconds(ErrorType.RATE_LIMIT, 1)
        b2 = ErrorParser.get_backoff_seconds(ErrorType.RATE_LIMIT, 2)
        b3 = ErrorParser.get_backoff_seconds(ErrorType.RATE_LIMIT, 3)
        assert b1 >= 240.0  # 300 ± 20%
        assert b2 >= 480.0  # 600 ± 20%
        assert b3 >= 1440.0  # 1800 ± 20%

    def test_server_error_exponential(self) -> None:
        b1 = ErrorParser.get_backoff_seconds(ErrorType.SERVER_ERROR, 1)
        b2 = ErrorParser.get_backoff_seconds(ErrorType.SERVER_ERROR, 2)
        b3 = ErrorParser.get_backoff_seconds(ErrorType.SERVER_ERROR, 3)
        assert b1 >= 1.6  # 2 ± 20%
        assert b2 >= 3.2  # 4 ± 20%
        assert b3 >= 6.4  # 8 ± 20%

    def test_timeout_schedule(self) -> None:
        b1 = ErrorParser.get_backoff_seconds(ErrorType.TIMEOUT, 1)
        assert b1 >= 4.0  # 5 ± 20%

    def test_unknown_returns_zero(self) -> None:
        b = ErrorParser.get_backoff_seconds(ErrorType.UNKNOWN, 1)
        assert b == 0.0

    def test_auth_failure_returns_zero(self) -> None:
        b = ErrorParser.get_backoff_seconds(ErrorType.AUTH_FAILURE, 1)
        assert b == 0.0

    def test_attempt_zero(self) -> None:
        b = ErrorParser.get_backoff_seconds(ErrorType.SERVER_ERROR, 0)
        assert b >= 1.6  # attempt 0 → schedule[0] = 2

    def test_attempts_beyond_schedule_extend(self) -> None:
        b8 = ErrorParser.get_backoff_seconds(ErrorType.RATE_LIMIT, 8)
        assert b8 > 1800.0

    def test_jitter_within_bounds(self) -> None:
        """20 runs should stay within ±20% jitter range."""
        results = [ErrorParser.get_backoff_seconds(ErrorType.SERVER_ERROR, 1) for _ in range(20)]
        for r in results:
            assert 1.6 <= r <= 2.4
