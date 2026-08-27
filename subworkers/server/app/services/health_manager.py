"""OpenCode server lifecycle manager.

Handles start/stop/health/restart of the OpenCode subprocess with:
- Exponential backoff on restart (2s → 4s → ... → 30s max)
- Auto-restart on crash (poll every 10s, max 10 attempts)
- Graceful shutdown (SIGTERM → 2s → SIGKILL)
- PID file management
- Health state machine (healthy → degraded → down)
- Structured logging for all events
"""
from __future__ import annotations

import asyncio
import os
import signal
import socket
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Coroutine

import structlog

from app.utils.exceptions import OpenCodeConnectionError
from app.utils.opencode_client import OpenCodeClient

log = structlog.get_logger()

# ── Constants ───────────────────────────────────────────────────────────
DEFAULT_PORT = 5655
DEFAULT_HOST = "127.0.0.1"
HEALTH_POLL_INTERVAL = 10.0  # seconds between health checks
HEALTH_BACKOFF_BASE = 2.0  # initial backoff on consecutive errors
HEALTH_BACKOFF_MAX = 60.0  # max backoff on consecutive errors
RESTART_BASE_DELAY = 2.0  # initial backoff delay
RESTART_MAX_DELAY = 30.0  # max backoff delay
RESTART_MAX_ATTEMPTS = 10  # max restart attempts before abort
GRACEFUL_SHUTDOWN_WAIT = 2.0  # seconds to wait after SIGTERM before SIGKILL
PID_FILE_NAME = "opencode.pid"
DEGRADED_FAILURE_THRESHOLD = 3  # consecutive failures before DOWN


class ServerState(str, Enum):
    """OpenCode server lifecycle states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    RESTARTING = "restarting"
    STOPPING = "stopping"
    DOWN = "down"  # crashed and max restarts exceeded


class HealthStatus(str, Enum):
    """Server health status (distinct from lifecycle ServerState)."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


# ── Type aliases ────────────────────────────────────────────────────────
StateCallback = Callable[[ServerState, ServerState], Coroutine[Any, Any, None]]
HealthCallback = Callable[[HealthStatus, HealthStatus, dict[str, Any]], Coroutine[Any, Any, None]]


class HealthManager:
    """Manages the OpenCode server subprocess lifecycle.

    Usage::

        manager = HealthManager(port=5655, work_dir="/path/to/opencode")
        await manager.start()
        # ... server running ...
        await manager.stop()
    """

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        host: str = DEFAULT_HOST,
        work_dir: str | None = None,
        opencode_bin: str = "opencode",
        pid_dir: str | None = None,
        manage_process: bool = True,
    ) -> None:
        self._port = port
        self._host = host
        self._work_dir = work_dir
        self._opencode_bin = opencode_bin
        self._pid_dir = pid_dir or str(Path.cwd())
        self._manage_process = manage_process

        self._process: asyncio.subprocess.Process | None = None
        self._state = ServerState.STOPPED
        self._restart_count = 0
        self._monitor_task: asyncio.Task[None] | None = None
        self._state_callbacks: list[StateCallback] = []
        self._pid_file = Path(self._pid_dir) / PID_FILE_NAME

        self._health_status = HealthStatus.DOWN
        self._consecutive_failures = 0
        self._health_callbacks: list[HealthCallback] = []
        self._last_health_check: dict[str, Any] | None = None

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def state(self) -> ServerState:
        return self._state

    @property
    def pid(self) -> int | None:
        return self._process.pid if self._process else None

    @property
    def base_url(self) -> str:
        return f"http://{self._host}:{self._port}"

    @property
    def pid_file(self) -> Path:
        return self._pid_file

    @property
    def restart_count(self) -> int:
        return self._restart_count

    @property
    def health_status(self) -> HealthStatus:
        return self._health_status

    @property
    def last_health_check(self) -> dict[str, Any] | None:
        return self._last_health_check

    # ── Health state machine ────────────────────────────────────────────

    def on_health_change(self, callback: HealthCallback) -> None:
        self._health_callbacks.append(callback)

    async def _set_health_status(
        self, new_status: HealthStatus, check_result: dict[str, Any]
    ) -> None:
        old_status = self._health_status
        if old_status == new_status:
            return
        self._health_status = new_status
        log.info(
            "health.status_change",
            old=old_status.value,
            new=new_status.value,
            failures=self._consecutive_failures,
        )
        for callback in self._health_callbacks:
            try:
                await callback(old_status, new_status, check_result)
            except Exception:
                log.exception(
                    "health.callback_error",
                    old=old_status.value,
                    new=new_status.value,
                )

    # ── State management ────────────────────────────────────────────────

    async def _set_state(self, new_state: ServerState) -> None:
        old_state = self._state
        if old_state == new_state:
            return
        self._state = new_state
        log.info(
            "lifecycle.state_change",
            old=old_state.value,
            new=new_state.value,
            pid=self.pid,
        )
        for callback in self._state_callbacks:
            try:
                await callback(old_state, new_state)
            except Exception:
                log.exception("lifecycle.state_callback_error", new=new_state.value)

    def on_state_change(self, callback: StateCallback) -> None:
        """Register a callback for state transitions."""
        self._state_callbacks.append(callback)

    # ── PID file management ─────────────────────────────────────────────

    def _write_pid(self) -> None:
        if self.pid is None:
            return
        self._pid_file.write_text(str(self.pid))
        log.info("lifecycle.pid_written", pid=self.pid, path=str(self._pid_file))

    def _read_pid(self) -> int | None:
        try:
            return int(self._pid_file.read_text())
        except (FileNotFoundError, ValueError):
            return None

    def _cleanup_pid(self) -> None:
        try:
            self._pid_file.unlink(missing_ok=True)
        except OSError:
            pass

    # ── Start ───────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the OpenCode server subprocess."""
        if self._state in (ServerState.RUNNING, ServerState.STARTING):
            log.warning("lifecycle.already_running", state=self._state.value)
            return

        await self._set_state(ServerState.STARTING)

        cmd = [self._opencode_bin, "serve", "--port", str(self._port)]
        log.info("lifecycle.starting", cmd=cmd, work_dir=self._work_dir)

        try:
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self._work_dir,
            )
            self._write_pid()
            await self._set_state(ServerState.RUNNING)
            self._restart_count = 0
            log.info("lifecycle.started", pid=self.pid)
        except FileNotFoundError as exc:
            log.error("lifecycle.binary_not_found", binary=self._opencode_bin)
            await self._set_state(ServerState.DOWN)
            raise RuntimeError(f"OpenCode binary not found: {self._opencode_bin}") from exc
        except Exception as exc:
            log.error("lifecycle.start_failed", error=str(exc))
            await self._set_state(ServerState.DOWN)
            raise

    # ── Stop ────────────────────────────────────────────────────────────

    async def stop(self) -> None:
        """Stop the OpenCode server gracefully.

        Sends SIGTERM, waits GRACEFUL_SHUTDOWN_WAIT, then SIGKILL if needed.
        """
        if self._state == ServerState.STOPPED:
            return

        await self._set_state(ServerState.STOPPING)

        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

        if self._process and self._process.returncode is None:
            log.info("lifecycle.stopping", pid=self.pid)
            try:
                self._process.send_signal(signal.SIGTERM)
                try:
                    await asyncio.wait_for(
                        self._process.wait(), timeout=GRACEFUL_SHUTDOWN_WAIT
                    )
                except asyncio.TimeoutError:
                    log.warning("lifecycle.force_kill", pid=self.pid)
                    self._process.kill()
                    try:
                        await self._process.wait()
                    except asyncio.TimeoutError:
                        pass  # process stuck, move on
            except ProcessLookupError:
                pass  # already dead

        self._cleanup_pid()
        self._process = None
        self._restart_count = 0
        await self._set_state(ServerState.STOPPED)
        log.info("lifecycle.stopped")

    # ── Health check ────────────────────────────────────────────────────

    async def check_health(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "process_alive": False,
            "port_open": False,
            "http_healthy": False,
            "response_time_ms": 0.0,
            "details": "",
        }

        start = time.monotonic()

        if self._manage_process:
            if self._process and self._process.returncode is None:
                result["process_alive"] = True
            else:
                result["details"] = "process not running"
                result["response_time_ms"] = round((time.monotonic() - start) * 1000, 2)
                await self._apply_health_result(result)
                return result
        else:
            # External server — process ownership is unknown; port + HTTP decide.
            result["process_alive"] = True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((self._host, self._port))
            sock.close()
            result["port_open"] = True
        except (socket.timeout, ConnectionRefusedError, OSError) as exc:
            result["details"] = f"port {self._port} not open: {exc}"
            result["response_time_ms"] = round((time.monotonic() - start) * 1000, 2)
            await self._apply_health_result(result)
            return result

        try:
            async with OpenCodeClient(self.base_url, default_timeout=5.0) as client:
                health = await client.health()
                result["http_healthy"] = health.get("healthy", False)
                result["details"] = str(health)
        except (OpenCodeConnectionError, Exception) as exc:
            result["details"] = f"HTTP check failed: {exc}"

        result["response_time_ms"] = round((time.monotonic() - start) * 1000, 2)
        await self._apply_health_result(result)
        return result

    async def _apply_health_result(self, result: dict[str, Any]) -> None:
        self._last_health_check = result

        if result["http_healthy"]:
            self._consecutive_failures = 0
            await self._set_health_status(HealthStatus.HEALTHY, result)
        elif result["process_alive"] and result["port_open"]:
            self._consecutive_failures = 0
            await self._set_health_status(HealthStatus.HEALTHY, result)
        elif result["process_alive"]:
            self._consecutive_failures += 1
            if self._consecutive_failures >= DEGRADED_FAILURE_THRESHOLD:
                await self._set_health_status(HealthStatus.DOWN, result)
            else:
                await self._set_health_status(HealthStatus.DEGRADED, result)
        else:
            self._consecutive_failures += 1
            await self._set_health_status(HealthStatus.DOWN, result)

    async def is_healthy(self) -> bool:
        check = await self.check_health()
        return check["process_alive"] and check["http_healthy"]

    # ── Restart ─────────────────────────────────────────────────────────

    async def restart(self) -> None:
        """Restart with exponential backoff.

        Delay: 2s → 4s → 8s → 16s → 30s (capped).
        After RESTART_MAX_ATTEMPTS, sets state to DOWN and raises.
        """
        self._restart_count += 1

        if self._restart_count > RESTART_MAX_ATTEMPTS:
            log.error(
                "lifecycle.max_restarts_exceeded",
                attempts=self._restart_count,
            )
            await self._set_state(ServerState.DOWN)
            raise RuntimeError(
                f"OpenCode server failed to restart after {RESTART_MAX_ATTEMPTS} attempts"
            )

        delay = min(
            RESTART_BASE_DELAY * (2 ** (self._restart_count - 1)),
            RESTART_MAX_DELAY,
        )
        log.info(
            "lifecycle.restarting",
            attempt=self._restart_count,
            delay=delay,
        )
        await self._set_state(ServerState.RESTARTING)
        await asyncio.sleep(delay)

        await self.stop()
        await self.start()

    # ── Auto-restart on crash ───────────────────────────────────────────

    async def start_with_monitor(self) -> None:
        await self.start()
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def start_external_monitor(self) -> None:
        """Track an externally managed OpenCode server (no subprocess).

        Used in Docker where opencode runs on the host via opencode-serve.sh.
        """
        self._state = ServerState.RUNNING
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self) -> None:
        log.info("health.monitor_started", interval=HEALTH_POLL_INTERVAL)
        monitor_errors = 0
        while True:
            try:
                interval = HEALTH_POLL_INTERVAL + min(
                    monitor_errors * HEALTH_BACKOFF_BASE, HEALTH_BACKOFF_MAX
                )
                await asyncio.sleep(interval)
                monitor_errors = 0

                if self._manage_process and self._process and self._process.returncode is not None:
                    log.warning(
                        "health.process_died",
                        returncode=self._process.returncode,
                    )
                    await self.restart()
                    continue

                if self._state == ServerState.RUNNING:
                    await self.check_health()

            except asyncio.CancelledError:
                log.info("health.monitor_stopped")
                break
            except Exception:
                monitor_errors += 1
                log.exception(
                    "health.monitor_error",
                    consecutive_errors=monitor_errors,
                )

    async def shutdown(self) -> None:
        await self.stop()
        self._health_status = HealthStatus.DOWN
        self._consecutive_failures = 0
        log.info("health.manager_shutdown")
