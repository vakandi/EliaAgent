"""Tests for session_monitor.py — mocked HTTP + unit tests."""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.session_monitor import (
    CompletionResult,
    SessionInfo,
    SessionMonitor,
    SessionState,
)


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def monitor() -> SessionMonitor:
    return SessionMonitor(
        opencode_base_url="http://localhost:9999",
        poll_interval=0.05,
        timeout_seconds=2.0,
        idle_minutes=0.01,
        stuck_busy_minutes=0.01,
        stuck_no_tool_minutes=0.01,
        http_timeout=1.0,
    )


@pytest.fixture
def session_id() -> str:
    return "test-session-001"


# ── _determine_state ─────────────────────────────────────────────────────


class TestDetermineState:
    def test_running(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "running"}) == SessionState.RUNNING

    def test_busy(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "busy"}) == SessionState.RUNNING

    def test_active(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "active"}) == SessionState.RUNNING

    def test_idle(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "idle"}) == SessionState.IDLE

    def test_waiting(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "waiting"}) == SessionState.IDLE

    def test_error(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "error"}) == SessionState.ERROR

    def test_failed(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "failed"}) == SessionState.ERROR

    def test_rate_limited(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "rate_limited"}) == SessionState.RATE_LIMITED

    def test_throttled(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "throttled"}) == SessionState.RATE_LIMITED

    def test_empty(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({}) == SessionState.UNKNOWN

    def test_unknown_value(self, monitor: SessionMonitor) -> None:
        assert monitor._determine_state({"status": "weird"}) == SessionState.UNKNOWN


# ── _detect_completion_layer1 (exit code) ────────────────────────────────


class TestCompletionLayer1:
    def test_exit_code_zero(self, monitor: SessionMonitor) -> None:
        r = monitor._detect_completion_layer1({"exit_code": 0})
        assert r.completed is True
        assert r.layer == 1

    def test_exit_code_nonzero(self, monitor: SessionMonitor) -> None:
        r = monitor._detect_completion_layer1({"exit_code": 1})
        assert r.completed is False

    def test_no_exit_code(self, monitor: SessionMonitor) -> None:
        r = monitor._detect_completion_layer1({})
        assert r.completed is False


# ── _detect_completion_layer2 (idle quiet) ───────────────────────────────


class TestCompletionLayer2:
    def test_idle_long_enough(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.IDLE)
        session.last_activity = time.time() - 999
        r = monitor._detect_completion_layer2(session)
        assert r.completed is True
        assert r.layer == 2

    def test_idle_not_long_enough(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.IDLE)
        session.last_activity = time.time() - 0.1
        r = monitor._detect_completion_layer2(session)
        assert r.completed is False

    def test_running_not_completed(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.RUNNING)
        r = monitor._detect_completion_layer2(session)
        assert r.completed is False


# ── _detect_completion_layer3 (timeout) ──────────────────────────────────


class TestCompletionLayer3:
    def test_timeout_reached(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x")
        r = monitor._detect_completion_layer3(session, start_time=time.time() - 999)
        assert r.completed is True
        assert r.layer == 3

    def test_not_yet_timeout(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x")
        r = monitor._detect_completion_layer3(session, start_time=time.time())
        assert r.completed is False


# ── _check_completion_marker ─────────────────────────────────────────────


class TestCompletionMarker:
    def test_marker_found(self, monitor: SessionMonitor) -> None:
        assert monitor._check_completion_marker({"messages": [{"content": "<promise>DONE</promise>"}]}) is True

    def test_marker_not_found(self, monitor: SessionMonitor) -> None:
        assert monitor._check_completion_marker({"messages": [{"content": "hello"}]}) is False

    def test_empty_messages(self, monitor: SessionMonitor) -> None:
        assert monitor._check_completion_marker({"messages": []}) is False

    def test_no_messages_key(self, monitor: SessionMonitor) -> None:
        assert monitor._check_completion_marker({}) is False


# ── detect_stuck_session ─────────────────────────────────────────────────


class TestDetectStuck:
    def test_stuck_running_long_no_tool(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.RUNNING)
        session.last_activity = time.time() - 999
        session.last_tool_call = time.time() - 999
        assert monitor.detect_stuck_session(session) is True

    def test_not_stuck_too_short(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.RUNNING)
        session.last_activity = time.time() - 0.1
        session.last_tool_call = time.time() - 0.1
        assert monitor.detect_stuck_session(session) is False

    def test_not_stuck_recent_tool(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.RUNNING)
        session.last_activity = time.time() - 999
        session.last_tool_call = time.time() - 0.1
        assert monitor.detect_stuck_session(session) is False

    def test_not_stuck_idle(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.IDLE)
        session.last_activity = time.time() - 999
        assert monitor.detect_stuck_session(session) is False

    def test_not_stuck_no_tool_call(self, monitor: SessionMonitor) -> None:
        session = SessionInfo(session_id="x", state=SessionState.RUNNING)
        session.last_activity = time.time() - 999
        session.last_tool_call = None
        assert monitor.detect_stuck_session(session) is True


# ── _check_rate_limit ────────────────────────────────────────────────────


class TestCheckRateLimit:
    def test_rate_limited_flag(self, monitor: SessionMonitor) -> None:
        assert monitor._check_rate_limit({"rate_limited": True}) is True

    def test_rate_limit_exceeded(self, monitor: SessionMonitor) -> None:
        assert monitor._check_rate_limit({"rate_limit_exceeded": True}) is True

    def test_not_limited(self, monitor: SessionMonitor) -> None:
        assert monitor._check_rate_limit({}) is False


# ── monitor_session integration ──────────────────────────────────────────


class TestMonitorSession:
    @pytest.mark.asyncio
    async def test_exit_code_zero_immediate(self, monitor: SessionMonitor, session_id: str) -> None:
        async def exit_zero(*args, **kwargs):
            return {"status": "idle", "exit_code": 0}

        monitor._fetch_status = exit_zero
        result = await monitor.monitor_session(session_id)
        assert result.completed is True
        assert result.layer == 1
        assert "exit code" in result.reason

    @pytest.mark.asyncio
    async def test_timeout(self, monitor: SessionMonitor, session_id: str) -> None:
        monitor._timeout_seconds = 0.1
        monitor._poll_interval = 0.05

        async def always_running(*args, **kwargs):
            return {"status": "running"}

        monitor._fetch_status = always_running
        result = await monitor.monitor_session(session_id)
        assert result.completed is True
        assert result.layer == 3

    @pytest.mark.asyncio
    async def test_api_error_returns_error(self, monitor: SessionMonitor, session_id: str) -> None:
        async def always_timeout(*args, **kwargs):
            return None

        monitor._fetch_status = always_timeout
        monitor._timeout_seconds = 0.15
        monitor._poll_interval = 0.05
        result = await monitor.monitor_session(session_id)
        assert result.completed is True
        assert result.layer == 3

    @pytest.mark.asyncio
    async def test_completion_marker(self, monitor: SessionMonitor, session_id: str) -> None:
        call_count = 0

        async def marker_status(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return {"status": "running", "messages": [{"content": "done <promise>DONE</promise>"}]}
            return {"status": "running"}

        monitor._fetch_status = marker_status
        result = await monitor.monitor_session(session_id)
        assert result.completed is True
        assert "marker" in result.reason

    @pytest.mark.asyncio
    async def test_rate_limit_detected(self, monitor: SessionMonitor, session_id: str) -> None:
        monitor._timeout_seconds = 30.0
        monitor._poll_interval = 0.01
        call_count = 0

        async def rate_limit_status(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return {"status": "running", "rate_limited": True}
            return {"status": "running"}

        monitor._fetch_status = rate_limit_status
        result = await monitor.monitor_session(session_id, timeout=30.0)
        assert result.completed is True
        assert "rate" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_state_change_callback(self, monitor: SessionMonitor, session_id: str) -> None:
        transitions: list[tuple[str, str]] = []

        async def on_change(old: str, new: str) -> None:
            transitions.append((old, new))

        monitor.set_on_state_change(on_change)

        call_count = 0

        async def transitioning_status(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return {"status": "running"}
            return {"status": "running"}

        monitor._fetch_status = transitioning_status
        result = await monitor.monitor_session(session_id, timeout=0.3)
        assert len(transitions) > 0
        assert transitions[0][0] == "unknown"
        assert transitions[0][1] == "running"

    @pytest.mark.asyncio
    async def test_stuck_detection(self, monitor: SessionMonitor, session_id: str) -> None:
        monitor._timeout_seconds = 30.0
        monitor._stuck_busy_minutes = 0.001
        monitor._stuck_no_tool_minutes = 0.001
        monitor._poll_interval = 0.01

        async def always_running(*args, **kwargs):
            return {"status": "running"}

        monitor._fetch_status = always_running

        result = await monitor.monitor_session(session_id, timeout=30.0)
        assert result.completed is True
        assert "stuck" in result.reason.lower()


# ── SessionInfo ──────────────────────────────────────────────────────────


class TestSessionInfo:
    def test_defaults(self) -> None:
        info = SessionInfo(session_id="x")
        assert info.state == SessionState.UNKNOWN
        assert info.message_count == 0
        assert info.raw_status == {}

    def test_custom(self) -> None:
        info = SessionInfo(session_id="y", state=SessionState.RUNNING, message_count=5)
        assert info.state == SessionState.RUNNING
        assert info.message_count == 5


# ── CompletionResult ─────────────────────────────────────────────────────


class TestCompletionResult:
    def test_completed(self) -> None:
        r = CompletionResult(completed=True, layer=1, reason="exit code 0")
        assert r.completed is True
        assert r.layer == 1

    def test_not_completed(self) -> None:
        r = CompletionResult(completed=False)
        assert r.completed is False
        assert r.layer is None
