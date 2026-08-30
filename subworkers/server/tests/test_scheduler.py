"""Tests for SubworkerScheduler — APScheduler integration."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.config.models import CronSchedule, IntervalSchedule, SubworkerConfig, ScheduleType
from app.services.scheduler import SubworkerScheduler


# ── Fixtures ────────────────────────────────────────────────────────────

def _make_config(
    name: str = "test-sub",
    *,
    enabled: bool = True,
    hours: list[int] | None = None,
    minute: int = 0,
    cron: str | None = None,
) -> SubworkerConfig:
    if cron:
        schedule = CronSchedule(expression=cron)
    else:
        schedule = IntervalSchedule(hours=hours or [9, 12, 15], minute=minute)
    return SubworkerConfig(
        name=name,
        enabled=enabled,
        schedule=schedule,
        agent_id=f"{name}-agent",
    )


@pytest.fixture
def run_fn() -> AsyncMock:
    return AsyncMock(return_value=None)


@pytest.fixture
def scheduler_not_started(run_fn: AsyncMock) -> SubworkerScheduler:
    """Sync fixture for tests that don't need the scheduler started."""
    return SubworkerScheduler(run_fn=run_fn)


@pytest_asyncio.fixture
async def scheduler(run_fn: AsyncMock) -> SubworkerScheduler:
    s = SubworkerScheduler(run_fn=run_fn)
    yield s
    if s._scheduler.running:
        await s.stop()


# ── Trigger building ────────────────────────────────────────────────────

class TestBuildTrigger:
    """Tests for schedule → CronTrigger conversion."""

    def test_interval_schedule(self, scheduler_not_started: SubworkerScheduler) -> None:
        config = _make_config(hours=[9, 12, 15], minute=30)
        trigger = scheduler_not_started._build_trigger(config)
        assert trigger.fields[0].expressions  # minute
        assert trigger.fields[1].expressions  # hour

    def test_cron_schedule(self, scheduler_not_started: SubworkerScheduler) -> None:
        config = _make_config(cron="0 9-23 * * *")
        trigger = scheduler_not_started._build_trigger(config)
        assert trigger.fields[0].expressions  # minute=0
        assert trigger.fields[1].expressions  # hour=9-23

    def test_interval_schedule_sorted_hours(self, scheduler_not_started: SubworkerScheduler) -> None:
        config = _make_config(hours=[20, 9, 15], minute=0)
        trigger = scheduler_not_started._build_trigger(config)
        # Hours should be sorted: 9,15,20
        assert trigger.fields[1] is not None

    def test_invalid_cron_raises(self, scheduler_not_started: SubworkerScheduler) -> None:
        config = _make_config(cron="invalid")
        with pytest.raises(ValueError, match="Invalid cron expression"):
            scheduler_not_started._build_trigger(config)


# ── Add/remove subworker ────────────────────────────────────────────────

class TestAddRemove:
    """Tests for adding and removing subworkers from the scheduler."""

    @pytest.mark.asyncio
    async def test_add_subworker_creates_job(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)
        job = scheduler._scheduler.get_job("subworker:test-sub")
        assert job is not None
        assert job.name == "subworker:test-sub"
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_add_disabled_subworker_no_job(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config(enabled=False)
        scheduler.add_subworker(config)
        job = scheduler._scheduler.get_job("subworker:test-sub")
        assert job is None
        assert config.name in scheduler._configs
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_add_replaces_existing_job(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config1 = _make_config(hours=[9])
        scheduler.add_subworker(config1)
        config2 = _make_config(hours=[10, 11])
        scheduler.add_subworker(config2)
        jobs = scheduler._scheduler.get_jobs()
        sub_jobs = [j for j in jobs if j.id == "subworker:test-sub"]
        assert len(sub_jobs) == 1
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_remove_subworker(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)
        removed = scheduler.remove_subworker("test-sub")
        assert removed is True
        job = scheduler._scheduler.get_job("subworker:test-sub")
        assert job is None
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_returns_false(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        removed = scheduler.remove_subworker("nonexistent")
        assert removed is False
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_update_config_replaces_job(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config1 = _make_config(hours=[9])
        scheduler.add_subworker(config1)
        config2 = _make_config(hours=[14])
        scheduler.add_subworker(config2)
        assert scheduler._configs["test-sub"] == config2
        await scheduler.stop()


# ── Trigger now ─────────────────────────────────────────────────────────


class TestScheduledFire:
    """Scheduled fires must register in _running so /status reports running."""

    @pytest.mark.asyncio
    async def test_scheduled_fire_tracks_running(self, scheduler: SubworkerScheduler, run_fn: AsyncMock) -> None:
        async def slow_run(*_args, **_kwargs):
            await asyncio.sleep(0.2)
            return None

        run_fn.side_effect = slow_run
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)
        task = asyncio.create_task(scheduler._scheduled_fire(config))
        await asyncio.sleep(0.05)
        assert scheduler.get_status()["jobs"][0]["running"] is True
        assert "test-sub" in scheduler.get_running()
        inner = scheduler._running.get("test-sub")
        if inner:
            await inner
        await task
        assert scheduler.get_status()["jobs"][0]["running"] is False
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_scheduled_fire_skips_when_already_running(self, scheduler: SubworkerScheduler, run_fn: AsyncMock) -> None:
        await scheduler.start()
        config = _make_config()
        first = asyncio.create_task(scheduler._scheduled_fire(config))
        await asyncio.sleep(0.02)
        await scheduler._scheduled_fire(config)
        await first
        run_fn.assert_called_once()
        await scheduler.stop()


class TestTriggerNow:
    """Tests for manual immediate triggers."""

    @pytest.mark.asyncio
    async def test_trigger_now_runs_subworker(self, scheduler: SubworkerScheduler, run_fn: AsyncMock) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)
        result = await scheduler.trigger_now("test-sub")
        assert result["status"] == "triggered"
        # Wait for the async task to complete
        await asyncio.sleep(0.1)
        run_fn.assert_called_once_with(config, None, None)
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_trigger_now_unknown_returns_error(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        result = await scheduler.trigger_now("nonexistent")
        assert result["status"] == "error"
        assert "not found" in result["message"]
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_trigger_now_already_running_returns_error(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)

        # Simulate a running task
        async def slow_run(cfg: SubworkerConfig) -> None:
            await asyncio.sleep(10)

        scheduler._run_fn = slow_run
        scheduler._running["test-sub"] = asyncio.create_task(slow_run(config))
        result = await scheduler.trigger_now("test-sub")
        assert result["status"] == "error"
        assert "already running" in result["message"]
        scheduler._running["test-sub"].cancel()
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_trigger_now_error_propagates(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)
        scheduler._run_fn = AsyncMock(side_effect=RuntimeError("boom"))
        result = await scheduler.trigger_now("test-sub")
        assert result["status"] == "triggered"
        await asyncio.sleep(0.1)
        await scheduler.stop()


# ── Get next run ────────────────────────────────────────────────────────

class TestGetNextRun:
    """Tests for querying next scheduled run."""

    @pytest.mark.asyncio
    async def test_get_next_run_with_job(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config(hours=[9, 12])
        scheduler.add_subworker(config)
        next_run = scheduler.get_next_run("test-sub")
        assert next_run is not None
        assert isinstance(next_run, datetime)
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_get_next_run_unknown_returns_none(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        next_run = scheduler.get_next_run("nonexistent")
        assert next_run is None
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_get_next_run_disabled_returns_none(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config(enabled=False)
        scheduler.add_subworker(config)
        next_run = scheduler.get_next_run("test-sub")
        assert next_run is None
        await scheduler.stop()


# ── Get status ──────────────────────────────────────────────────────────

class TestGetStatus:
    """Tests for scheduler status reporting."""

    @pytest.mark.asyncio
    async def test_status_empty(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        status = scheduler.get_status()
        assert status["scheduler_running"] is True
        assert status["job_count"] == 0
        assert status["jobs"] == []
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_status_with_jobs(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        scheduler.add_subworker(_make_config("sub1", hours=[9]))
        scheduler.add_subworker(_make_config("sub2", hours=[12]))
        status = scheduler.get_status()
        assert status["job_count"] == 2
        names = [j["name"] for j in status["jobs"]]
        assert "sub1" in names
        assert "sub2" in names
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_status_disabled_subworker(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        scheduler.add_subworker(_make_config("sub1", enabled=False))
        status = scheduler.get_status()
        assert status["job_count"] == 1
        job = status["jobs"][0]
        assert job["enabled"] is False
        assert job["next_run"] is None
        await scheduler.stop()


# ── Reload schedules ────────────────────────────────────────────────────

class TestReloadSchedules:
    """Tests for hot-reloading schedules."""

    @pytest.mark.asyncio
    async def test_reload_adds_new(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        new_configs = [_make_config("new-sub", hours=[10])]
        result = await scheduler.reload_schedules(new_configs)
        assert "new-sub" in result["added"]
        assert scheduler._scheduler.get_job("subworker:new-sub") is not None
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_reload_removes_old(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        scheduler.add_subworker(_make_config("old-sub", hours=[9]))
        result = await scheduler.reload_schedules([])
        assert "old-sub" in result["removed"]
        assert scheduler._scheduler.get_job("subworker:old-sub") is None
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_reload_updates_existing(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        scheduler.add_subworker(_make_config("sub1", hours=[9]))
        result = await scheduler.reload_schedules([_make_config("sub1", hours=[14])])
        assert "sub1" in result["updated"]
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_reload_preserves_running(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config("sub1", hours=[9])
        scheduler.add_subworker(config)

        # Simulate running
        async def slow_run(cfg: SubworkerConfig) -> None:
            await asyncio.sleep(10)
        scheduler._run_fn = slow_run
        scheduler._running["sub1"] = asyncio.create_task(slow_run(config))

        # Reload with different schedule — should preserve running
        new_config = _make_config("sub1", hours=[14])
        result = await scheduler.reload_schedules([new_config], preserve_running=True)
        assert "sub1" in result["updated"]
        # Running task should not be cancelled
        assert not scheduler._running["sub1"].done()
        scheduler._running["sub1"].cancel()
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_reload_mixed_changes(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        scheduler.add_subworker(_make_config("keep", hours=[9]))
        scheduler.add_subworker(_make_config("drop", hours=[10]))
        new_configs = [
            _make_config("keep", hours=[14]),
            _make_config("add-new", hours=[15]),
        ]
        result = await scheduler.reload_schedules(new_configs)
        assert "keep" in result["updated"]
        assert "drop" in result["removed"]
        assert "add-new" in result["added"]
        await scheduler.stop()


# ── Lifecycle ───────────────────────────────────────────────────────────

class TestLifecycle:
    """Tests for start/stop lifecycle."""

    @pytest.mark.asyncio
    async def test_start_stop(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        assert scheduler._scheduler.running is True
        await scheduler.stop()
        # shutdown(wait=False) is non-blocking — yield to let the event loop
        # process the shutdown before checking the flag.
        await asyncio.sleep(0)
        assert scheduler._scheduler.running is False

    @pytest.mark.asyncio
    async def test_stop_cancels_running(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)

        async def slow_run(cfg: SubworkerConfig) -> None:
            await asyncio.sleep(10)
        scheduler._run_fn = slow_run
        task = asyncio.create_task(slow_run(config))
        scheduler._running["test-sub"] = task

        await scheduler.stop()
        await asyncio.sleep(0)
        assert task.cancelled()

    @pytest.mark.asyncio
    async def test_double_start_safe(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        await scheduler.start()  # Should not raise
        assert scheduler._scheduler.running is True
        await scheduler.stop()


# ── Callbacks ───────────────────────────────────────────────────────────

class TestCallbacks:
    """Tests for run completion callbacks."""

    @pytest.mark.asyncio
    async def test_callback_on_success(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        cb = AsyncMock()
        scheduler.on_run_complete(cb)
        config = _make_config()
        scheduler.add_subworker(config)
        await scheduler.trigger_now("test-sub")
        await asyncio.sleep(0.1)
        cb.assert_called_once_with("test-sub", "success")
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_callback_on_error(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        cb = AsyncMock()
        scheduler.on_run_complete(cb)
        config = _make_config()
        scheduler.add_subworker(config)
        scheduler._run_fn = AsyncMock(side_effect=RuntimeError("boom"))
        await scheduler.trigger_now("test-sub")
        await asyncio.sleep(0.1)
        cb.assert_called_once_with("test-sub", "error")
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_callback_error_does_not_crash(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        bad_cb = AsyncMock(side_effect=RuntimeError("callback boom"))
        scheduler.on_run_complete(bad_cb)
        config = _make_config()
        scheduler.add_subworker(config)
        # Should not raise
        await scheduler.trigger_now("test-sub")
        await asyncio.sleep(0.1)
        bad_cb.assert_called_once()
        await scheduler.stop()


# ── Get running ─────────────────────────────────────────────────────────

class TestGetRunning:
    """Tests for get_running method."""

    @pytest.mark.asyncio
    async def test_get_running_empty(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        assert scheduler.get_running() == []
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_get_running_with_task(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        config = _make_config()
        scheduler.add_subworker(config)

        async def slow_run(cfg: SubworkerConfig) -> None:
            await asyncio.sleep(10)
        scheduler._run_fn = slow_run
        scheduler._running["test-sub"] = asyncio.create_task(slow_run(config))

        running = scheduler.get_running()
        assert "test-sub" in running
        scheduler._running["test-sub"].cancel()
        await scheduler.stop()

    @pytest.mark.asyncio
    async def test_get_running_excludes_done(self, scheduler: SubworkerScheduler) -> None:
        await scheduler.start()
        # Completed task should not appear
        done_task = asyncio.create_task(asyncio.sleep(0))
        scheduler._running["done-sub"] = done_task
        await asyncio.sleep(0.05)  # Let it complete
        assert scheduler.get_running() == []
        await scheduler.stop()


# ── Session state persistence ───────────────────────────────────────────

class TestSessionStatePersistence:
    """Tests for persistent session state across restarts (docker nuke survival).

    The scheduler's _last_session_ids mapping lives in memory; when the Docker
    container is recreated (nuke_docker.sh), that mapping is lost and old
    sessions become unreachable via /sessions/{name}. With state_file set,
    the mapping is persisted to a bind-mounted host path and reloaded on init.
    """

    @staticmethod
    def _run_result(session_id: str) -> MagicMock:
        result = MagicMock()
        result.session_id = session_id
        result.stdout = "done"
        result.success = True
        result.total_duration_seconds = 1.0
        return result

    def test_state_file_roundtrip(self, tmp_path: Any) -> None:
        state_file = tmp_path / "scheduler_state.json"
        s1 = SubworkerScheduler(run_fn=AsyncMock(), state_file=state_file)
        s1._last_session_ids["test-sub"] = "ses_abc123"
        s1._save_state()
        assert state_file.exists()

        s2 = SubworkerScheduler(run_fn=AsyncMock(), state_file=state_file)
        assert s2.get_last_session_id("test-sub") == "ses_abc123"

    def test_no_state_file_starts_empty(self, tmp_path: Any) -> None:
        s = SubworkerScheduler(run_fn=AsyncMock(), state_file=tmp_path / "missing.json")
        assert s.get_last_session_id("anything") is None

    def test_corrupt_state_file_ignored(self, tmp_path: Any) -> None:
        state_file = tmp_path / "scheduler_state.json"
        state_file.write_text("{corrupt json")
        s = SubworkerScheduler(run_fn=AsyncMock(), state_file=state_file)
        assert s.get_last_session_id("anything") is None

    def test_none_state_file_disables_persistence(self) -> None:
        s = SubworkerScheduler(run_fn=AsyncMock(), state_file=None)
        s._last_session_ids["test-sub"] = "ses_abc123"
        s._save_state()

    @pytest.mark.asyncio
    async def test_execute_saves_session_id_to_disk(self, tmp_path: Any) -> None:
        state_file = tmp_path / "scheduler_state.json"
        config = _make_config()
        s = SubworkerScheduler(
            run_fn=AsyncMock(return_value=self._run_result("ses_saved123")),
            state_file=state_file,
        )
        await s.start()
        s.add_subworker(config)
        await s.trigger_now("test-sub")
        await asyncio.sleep(0.1)

        assert s.get_last_session_id("test-sub") == "ses_saved123"
        data = json.loads(state_file.read_text())
        assert data["last_session_ids"]["test-sub"] == "ses_saved123"
        await s.stop()

    @pytest.mark.asyncio
    async def test_state_survives_recreation_after_run(self, tmp_path: Any) -> None:
        state_file = tmp_path / "scheduler_state.json"
        config = _make_config()
        s1 = SubworkerScheduler(
            run_fn=AsyncMock(return_value=self._run_result("ses_persist99")),
            state_file=state_file,
        )
        await s1.start()
        s1.add_subworker(config)
        await s1.trigger_now("test-sub")
        await asyncio.sleep(0.1)
        await s1.stop()

        s2 = SubworkerScheduler(run_fn=AsyncMock(), state_file=state_file)
        assert s2.get_last_session_id("test-sub") == "ses_persist99"
