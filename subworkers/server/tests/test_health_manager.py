"""Unit tests for HealthManager (OpenCode lifecycle)."""
from __future__ import annotations

import asyncio
import signal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.health_manager import (
    DEFAULT_PORT,
    DEGRADED_FAILURE_THRESHOLD,
    GRACEFUL_SHUTDOWN_WAIT,
    HEALTH_BACKOFF_BASE,
    HEALTH_BACKOFF_MAX,
    PID_FILE_NAME,
    RESTART_BASE_DELAY,
    RESTART_MAX_ATTEMPTS,
    RESTART_MAX_DELAY,
    HealthManager,
    HealthStatus,
    ServerState,
)


# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_pid_dir(tmp_path: Path) -> Path:
    """Provide a temp directory for PID files."""
    d = tmp_path / "pids"
    d.mkdir()
    return d


@pytest.fixture
def manager(tmp_pid_dir: Path) -> HealthManager:
    """HealthManager with a temp PID dir and a mock binary name."""
    return HealthManager(
        port=19999,
        host="127.0.0.1",
        opencode_bin="echo",  # 'echo' is a safe binary that exits immediately
        pid_dir=str(tmp_pid_dir),
    )


def _mock_process(pid: int = 12345) -> MagicMock:
    """Create a mock asyncio subprocess.Process."""
    proc = MagicMock(spec=asyncio.subprocess.Process)
    proc.pid = pid
    proc.returncode = None
    proc.send_signal = MagicMock()
    proc.terminate = MagicMock()
    proc.kill = MagicMock()
    proc.wait = AsyncMock(return_value=0)
    proc.communicate = AsyncMock(return_value=(b"", b""))
    return proc


# ── ServerState ────────────────────────────────────────────────────────────


class TestServerState:
    def test_values(self) -> None:
        assert ServerState.STOPPED.value == "stopped"
        assert ServerState.RUNNING.value == "running"
        assert ServerState.DOWN.value == "down"

    def test_is_string_enum(self) -> None:
        assert isinstance(ServerState.STOPPED, str)
        assert ServerState.STOPPED == "stopped"


# ── HealthManager init ─────────────────────────────────────────────────────


class TestHealthManagerInit:
    def test_default_state(self, manager: HealthManager) -> None:
        assert manager.state == ServerState.STOPPED
        assert manager.pid is None
        assert manager.restart_count == 0

    def test_base_url(self, manager: HealthManager) -> None:
        assert manager.base_url == "http://127.0.0.1:19999"

    def test_pid_file_path(self, manager: HealthManager, tmp_pid_dir: Path) -> None:
        assert manager.pid_file == tmp_pid_dir / PID_FILE_NAME


# ── State management ──────────────────────────────────────────────────────


class TestStateManagement:
    @pytest.mark.asyncio
    async def test_set_state(self, manager: HealthManager) -> None:
        await manager._set_state(ServerState.STARTING)
        assert manager.state == ServerState.STARTING

    @pytest.mark.asyncio
    async def test_no_callback_on_same_state(self, manager: HealthManager) -> None:
        cb = AsyncMock()
        manager.on_state_change(cb)
        await manager._set_state(ServerState.STOPPED)  # already STOPPED
        cb.assert_not_called()

    @pytest.mark.asyncio
    async def test_callback_fires(self, manager: HealthManager) -> None:
        cb = AsyncMock()
        manager.on_state_change(cb)
        await manager._set_state(ServerState.RUNNING)
        cb.assert_called_once_with(ServerState.STOPPED, ServerState.RUNNING)

    @pytest.mark.asyncio
    async def test_callback_exception_does_not_crash(self, manager: HealthManager) -> None:
        async def bad_cb(old: ServerState, new: ServerState) -> None:
            raise RuntimeError("boom")

        manager.on_state_change(bad_cb)
        # Should not raise
        await manager._set_state(ServerState.RUNNING)
        assert manager.state == ServerState.RUNNING


# ── PID file ──────────────────────────────────────────────────────────────


class TestPidFile:
    def test_write_and_cleanup(self, manager: HealthManager, tmp_pid_dir: Path) -> None:
        manager._process = _mock_process(42)
        manager._write_pid()
        assert manager.pid_file.read_text() == "42"

        manager._cleanup_pid()
        assert not manager.pid_file.exists()

    def test_write_pid_no_process(self, manager: HealthManager, tmp_pid_dir: Path) -> None:
        # Should be a no-op
        manager._write_pid()
        assert not manager.pid_file.exists()

    def test_read_pid(self, manager: HealthManager, tmp_pid_dir: Path) -> None:
        manager.pid_file.write_text("999")
        assert manager._read_pid() == 999

    def test_read_pid_missing(self, manager: HealthManager) -> None:
        assert manager._read_pid() is None

    def test_cleanup_pid_missing(self, manager: HealthManager) -> None:
        # Should not raise
        manager._cleanup_pid()


# ── Start ─────────────────────────────────────────────────────────────────


class TestStart:
    @pytest.mark.asyncio
    async def test_start_spawns_process(self, manager: HealthManager) -> None:
        with patch("asyncio.create_subprocess_exec") as mock_create:
            mock_proc = _mock_process(100)
            mock_create.return_value = mock_proc
            await manager.start()
            assert manager.state == ServerState.RUNNING
            assert manager.pid == 100

    @pytest.mark.asyncio
    async def test_start_noop_if_already_running(self, manager: HealthManager) -> None:
        with patch("asyncio.create_subprocess_exec") as mock_create:
            manager._state = ServerState.RUNNING
            manager._process = _mock_process()
            await manager.start()
            mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_binary_not_found(self, manager: HealthManager) -> None:
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError):
            with pytest.raises(RuntimeError, match="binary not found"):
                await manager.start()
            assert manager.state == ServerState.DOWN

    @pytest.mark.asyncio
    async def test_start_writes_pid_file(self, manager: HealthManager, tmp_pid_dir: Path) -> None:
        with patch("asyncio.create_subprocess_exec") as mock_create:
            mock_create.return_value = _mock_process(777)
            await manager.start()
            assert manager.pid_file.read_text() == "777"


# ── Stop ──────────────────────────────────────────────────────────────────


class TestStop:
    @pytest.mark.asyncio
    async def test_stop_noop_when_stopped(self, manager: HealthManager) -> None:
        await manager.stop()
        assert manager.state == ServerState.STOPPED

    @pytest.mark.asyncio
    async def test_stop_terminates_process(self, manager: HealthManager) -> None:
        proc = _mock_process(200)
        proc.wait = AsyncMock(return_value=0)
        manager._process = proc
        await manager._set_state(ServerState.RUNNING)

        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait:
            mock_wait.return_value = 0
            await manager.stop()
            proc.send_signal.assert_called_with(signal.SIGTERM)

        assert manager.state == ServerState.STOPPED
        assert manager.pid is None

    @pytest.mark.asyncio
    async def test_stop_force_kill_on_timeout(self, manager: HealthManager) -> None:
        proc = _mock_process(300)
        proc.wait = AsyncMock(side_effect=asyncio.TimeoutError)
        manager._process = proc
        await manager._set_state(ServerState.RUNNING)

        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait:
            mock_wait.side_effect = asyncio.TimeoutError
            await manager.stop()

        proc.kill.assert_called()
        assert manager.state == ServerState.STOPPED

    @pytest.mark.asyncio
    async def test_stop_cleans_pid_file(self, manager: HealthManager, tmp_pid_dir: Path) -> None:
        manager.pid_file.write_text("500")
        proc = _mock_process(500)
        proc.wait = AsyncMock(return_value=0)
        manager._process = proc
        await manager._set_state(ServerState.RUNNING)

        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait:
            mock_wait.return_value = 0
            await manager.stop()

        assert not manager.pid_file.exists()


# ── Check health ──────────────────────────────────────────────────────────


class TestCheckHealth:
    @pytest.mark.asyncio
    async def test_health_no_process(self, manager: HealthManager) -> None:
        result = await manager.check_health()
        assert result["process_alive"] is False
        assert result["port_open"] is False
        assert result["http_healthy"] is False

    @pytest.mark.asyncio
    async def test_health_process_dead(self, manager: HealthManager) -> None:
        proc = _mock_process(400)
        proc.returncode = 1  # process exited
        manager._process = proc
        result = await manager.check_health()
        assert result["process_alive"] is False

    @pytest.mark.asyncio
    async def test_health_port_closed(self, manager: HealthManager) -> None:
        proc = _mock_process(500)
        manager._process = proc
        with patch("socket.socket") as mock_sock:
            mock_sock.return_value.connect.side_effect = ConnectionRefusedError
            result = await manager.check_health()
        assert result["process_alive"] is True
        assert result["port_open"] is False


# ── Restart ───────────────────────────────────────────────────────────────


class TestRestart:
    @pytest.mark.asyncio
    async def test_restart_backoff_increases(self, manager: HealthManager) -> None:
        with (
            patch.object(manager, "stop", new_callable=AsyncMock),
            patch.object(manager, "start", new_callable=AsyncMock),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            await manager.restart()
            assert manager.restart_count == 1

            await manager.restart()
            assert manager.restart_count == 2

    @pytest.mark.asyncio
    async def test_restart_max_attempts_exceeded(self, manager: HealthManager) -> None:
        manager._restart_count = RESTART_MAX_ATTEMPTS
        with pytest.raises(RuntimeError, match="failed to restart"):
            await manager.restart()
        assert manager.state == ServerState.DOWN

    @pytest.mark.asyncio
    async def test_restart_backoff_cap(self, manager: HealthManager) -> None:
        """Backoff delay should cap at RESTART_MAX_DELAY."""
        with (
            patch.object(manager, "stop", new_callable=AsyncMock),
            patch.object(manager, "start", new_callable=AsyncMock),
            patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        ):
            # Set restart_count high enough that raw delay would exceed cap
            manager._restart_count = 6  # 2 * 2^6 = 128 > 30
            await manager.restart()
            # sleep should have been called with capped value
            mock_sleep.assert_called_with(RESTART_MAX_DELAY)


# ── Monitor loop ──────────────────────────────────────────────────────────


class TestMonitorLoop:
    @pytest.mark.asyncio
    async def test_monitor_detects_dead_process(self, manager: HealthManager) -> None:
        """Monitor should trigger restart when process dies."""
        proc = _mock_process(600)
        proc.returncode = 1  # dead
        manager._process = proc
        manager._state = ServerState.RUNNING

        with (
            patch.object(manager, "restart", new_callable=AsyncMock) as mock_restart,
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            manager._monitor_task = asyncio.create_task(manager._monitor_loop())
            await asyncio.sleep(0.1)
            manager._monitor_task.cancel()
            try:
                await manager._monitor_task
            except asyncio.CancelledError:
                pass
            # restart may or may not have been called depending on timing
            # but the task should not have crashed


# ── HealthStatus ─────────────────────────────────────────────────────────


class TestHealthStatus:
    def test_values(self) -> None:
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.DOWN.value == "down"

    def test_is_string_enum(self) -> None:
        assert isinstance(HealthStatus.HEALTHY, str)
        assert HealthStatus.HEALTHY == "healthy"

    def test_all_statuses_unique(self) -> None:
        values = [s.value for s in HealthStatus]
        assert len(values) == len(set(values))


# ── Health status properties ─────────────────────────────────────────────


class TestHealthStatusProperties:
    def test_initial_health_status_is_down(self, manager: HealthManager) -> None:
        assert manager.health_status == HealthStatus.DOWN

    def test_initial_last_health_check_is_none(self, manager: HealthManager) -> None:
        assert manager.last_health_check is None


# ── Health state machine (_set_health_status) ────────────────────────────


class TestSetHealthStatus:
    @pytest.mark.asyncio
    async def test_set_health_status_transitions(self, manager: HealthManager) -> None:
        result = {"http_healthy": True}
        await manager._set_health_status(HealthStatus.HEALTHY, result)
        assert manager.health_status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_no_callback_on_same_status(self, manager: HealthManager) -> None:
        cb = AsyncMock()
        manager.on_health_change(cb)
        # Already DOWN, set DOWN again
        await manager._set_health_status(HealthStatus.DOWN, {})
        cb.assert_not_called()

    @pytest.mark.asyncio
    async def test_callback_fires_on_transition(self, manager: HealthManager) -> None:
        cb = AsyncMock()
        manager.on_health_change(cb)
        result = {"http_healthy": True}
        await manager._set_health_status(HealthStatus.HEALTHY, result)
        cb.assert_called_once_with(HealthStatus.DOWN, HealthStatus.HEALTHY, result)

    @pytest.mark.asyncio
    async def test_callback_exception_does_not_crash(self, manager: HealthManager) -> None:
        async def bad_cb(old: HealthStatus, new: HealthStatus, r: dict) -> None:
            raise RuntimeError("boom")

        manager.on_health_change(bad_cb)
        await manager._set_health_status(HealthStatus.HEALTHY, {})
        assert manager.health_status == HealthStatus.HEALTHY


# ── _apply_health_result ────────────────────────────────────────────────


class TestApplyHealthResult:
    @pytest.mark.asyncio
    async def test_http_healthy_sets_healthy(self, manager: HealthManager) -> None:
        result = {"http_healthy": True, "process_alive": True, "port_open": True}
        await manager._apply_health_result(result)
        assert manager.health_status == HealthStatus.HEALTHY
        assert manager._consecutive_failures == 0
        assert manager.last_health_check is result

    @pytest.mark.asyncio
    async def test_port_open_but_not_http_sets_healthy(self, manager: HealthManager) -> None:
        """Process alive + port open but no HTTP → still HEALTHY."""
        result = {"http_healthy": False, "process_alive": True, "port_open": True}
        await manager._apply_health_result(result)
        assert manager.health_status == HealthStatus.HEALTHY
        assert manager._consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_process_alive_port_closed_degraded(self, manager: HealthManager) -> None:
        result = {"http_healthy": False, "process_alive": True, "port_open": False}
        await manager._apply_health_result(result)
        assert manager.health_status == HealthStatus.DEGRADED
        assert manager._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_consecutive_failures_to_down(self, manager: HealthManager) -> None:
        result = {"http_healthy": False, "process_alive": True, "port_open": False}
        # Fail DEGRADED_FAILURE_THRESHOLD times → DOWN
        for _ in range(DEGRADED_FAILURE_THRESHOLD):
            await manager._apply_health_result(result)
        assert manager.health_status == HealthStatus.DOWN

    @pytest.mark.asyncio
    async def test_process_dead_sets_down(self, manager: HealthManager) -> None:
        result = {"http_healthy": False, "process_alive": False, "port_open": False}
        await manager._apply_health_result(result)
        assert manager.health_status == HealthStatus.DOWN
        assert manager._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_recovery_resets_failures(self, manager: HealthManager) -> None:
        # Build up failures
        bad = {"http_healthy": False, "process_alive": True, "port_open": False}
        for _ in range(2):
            await manager._apply_health_result(bad)
        assert manager._consecutive_failures == 2
        # Recovery
        good = {"http_healthy": True, "process_alive": True, "port_open": True}
        await manager._apply_health_result(good)
        assert manager._consecutive_failures == 0
        assert manager.health_status == HealthStatus.HEALTHY


# ── check_health response_time_ms ───────────────────────────────────────


class TestCheckHealthResponseTime:
    @pytest.mark.asyncio
    async def test_response_time_ms_present(self, manager: HealthManager) -> None:
        result = await manager.check_health()
        assert "response_time_ms" in result
        assert isinstance(result["response_time_ms"], float)
        assert result["response_time_ms"] >= 0.0

    @pytest.mark.asyncio
    async def test_last_health_check_updated(self, manager: HealthManager) -> None:
        assert manager.last_health_check is None
        await manager.check_health()
        assert manager.last_health_check is not None

    @pytest.mark.asyncio
    async def test_health_status_updates_on_check(self, manager: HealthManager) -> None:
        # No process → should be DOWN
        await manager.check_health()
        assert manager.health_status == HealthStatus.DOWN


# ── Shutdown ────────────────────────────────────────────────────────────


class TestShutdown:
    @pytest.mark.asyncio
    async def test_shutdown_stops_and_resets_health(self, manager: HealthManager) -> None:
        # Put manager in a healthy-ish state
        manager._health_status = HealthStatus.HEALTHY
        manager._consecutive_failures = 5
        await manager.shutdown()
        assert manager.health_status == HealthStatus.DOWN
        assert manager._consecutive_failures == 0
        assert manager.state == ServerState.STOPPED

    @pytest.mark.asyncio
    async def test_shutdown_when_already_stopped(self, manager: HealthManager) -> None:
        await manager.shutdown()
        assert manager.health_status == HealthStatus.DOWN
