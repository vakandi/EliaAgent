"""SubworkerScheduler — APScheduler integration with JSON-based scheduling.

Loads subworker configs, creates cron/interval jobs, supports manual triggers
and hot-reload without losing running subworker state.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Coroutine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import structlog

from app.config.models import CronSchedule, IntervalSchedule, SubworkerConfig

log = structlog.get_logger(__name__)

# ── Type aliases ────────────────────────────────────────────────────────
RunFn = Callable[[SubworkerConfig, str | None, str | None], Coroutine[Any, Any, Any]]


# ── Scheduler ───────────────────────────────────────────────────────────

class SubworkerScheduler:
    """Wraps APScheduler to manage subworker execution on configured schedules.

    Usage::

        scheduler = SubworkerScheduler(run_fn=my_runner.run_subworker)
        await scheduler.start()
        scheduler.add_subworker(config)
        result = await scheduler.trigger_now("my-subworker")
    """

    def __init__(self, run_fn: RunFn, state_file: Path | str | None = None) -> None:
        self._run_fn = run_fn
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._configs: dict[str, SubworkerConfig] = {}
        self._running: dict[str, asyncio.Task[None]] = {}
        self._last_session_ids: dict[str, str] = {}
        self._last_run_results: dict[str, dict[str, Any]] = {}
        self._callbacks: list[Callable[[str, str], Coroutine[Any, Any, None]]] = []
        self._state_file = Path(state_file) if state_file else None
        self._load_state()

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the underlying APScheduler."""
        if not self._scheduler.running:
            self._scheduler.start()
            log.info("scheduler.started")

    async def stop(self) -> None:
        """Shut down the scheduler and cancel any running tasks."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            log.info("scheduler.stopped")
        for name, task in self._running.items():
            if not task.done():
                task.cancel()
                log.info("scheduler.cancelled_running name=%s", name)
        self._running.clear()

    # ── Public API ────────────────────────────────────────────────────────

    def add_subworker(self, config: SubworkerConfig) -> None:
        """Add or update a subworker's schedule in the scheduler."""
        self._configs[config.name] = config

        # Remove existing job if updating
        job_id = self._job_id(config.name)
        existing = self._scheduler.get_job(job_id)
        if existing:
            self._scheduler.remove_job(job_id)

        if not config.enabled:
            log.info("scheduler.subworker_disabled name=%s", config.name)
            return

        trigger = self._build_trigger(config)
        self._scheduler.add_job(
            self._execute,
            trigger=trigger,
            args=[config],
            id=job_id,
            name=f"subworker:{config.name}",
            replace_existing=True,
            misfire_grace_time=60,
        )
        next_run = self._scheduler.get_job(job_id)
        next_run_time = getattr(next_run, "next_run_time", None) if next_run else None
        log.info(
            "scheduler.subworker_added name=%s next_run=%s",
            config.name,
            next_run_time.isoformat() if next_run_time else "pending",
        )

    def remove_subworker(self, name: str) -> bool:
        """Remove a subworker from the scheduler. Returns True if found."""
        self._configs.pop(name, None)
        job_id = self._job_id(name)
        job = self._scheduler.get_job(job_id)
        if job:
            self._scheduler.remove_job(job_id)
            log.info("scheduler.subworker_removed name=%s", name)
            return True
        return False

    async def trigger_now(
        self,
        name: str,
        prompt: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Manually trigger a subworker immediately (outside schedule)."""
        config = self._configs.get(name)
        if not config:
            return {"status": "error", "message": f"Subworker '{name}' not found"}

        if name in self._running and not self._running[name].done():
            return {"status": "error", "message": f"Subworker '{name}' is already running"}

        task = asyncio.create_task(self._execute(config, prompt, model))
        self._running[name] = task
        return {"status": "triggered", "name": name}

    def get_next_run(self, name: str) -> datetime | None:
        """Return the next scheduled run time for a subworker."""
        job_id = self._job_id(name)
        job = self._scheduler.get_job(job_id)
        return getattr(job, "next_run_time", None) if job else None

    def get_status(self) -> dict[str, Any]:
        """Return scheduler status and all registered subworkers."""
        jobs = []
        for name, config in self._configs.items():
            job_id = self._job_id(name)
            job = self._scheduler.get_job(job_id)
            next_run_time = getattr(job, "next_run_time", None) if job else None
            jobs.append({
                "name": name,
                "enabled": config.enabled,
                "running": name in self._running and not self._running[name].done(),
                "next_run": next_run_time.isoformat() if next_run_time else None,
            })
        return {
            "scheduler_running": self._scheduler.running,
            "job_count": len(jobs),
            "jobs": jobs,
        }

    def get_running(self) -> list[str]:
        """Return names of currently running subworkers."""
        return [
            name for name, task in self._running.items()
            if not task.done()
        ]

    def get_last_session_id(self, name: str) -> str | None:
        return self._last_session_ids.get(name)

    def get_last_run_result(self, name: str) -> dict[str, Any] | None:
        return self._last_run_results.get(name)

    async def reload_schedules(
        self,
        configs: list[SubworkerConfig],
        *,
        preserve_running: bool = True,
    ) -> dict[str, Any]:
        """Reload all schedules from new config list without stopping running tasks.

        Returns summary of changes.
        """
        old_names = set(self._configs.keys())
        new_configs = {sw.name: sw for sw in configs}
        new_names = set(new_configs.keys())

        added = new_names - old_names
        removed = old_names - new_names
        updated = old_names & new_names

        # Only reload schedules for subworkers that aren't currently running
        for name in removed:
            if preserve_running and name in self._running and not self._running[name].done():
                log.info("scheduler.reload_skip_running name=%s", name)
                continue
            self.remove_subworker(name)

        for name in added:
            self.add_subworker(new_configs[name])

        for name in updated:
            if preserve_running and name in self._running and not self._running[name].done():
                log.info("scheduler.reload_skip_running name=%s", name)
                continue
            self.add_subworker(new_configs[name])

        self._configs = new_configs

        result = {
            "added": sorted(added),
            "removed": sorted(removed),
            "updated": sorted(updated),
            "total": len(new_configs),
        }
        log.info("scheduler.reloaded %s", result)
        return result

    # ── Callbacks ─────────────────────────────────────────────────────────

    def on_run_complete(self, callback: Callable[[str, str], Coroutine[Any, Any, None]]) -> None:
        """Register callback(name, status) for run completion."""
        self._callbacks.append(callback)

    # ── Private ───────────────────────────────────────────────────────────

    def _load_state(self) -> None:
        if not self._state_file or not self._state_file.exists():
            return
        try:
            data = json.loads(self._state_file.read_text())
            sessions = data.get("last_session_ids")
            if isinstance(sessions, dict):
                self._last_session_ids = {
                    k: v for k, v in sessions.items() if isinstance(v, str)
                }
            results = data.get("last_run_results")
            if isinstance(results, dict):
                self._last_run_results = results
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("scheduler.state_load_failed file=%s error=%s", self._state_file, exc)

    def _save_state(self) -> None:
        if not self._state_file:
            return
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps({
                "last_session_ids": self._last_session_ids,
                "last_run_results": self._last_run_results,
            }, indent=2)
            tmp = self._state_file.with_suffix(".json.tmp")
            tmp.write_text(payload)
            tmp.replace(self._state_file)
        except OSError as exc:
            log.error("scheduler.state_save_failed file=%s error=%s", self._state_file, exc)

    async def _execute(
        self,
        config: SubworkerConfig,
        prompt: str | None = None,
        model: str | None = None,
    ) -> None:
        """Run a subworker and handle completion."""
        name = config.name
        log.info("scheduler.run_start name=%s", name)
        try:
            result = await self._run_fn(config, prompt, model)
            if hasattr(result, "session_id") and result.session_id:
                self._last_session_ids[name] = result.session_id
            if hasattr(result, "stdout"):
                self._last_run_results[name] = {
                    "session_id": getattr(result, "session_id", None),
                    "success": getattr(result, "success", False),
                    "stdout": getattr(result, "stdout", ""),
                    "duration_seconds": getattr(result, "total_duration_seconds", 0),
                }
            self._save_state()
            log.info("scheduler.run_complete name=%s status=success", name)
            await self._fire_callbacks(name, "success")
        except asyncio.CancelledError:
            log.info("scheduler.run_cancelled name=%s", name)
            await self._fire_callbacks(name, "cancelled")
        except Exception as exc:
            log.error("scheduler.run_error name=%s error=%s", name, str(exc))
            await self._fire_callbacks(name, "error")
        finally:
            self._running.pop(name, None)

    async def _fire_callbacks(self, name: str, status: str) -> None:
        for cb in self._callbacks:
            try:
                await cb(name, status)
            except Exception:
                log.exception("scheduler.callback_error name=%s", name)

    def _build_trigger(self, config: SubworkerConfig) -> CronTrigger:
        """Convert a Schedule config to an APScheduler CronTrigger."""
        schedule = config.schedule
        if isinstance(schedule, CronSchedule):
            parts = schedule.expression.split()
            if len(parts) != 5:
                raise ValueError(f"Invalid cron expression: {schedule.expression}")
            return CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
            )
        elif isinstance(schedule, IntervalSchedule):
            # Interval: run at specific hours array, each at the specified minute
            # Convert to cron: minute=X, hour=H1,H2,...
            hours_str = ",".join(str(h) for h in sorted(schedule.hours))
            return CronTrigger(minute=schedule.minute, hour=hours_str)
        else:
            raise ValueError(f"Unknown schedule type: {type(schedule)}")

    @staticmethod
    def _job_id(name: str) -> str:
        return f"subworker:{name}"
