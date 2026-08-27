"""Session monitor for OpenCode session polling and completion detection.

Polls /session/status every 2 seconds, detects completion via 3 layers,
and flags stuck sessions (busy >15min with no tool calls for 5min).
"""

import asyncio
import structlog
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine

import httpx

logger = structlog.get_logger(__name__)

POLL_INTERVAL_SECONDS = 2.0
DEFAULT_TIMEOUT_SECONDS = 600.0  # 10 minutes
COMPLETION_IDLE_MINUTES = 2
STUCK_BUSY_MINUTES = 15
STUCK_NO_TOOL_MINUTES = 5
COMPLETION_MARKER = "<promise>DONE</promise>"

OnStateChangeCallback = Callable[[str, str], Coroutine[Any, Any, None] | None]


class SessionState(str, Enum):
    RUNNING = "running"
    IDLE = "idle"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"
    COMPLETED = "completed"
    STUCK = "stuck"


@dataclass
class SessionInfo:
    session_id: str
    state: SessionState = SessionState.UNKNOWN
    last_activity: float = field(default_factory=time.time)
    last_tool_call: float | None = None
    message_count: int = 0
    error_message: str | None = None
    raw_status: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResult:
    completed: bool
    layer: int | None = None
    reason: str = ""


class SessionMonitor:
    """Polls OpenCode session status and detects completion/stuck conditions."""

    def __init__(
        self,
        opencode_base_url: str = "http://localhost:5655",
        poll_interval: float = POLL_INTERVAL_SECONDS,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        idle_minutes: float = COMPLETION_IDLE_MINUTES,
        stuck_busy_minutes: float = STUCK_BUSY_MINUTES,
        stuck_no_tool_minutes: float = STUCK_NO_TOOL_MINUTES,
        http_timeout: float = 5.0,
    ) -> None:
        self._base_url = opencode_base_url.rstrip("/")
        self._poll_interval = poll_interval
        self._timeout_seconds = timeout_seconds
        self._idle_minutes = idle_minutes
        self._stuck_busy_minutes = stuck_busy_minutes
        self._stuck_no_tool_minutes = stuck_no_tool_minutes
        self._http_timeout = http_timeout
        self._on_state_change: OnStateChangeCallback | None = None
        self._sessions: dict[str, SessionInfo] = {}
        self._monitoring = False

    def set_on_state_change(self, callback: OnStateChangeCallback | None) -> None:
        self._on_state_change = callback

    def get_session_info(self, session_id: str) -> SessionInfo | None:
        return self._sessions.get(session_id)

    async def _fetch_status(self, session_id: str) -> dict[str, Any] | None:
        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                resp = await client.get(f"{self._base_url}/session/status", params={"session_id": session_id})
                if resp.status_code < 300:
                    return resp.json()
                logger.warning("session_status_http_error", extra={"session_id": session_id, "status": resp.status_code})
                return None
        except httpx.TimeoutException:
            logger.warning("session_status_timeout", extra={"session_id": session_id})
            return None
        except Exception as exc:
            logger.warning("session_status_error", extra={"session_id": session_id, "error": str(exc)})
            return None

    def _determine_state(self, raw_status: dict[str, Any]) -> SessionState:
        status_str = str(raw_status.get("status", "")).lower()
        if "running" in status_str or "busy" in status_str or "active" in status_str:
            return SessionState.RUNNING
        if "idle" in status_str or "waiting" in status_str:
            return SessionState.IDLE
        if "error" in status_str or "failed" in status_str:
            return SessionState.ERROR
        if "rate_limit" in status_str or "throttl" in status_str:
            return SessionState.RATE_LIMITED
        return SessionState.UNKNOWN

    def _detect_completion_layer1(self, raw_status: dict[str, Any]) -> CompletionResult:
        exit_code = raw_status.get("exit_code")
        if exit_code is not None and exit_code == 0:
            return CompletionResult(completed=True, layer=1, reason="process exit code 0")
        return CompletionResult(completed=False)

    def _detect_completion_layer2(self, session: SessionInfo) -> CompletionResult:
        if session.state == SessionState.IDLE:
            idle_duration = time.time() - session.last_activity
            idle_threshold = self._idle_minutes * 60
            if idle_duration >= idle_threshold:
                return CompletionResult(
                    completed=True,
                    layer=2,
                    reason=f"idle for {idle_duration:.0f}s (threshold: {idle_threshold:.0f}s)",
                )
        return CompletionResult(completed=False)

    def _detect_completion_layer3(self, session: SessionInfo, start_time: float) -> CompletionResult:
        elapsed = time.time() - start_time
        if elapsed >= self._timeout_seconds:
            return CompletionResult(
                completed=True,
                layer=3,
                reason=f"timeout after {elapsed:.0f}s (limit: {self._timeout_seconds:.0f}s)",
            )
        return CompletionResult(completed=False)

    def _check_completion_marker(self, raw_status: dict[str, Any]) -> bool:
        messages = raw_status.get("messages", [])
        for msg in messages:
            content = str(msg.get("content", ""))
            if COMPLETION_MARKER in content:
                return True
        return False

    def detect_stuck_session(self, session: SessionInfo) -> bool:
        if session.state != SessionState.RUNNING:
            return False

        busy_duration = time.time() - session.last_activity
        busy_threshold = self._stuck_busy_minutes * 60
        if busy_duration < busy_threshold:
            return False

        if session.last_tool_call is not None:
            tool_silence = time.time() - session.last_tool_call
            tool_threshold = self._stuck_no_tool_minutes * 60
            if tool_silence < tool_threshold:
                return False

        return True

    def _check_rate_limit(self, raw_status: dict[str, Any]) -> bool:
        return raw_status.get("rate_limited", False) or raw_status.get("rate_limit_exceeded", False)

    async def _notify_state_change(self, old_state: str, new_state: str, session_id: str) -> None:
        if self._on_state_change is not None:
            try:
                await self._on_state_change(old_state, new_state)
            except Exception as exc:
                logger.error("on_state_change_error", extra={"error": str(exc), "session_id": session_id})

    async def monitor_session(
        self,
        session_id: str,
        timeout: float | None = None,
    ) -> CompletionResult:
        effective_timeout = timeout or self._timeout_seconds
        start_time = time.time()
        session = SessionInfo(session_id=session_id)
        self._sessions[session_id] = session

        logger.info("monitor_start", extra={"session_id": session_id, "timeout": effective_timeout})

        while True:
            elapsed = time.time() - start_time
            if elapsed >= effective_timeout:
                result = CompletionResult(completed=True, layer=3, reason="monitor timeout")
                logger.info("monitor_timeout", extra={"session_id": session_id, "elapsed": elapsed})
                return result

            raw_status = await self._fetch_status(session_id)
            if raw_status is None:
                await asyncio.sleep(self._poll_interval)
                continue

            session.raw_status = raw_status

            if self._check_completion_marker(raw_status):
                return CompletionResult(completed=True, layer=2, reason="completion marker found")

            if self._check_rate_limit(raw_status):
                new_state = SessionState.RATE_LIMITED
                if session.state != new_state:
                    old_state = session.state.value
                    session.state = new_state
                    session.error_message = "rate limited"
                    await self._notify_state_change(old_state, new_state.value, session_id)
                return CompletionResult(
                    completed=True,
                    layer=2,
                    reason="rate limited",
                )

            new_state = self._determine_state(raw_status)
            if session.state != new_state:
                old_state = session.state.value
                session.state = new_state
                session.last_activity = time.time()
                await self._notify_state_change(old_state, new_state.value, session_id)

            completion = self._detect_completion_layer1(raw_status)
            if completion.completed:
                return completion

            completion = self._detect_completion_layer2(session)
            if completion.completed:
                return completion

            completion = self._detect_completion_layer3(session, start_time)
            if completion.completed:
                return completion

            if self.detect_stuck_session(session):
                session.state = SessionState.STUCK
                logger.warning("session_stuck", extra={"session_id": session_id})
                return CompletionResult(completed=True, layer=2, reason="stuck: busy >15min no tool calls")

            await asyncio.sleep(self._poll_interval)

    async def fetch_messages(self, session_id: str) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                resp = await client.get(f"{self._base_url}/message/list", params={"session_id": session_id})
                if resp.status_code < 300:
                    return resp.json().get("messages", [])
                return []
        except Exception:
            return []

    def clear_sessions(self) -> None:
        self._sessions.clear()
