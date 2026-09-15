"""IdleCleanupManager — detects idle sessions and cleans up memory-hogging processes.

When all enabled subworkers are idle (not running) for more than IDLE_TIMEOUT,
the manager kills parallel-browser-mcp and Chrome headless processes that
consume the majority of container RAM. This prevents OOM-kills caused by
stale browser instances left running after subworker runs complete.

The system:
  1. Checks every CHECK_INTERVAL seconds whether all enabled subworkers are idle
  2. Tracks how long they've been idle (IDLE_TIMEOUT seconds, default 300 = 5min)
  3. When idle threshold is reached, kills parallel-browser-mcp + Chrome processes
  4. Optionally restarts opencode if it was OOM-killed
  5. Resets the idle timer after cleanup
"""
from __future__ import annotations

import asyncio
import os
import signal
import time
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# ── Defaults ──────────────────────────────────────────────────────
IDLE_TIMEOUT = 300          # seconds (5 minutes)
CHECK_INTERVAL = 30         # seconds between idle checks
MAX_IDLE_RESTARTS = 3       # max cleanup cycles before full opencode restart
CLEANUP_COOLDOWN = 60       # seconds between cleanup attempts

# ── Process patterns to kill ──────────────────────────────────────
PARALLEL_BROWSER_PATTERN = "parallel-browser-mcp"
CHROME_PATTERN = "chromium_headless_shell"
CHROME_UTILITY_PATTERN = "chrome-headless-shell"


class IdleCleanupManager:
    """Monitors subworker idle state and cleans up stale browser processes.

    Usage::

        mgr = IdleCleanupManager(scheduler, health_manager)
        await mgr.start()
        # ... runs in background ...
        await mgr.stop()
    """

    def __init__(
        self,
        scheduler: Any,
        health_manager: Any,
        *,
        idle_timeout: int = IDLE_TIMEOUT,
        check_interval: int = CHECK_INTERVAL,
        max_idle_restarts: int = MAX_IDLE_RESTARTS,
        cooldown: int = CLEANUP_COOLDOWN,
    ) -> None:
        self._scheduler = scheduler
        self._health = health_manager
        self._idle_timeout = idle_timeout
        self._check_interval = check_interval
        self._max_idle_restarts = max_idle_restarts
        self._cooldown = cooldown

        self._idle_since: float | None = None
        self._cleanup_count = 0
        self._last_cleanup: float = 0
        self._task: asyncio.Task[None] | None = None
        self._running = False

    # ── Properties ──────────────────────────────────────────────

    @property
    def idle_since(self) -> float | None:
        """When the system went idle, or None if currently active."""
        return self._idle_since

    @property
    def is_idle(self) -> bool:
        """Whether all enabled subworkers have been idle for longer than the timeout."""
        if self._idle_since is None:
            return False
        return time.time() - self._idle_since > self._idle_timeout

    @property
    def enabled_count(self) -> int:
        """Number of enabled subworkers."""
        try:
            return len([
                s for s in self._scheduler._configs.values()
                if s.enabled
            ])
        except Exception:
            return 0

    @property
    def running_count(self) -> int:
        """Number of currently running subworkers."""
        return len(self._scheduler.get_running())

    # ── Lifecycle ───────────────────────────────────────────────

    async def start(self) -> None:
        """Start the idle monitoring background task."""
        if self._running:
            log.warning("idle_cleanup.already_running")
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        log.info("idle_cleanup.started", interval=self._check_interval, timeout=self._idle_timeout)

    async def stop(self) -> None:
        """Stop the idle monitoring background task."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        log.info("idle_cleanup.stopped", cleanup_count=self._cleanup_count)

    # ── Main loop ───────────────────────────────────────────────

    async def _monitor_loop(self) -> None:
        """Background task: check idle state and trigger cleanup."""
        log.info("idle_cleanup.monitor_started")
        while self._running:
            try:
                await asyncio.sleep(self._check_interval)
                await self._check_and_cleanup()
            except asyncio.CancelledError:
                log.info("idle_cleanup.monitor_stopped")
                break
            except Exception:
                log.exception("idle_cleanup.monitor_error")

    async def _check_and_cleanup(self) -> None:
        """Check if all enabled subworkers are idle, and clean up if so."""
        running = self.running_count
        enabled = self.enabled_count

        if enabled == 0:
            # No enabled subworkers — nothing to do
            self._idle_since = None
            return

        if running == 0:
            # All enabled subworkers are idle
            if self._idle_since is None:
                self._idle_since = time.time()
                idle_seconds = 0
                log.info(
                    "idle_cleanup.idle_detected",
                    enabled=enabled,
                    running=running,
                    idle_for=0,
                )
            else:
                idle_seconds = int(time.time() - self._idle_since)
                log.debug(
                    "idle_cleanup.still_idle",
                    enabled=enabled,
                    running=running,
                    idle_for=idle_seconds,
                    timeout=self._idle_timeout,
                )

            if self.is_idle:
                await self._cleanup()
        else:
            # Some subworkers are running — reset idle timer
            if self._idle_since is not None:
                log.info(
                    "idle_cleanup.active_again",
                    running=running,
                    idle_for=int(time.time() - self._idle_since),
                )
                self._idle_since = None

    # ── Cleanup ─────────────────────────────────────────────────

    async def _cleanup(self) -> None:
        """Kill parallel-browser-mcp and Chrome processes to free RAM."""
        # Cooldown check — avoid rapid cleanup cycles
        now = time.time()
        if now - self._last_cleanup < self._cooldown:
            log.debug("idle_cleanup.cooldown_active", seconds=int(now - self._last_cleanup))
            return

        self._last_cleanup = now
        self._cleanup_count += 1

        log.warning(
            "idle_cleanup.starting",
            idle_for=int(time.time() - self._idle_since),
            cleanup_count=self._cleanup_count,
            enabled=self.enabled_count,
        )

        killed = await self._kill_browser_processes()

        # If we've done many cleanup cycles, restart opencode to reset its memory
        if self._cleanup_count >= self._max_idle_restarts:
            log.warning(
                "idle_cleanup.max_restarts_reached",
                count=self._cleanup_count,
                max=self._max_idle_restarts,
            )
            await self._restart_opencode()
            self._cleanup_count = 0

        # Reset idle timer after cleanup
        self._idle_since = None
        log.info("idle_cleanup.complete", killed=killed, cleanup_count=self._cleanup_count)

    async def _kill_browser_processes(self) -> dict[str, int]:
        """Kill parallel-browser-mcp and Chrome headless processes.

        Returns a dict with counts of killed processes per type.
        """
        killed: dict[str, int] = {}

        for pattern, label in [
            (PARALLEL_BROWSER_PATTERN, "parallel-browser-mcp"),
            (CHROME_PATTERN, "chromium_headless_shell"),
            (CHROME_UTILITY_PATTERN, "chrome-headless-shell"),
        ]:
            count = await self._kill_processes_by_pattern(pattern)
            killed[label] = count
            if count > 0:
                log.info("idle_cleanup.killed", label=label, count=count)

        return killed

    async def _kill_processes_by_pattern(self, pattern: str) -> int:
        """Kill all processes matching the given pattern. Returns count killed."""
        try:
            # Use pgrep to find PIDs, then kill them
            proc = await asyncio.create_subprocess_exec(
                "pgrep", "-f", pattern,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                return 0  # No matching processes

            pids = [
                line.strip()
                for line in stdout.decode().splitlines()
                if line.strip()
            ]

            if not pids:
                return 0

            # Kill each process
            killed = 0
            for pid_str in pids:
                try:
                    pid = int(pid_str)
                    # Skip our own process
                    if pid == os.getpid():
                        continue
                    os.kill(pid, signal.SIGTERM)
                    killed += 1
                except (ProcessLookupError, PermissionError, ValueError):
                    pass

            # Wait a moment, then force-kill any survivors
            await asyncio.sleep(1)
            for pid_str in pids:
                try:
                    pid = int(pid_str)
                    if pid == os.getpid():
                        continue
                    os.kill(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError, ValueError):
                    pass

            return killed

        except Exception:
            log.exception("idle_cleanup.kill_error", pattern=pattern)
            return 0

    async def _restart_opencode(self) -> None:
        """Restart the opencode server to reset its memory footprint.

        Only called when cleanup cycles exceed MAX_IDLE_RESTARTS, indicating
        a possible memory leak in the opencode/bun runtime.
        """
        log.warning("idle_cleanup.restarting_opencode")
        try:
            if self._health and hasattr(self._health, 'restart'):
                await self._health.restart()
                log.info("idle_cleanup.opencode_restarted")
            else:
                log.warning("idle_cleanup.no_health_manager_restart")
        except Exception:
            log.exception("idle_cleanup.opencode_restart_failed")

    # ── Status ──────────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """Return current idle cleanup status for monitoring."""
        return {
            "idle_cleanup_active": self._running,
            "idle_since": self._idle_since,
            "is_idle": self.is_idle,
            "idle_timeout": self._idle_timeout,
            "check_interval": self._check_interval,
            "cooldown": self._cooldown,
            "cleanup_count": self._cleanup_count,
            "max_idle_restarts": self._max_idle_restarts,
            "enabled_count": self.enabled_count,
            "running_count": self.running_count,
        }
