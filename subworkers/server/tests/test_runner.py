"""Unit tests for SubworkerRunner — mock OpenCodeClient (HTTP)."""
from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config.models import IntervalSchedule, ScheduleType, SubworkerConfig
from app.services.runner import (
    BACKOFF_MAX_SECONDS,
    BACKOFF_MIN_SECONDS,
    COMPLETION_MARKER,
    EXIT_CRASH,
    EXIT_TIMEOUT,
    MIN_OUTPUT_LINES,
    SubworkerRunner,
    RunPhase,
    RunAttempt,
    RunResult,
    SESSION_ID_PATTERN,
)


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "PROMPT.md").write_text("Do something useful\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\n")
    return ws


@pytest.fixture
def subworker_config(tmp_workspace: Path) -> SubworkerConfig:
    return SubworkerConfig(
        name="test-worker",
        enabled=True,
        schedule=IntervalSchedule(type=ScheduleType.INTERVAL, hours=[9], minute=0),
        workspace=str(tmp_workspace),
        agent_id="test-agent",
        model="test-model",
        max_retries=3,
        timeout_minutes=1,
    )


@pytest.fixture
def runner(subworker_config: SubworkerConfig, tmp_workspace: Path) -> SubworkerRunner:
    return SubworkerRunner(
        config=subworker_config,
        log_dir=tmp_workspace / "logs",
    )


def _assistant_text(msgs: list[dict[str, Any]]) -> str:
    for msg in reversed(msgs):
        info = msg.get("info", {})
        if info.get("role") != "assistant":
            continue
        parts = msg.get("parts", [])
        texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
        if texts:
            return "\n".join(texts)
    return ""


def _mock_messages(text: str) -> list[dict[str, Any]]:
    return [
        {"info": {"role": "user", "id": "m1"}, "parts": [{"type": "text", "text": "prompt"}]},
        {"info": {"role": "assistant", "id": "m2", "finish": "stop"}, "parts": [{"type": "text", "text": text}]},
    ]


_successful_text = "Working on task...\nUsed codegraph_explore\nRead file\nWrote output\nVerified\n<promise>DONE</promise>"


def _patch_client(mock_client: AsyncMock):
    """Context manager that patches OpenCodeClient with extract_assistant_text."""
    from contextlib import contextmanager

    @contextmanager
    def _patch():
        with patch("app.services.runner.OpenCodeClient", return_value=mock_client) as MockCls:
            MockCls.extract_assistant_text = staticmethod(_assistant_text)
            yield MockCls
    return _patch()


def _build_mock_client(
    *,
    session_id: str = "ses_test123abc",
    messages: list[dict[str, Any]] | None = None,
    create_side_effect: Exception | None = None,
    send_side_effect: Exception | None = None,
    wait_side_effect: Exception | None = None,
) -> AsyncMock:
    if messages is None:
        messages = _mock_messages(_successful_text)
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.extract_assistant_text = staticmethod(_assistant_text)
    if create_side_effect:
        client.create_session = AsyncMock(side_effect=create_side_effect)
    else:
        client.create_session = AsyncMock(return_value={"id": session_id, "agent": "test-agent"})
    if send_side_effect:
        client.send_message = AsyncMock(side_effect=send_side_effect)
    else:
        client.send_message = AsyncMock(return_value={})
    if wait_side_effect:
        client.wait_for_response = AsyncMock(side_effect=wait_side_effect)
    else:
        client.wait_for_response = AsyncMock(return_value={"type": "idle"})
    client.list_messages = AsyncMock(return_value=messages)
    return client


# ── Test: read prompt ──────────────────────────────────────────────────

class TestReadPrompt:
    def test_short_prompt_when_agent_id(self, runner: SubworkerRunner) -> None:
        prompt = runner._read_prompt()
        assert "test-worker" in prompt
        assert "DONE" in prompt
        assert "Do something useful" not in prompt

    def test_reads_prompt_file_when_no_agent(self, subworker_config: SubworkerConfig) -> None:
        subworker_config.agent_id = None
        runner = SubworkerRunner(config=subworker_config)
        prompt = runner._read_prompt()
        assert "Do something useful" in prompt

    def test_fallback_when_missing(self, subworker_config: SubworkerConfig, tmp_path: Path) -> None:
        subworker_config.workspace = str(tmp_path / "nonexistent")
        runner = SubworkerRunner(config=subworker_config)
        prompt = runner._read_prompt()
        assert "test-worker" in prompt


# ── Test: session ID extraction ─────────────────────────────────────────

class TestExtractSessionId:
    def test_extracts_session_id(self, runner: SubworkerRunner) -> None:
        output = "Created session ses_abc123xyz working..."
        assert runner._extract_session_id(output) == "ses_abc123xyz"

    def test_extracts_last_session_id(self, runner: SubworkerRunner) -> None:
        output = "ses_old111 then ses_new222"
        assert runner._extract_session_id(output) == "ses_new222"

    def test_returns_none_when_no_match(self, runner: SubworkerRunner) -> None:
        assert runner._extract_session_id("no session here") is None

    def test_returns_none_on_empty(self, runner: SubworkerRunner) -> None:
        assert runner._extract_session_id("") is None

    def test_session_id_pattern_regex(self) -> None:
        assert SESSION_ID_PATTERN.search("ses_abc123xyz") is not None
        assert SESSION_ID_PATTERN.search("ses_ABC123def456") is not None
        assert SESSION_ID_PATTERN.search("no_id_here") is None


# ── Test: validation ───────────────────────────────────────────────────

class TestValidateRun:
    def test_valid_with_marker(self, runner: SubworkerRunner) -> None:
        attempt = RunAttempt(attempt_number=1, exit_code=0,
                             stdout="line1\nline2\nline3\nline4\nline5\n<promise>DONE</promise>\n")
        result = runner._validate_run(attempt)
        assert result["valid"] is True
        assert result["checks"]["exit_code"] is True
        assert result["checks"]["completion_marker"] is True

    def test_valid_with_min_lines_only(self, runner: SubworkerRunner) -> None:
        attempt = RunAttempt(attempt_number=1, exit_code=0,
                             stdout="line1\nline2\nline3\nline4\nline5\n")
        result = runner._validate_run(attempt)
        assert result["valid"] is True
        assert result["checks"]["min_lines"] is True
        assert result["checks"]["completion_marker"] is False

    def test_invalid_no_output(self, runner: SubworkerRunner) -> None:
        attempt = RunAttempt(attempt_number=1, exit_code=0, stdout="")
        result = runner._validate_run(attempt)
        assert result["valid"] is False
        assert result["checks"]["min_lines"] is False

    def test_invalid_exit_code(self, runner: SubworkerRunner) -> None:
        attempt = RunAttempt(attempt_number=1, exit_code=1,
                             stdout="line1\nline2\nline3\nline4\nline5\n")
        result = runner._validate_run(attempt)
        assert result["valid"] is False
        assert result["checks"]["exit_code"] is False

    def test_invalid_exit_zero_but_no_output(self, runner: SubworkerRunner) -> None:
        attempt = RunAttempt(attempt_number=1, exit_code=0, stdout="")
        result = runner._validate_run(attempt)
        assert result["valid"] is False


# ── Test: backoff range ────────────────────────────────────────────────

class TestBackoff:
    def test_backoff_in_range(self) -> None:
        for _ in range(50):
            delay = random.uniform(BACKOFF_MIN_SECONDS, BACKOFF_MAX_SECONDS)
            assert BACKOFF_MIN_SECONDS <= delay <= BACKOFF_MAX_SECONDS

    def test_backoff_constants(self) -> None:
        assert BACKOFF_MIN_SECONDS > 0
        assert BACKOFF_MAX_SECONDS > BACKOFF_MIN_SECONDS


# ── Test: run_subworker success path ────────────────────────────────────

class TestRunSubworkerSuccess:
    @pytest.mark.asyncio
    async def test_successful_run(self, runner: SubworkerRunner) -> None:
        mock_client = _build_mock_client()
        with _patch_client(mock_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.5, 1.0, 1.5]
                result = await runner.run_subworker()

        assert result.success is True
        assert result.final_phase == RunPhase.COMPLETED
        assert result.total_attempts == 1
        assert result.session_id == "ses_test123abc"

    @pytest.mark.asyncio
    async def test_session_id_from_create(self, runner: SubworkerRunner) -> None:
        mock_client = _build_mock_client(session_id="ses_fresh_new_id")
        with _patch_client(mock_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.5, 1.0, 1.5]
                result = await runner.run_subworker()

        assert result.session_id == "ses_fresh_new_id"
        mock_client.create_session.assert_awaited_once()
        args, kwargs = mock_client.send_message.call_args
        assert args[0] == "ses_fresh_new_id"


# ── Test: run_subworker retry path ──────────────────────────────────────

class TestRunSubworkerRetry:
    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self, runner: SubworkerRunner) -> None:
        from app.utils.exceptions import OpenCodeConnectionError
        call_count = 0
        good_client = _build_mock_client()
        bad_client = _build_mock_client(send_side_effect=OpenCodeConnectionError("refused"))

        clients = [bad_client, good_client]

        def fake_ctx(*a: Any, **kw: Any) -> AsyncMock:
            nonlocal call_count
            c = clients[min(call_count, 1)]
            call_count += 1
            return c

        with patch("app.services.runner.OpenCodeClient") as MockClient:
            MockClient.side_effect = fake_ctx
            MockClient.extract_assistant_text = staticmethod(_assistant_text)
            with patch("app.services.runner.asyncio.sleep", new_callable=AsyncMock):
                with patch("app.services.runner.time") as mock_time:
                    mock_time.time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
                    result = await runner.run_subworker()

        assert result.success is True
        assert result.total_attempts == 2

    @pytest.mark.asyncio
    async def test_exhausts_retries(self, subworker_config: SubworkerConfig) -> None:
        from app.utils.exceptions import OpenCodeConnectionError
        subworker_config.max_retries = 1
        runner = SubworkerRunner(config=subworker_config)
        bad_client = _build_mock_client(send_side_effect=OpenCodeConnectionError("refused"))

        with _patch_client(bad_client):
            with patch("app.services.runner.asyncio.sleep", new_callable=AsyncMock):
                with patch("app.services.runner.time") as mock_time:
                    mock_time.time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
                    result = await runner.run_subworker()

        assert result.success is False
        assert result.total_attempts == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_non_retriable(self, runner: SubworkerRunner) -> None:
        from app.utils.exceptions import OpenCodeError
        bad_client = _build_mock_client(wait_side_effect=OpenCodeError("bad request", status_code=400))

        with _patch_client(bad_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.1, 0.2, 0.3]
                result = await runner.run_subworker()

        assert result.success is False
        assert result.total_attempts == 1


# ── Test: session recovery ─────────────────────────────────────────────

class TestSessionRecovery:
    @pytest.mark.asyncio
    async def test_session_id_reused_on_retry(self, runner: SubworkerRunner) -> None:
        from app.utils.exceptions import OpenCodeConnectionError
        call_count = 0

        fail_client = _build_mock_client(
            session_id="ses_first_session",
            messages=[{"info": {"role": "user"}, "parts": [{"type": "text", "text": "ok"}]}],
        )
        fail_client.send_message = AsyncMock(side_effect=OpenCodeConnectionError("refused"))
        ok_client = _build_mock_client(session_id="ses_first_session")

        clients = [fail_client, ok_client]

        def fake_ctx(*a: Any, **kw: Any) -> AsyncMock:
            nonlocal call_count
            c = clients[min(call_count, 1)]
            call_count += 1
            return c

        with patch("app.services.runner.OpenCodeClient") as MockClient:
            MockClient.side_effect = fake_ctx
            MockClient.extract_assistant_text = staticmethod(_assistant_text)
            with patch("app.services.runner.asyncio.sleep", new_callable=AsyncMock):
                with patch("app.services.runner.time") as mock_time:
                    mock_time.time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
                    result = await runner.run_subworker()

        assert result.session_id == "ses_first_session"
        assert result.total_attempts == 2


# ── Test: health check ─────────────────────────────────────────────────

class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_fails_when_unhealthy(self, runner: SubworkerRunner) -> None:
        runner._health_check = AsyncMock(return_value=False)
        result = await runner.run_subworker()
        assert result.success is False
        assert "health check failed" in result.error_message

    @pytest.mark.asyncio
    async def test_skips_when_no_health_check(self, runner: SubworkerRunner) -> None:
        mock_client = _build_mock_client()
        with _patch_client(mock_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.5, 1.0, 1.5]
                result = await runner.run_subworker()
        assert result.success is True


# ── Test: process error handling ────────────────────────────────────────

class TestProcessErrors:
    @pytest.mark.asyncio
    async def test_timeout_error(self, runner: SubworkerRunner) -> None:
        from app.utils.exceptions import OpenCodeTimeoutError
        bad_client = _build_mock_client(wait_side_effect=OpenCodeTimeoutError("timed out", status_code=408))

        with _patch_client(bad_client):
            with patch("app.services.runner.asyncio.sleep", new_callable=AsyncMock):
                with patch("app.services.runner.time") as mock_time:
                    mock_time.time.side_effect = [float(i) for i in range(20)]
                    result = await runner.run_subworker()

        assert result.success is False
        assert result.attempts[0].retriable is True

    @pytest.mark.asyncio
    async def test_generic_exception(self, runner: SubworkerRunner) -> None:
        bad_client = _build_mock_client(create_side_effect=RuntimeError("something broke"))

        with _patch_client(bad_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.1, 0.2, 0.3]
                result = await runner.run_subworker()

        assert result.success is False

    @pytest.mark.asyncio
    async def test_rate_limit_is_retriable(self, runner: SubworkerRunner) -> None:
        from app.utils.exceptions import RateLimitError
        bad_client = _build_mock_client(send_side_effect=RateLimitError("rate limited", status_code=429))

        with _patch_client(bad_client):
            with patch("app.services.runner.asyncio.sleep", new_callable=AsyncMock):
                with patch("app.services.runner.time") as mock_time:
                    mock_time.time.side_effect = [float(i) for i in range(20)]
                    result = await runner.run_subworker()

        assert result.success is False
        assert result.attempts[0].retriable is True


# ── Test: callbacks ─────────────────────────────────────────────────────

class TestCallbacks:
    @pytest.mark.asyncio
    async def test_phase_callback_called(self, runner: SubworkerRunner) -> None:
        phases_received: list[RunPhase] = []

        async def on_phase(phase: RunPhase, message: str) -> None:
            phases_received.append(phase)

        runner.on_phase_change(on_phase)
        mock_client = _build_mock_client()
        with _patch_client(mock_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.5, 1.0, 1.5]
                await runner.run_subworker()

        assert RunPhase.HEALTH_CHECK in phases_received
        assert RunPhase.INVOKE in phases_received

    @pytest.mark.asyncio
    async def test_retry_phase_emitted(self, subworker_config: SubworkerConfig) -> None:
        from app.utils.exceptions import OpenCodeConnectionError
        subworker_config.max_retries = 2
        runner = SubworkerRunner(config=subworker_config)
        phases_received: list[RunPhase] = []

        async def on_phase(phase: RunPhase, message: str) -> None:
            phases_received.append(phase)

        runner.on_phase_change(on_phase)

        call_count = 0
        bad_client = _build_mock_client(send_side_effect=OpenCodeConnectionError("refused"))
        good_client = _build_mock_client()
        clients = [bad_client, good_client]

        def fake_ctx(*a: Any, **kw: Any) -> AsyncMock:
            nonlocal call_count
            c = clients[min(call_count, 1)]
            call_count += 1
            return c

        with patch("app.services.runner.OpenCodeClient") as MockClient:
            MockClient.side_effect = fake_ctx
            MockClient.extract_assistant_text = staticmethod(_assistant_text)
            with patch("app.services.runner.asyncio.sleep", new_callable=AsyncMock):
                with patch("app.services.runner.time") as mock_time:
                    mock_time.time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
                    await runner.run_subworker()

        assert RunPhase.HEALTH_CHECK in phases_received
        assert RunPhase.INVOKE in phases_received
        assert RunPhase.RETRY in phases_received

    @pytest.mark.asyncio
    async def test_callback_error_does_not_crash(self, runner: SubworkerRunner) -> None:
        async def bad_callback(phase: RunPhase, message: str) -> None:
            raise RuntimeError("callback exploded")

        runner.on_phase_change(bad_callback)
        mock_client = _build_mock_client()
        with _patch_client(mock_client):
            with patch("app.services.runner.time") as mock_time:
                mock_time.time.side_effect = [0.0, 0.5, 1.0, 1.5]
                result = await runner.run_subworker()

        assert result.success is True


# ── Test: logging ──────────────────────────────────────────────────────

class TestLogging:
    def test_writes_log_file(self, runner: SubworkerRunner, tmp_workspace: Path) -> None:
        attempt = RunAttempt(attempt_number=1, exit_code=0, stdout="output\n" * 10,
                             stderr="", duration_seconds=5.0, session_id="ses_test123")
        result = RunResult(success=True, subworker_name="test-worker", total_attempts=1,
                           final_phase=RunPhase.COMPLETED, attempts=[attempt],
                           total_duration_seconds=5.0, session_id="ses_test123", stdout="output\n" * 10)
        runner._write_run_log(result)
        log_files = list((tmp_workspace / "logs").glob("test-worker_*.log"))
        assert len(log_files) == 1
        content = log_files[0].read_text()
        assert "test-worker" in content
        assert "Success: True" in content
        assert "ses_test123" in content

    def test_no_log_when_no_dir(self, subworker_config: SubworkerConfig) -> None:
        runner = SubworkerRunner(config=subworker_config, log_dir=None)
        result = RunResult(success=True, subworker_name="test")
        runner._write_run_log(result)


# ── Test: RunResult / RunAttempt dataclasses ────────────────────────────

class TestRunAttempt:
    def test_defaults(self) -> None:
        attempt = RunAttempt(attempt_number=1)
        assert attempt.exit_code is None
        assert attempt.stdout == ""
        assert attempt.stderr == ""
        assert attempt.retriable is False
        assert attempt.error_type is None


class TestRunResult:
    def test_defaults(self) -> None:
        result = RunResult(success=False, subworker_name="test")
        assert result.total_attempts == 0
        assert result.final_phase == RunPhase.FAILED
        assert result.attempts == []
        assert result.session_id is None
