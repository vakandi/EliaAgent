"""Tests for API routes (subworkers + server endpoints)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config.models import CronSchedule, IntervalSchedule, SubworkerConfig
from app.main import app


# ── Fixtures ────────────────────────────────────────────────────────────────

def _make_sw(name: str = "test-sw", enabled: bool = True, agent_id: str = "test-agent"):
    sw = MagicMock(spec=SubworkerConfig)
    sw.name = name
    sw.enabled = enabled
    sw.agent_id = agent_id
    sw.timeout_minutes = 30
    sw.max_retries = 3
    sw.model = None
    sw.workspace = None
    sw.schedule = IntervalSchedule(hours=[9, 10], minute=0)
    return sw


@pytest_asyncio.fixture
async def client():
    alpha = _make_sw("alpha", enabled=True)
    beta = _make_sw("beta", enabled=False)

    mock_config = MagicMock()
    mock_config.subworkers = [alpha, beta]
    mock_config.get_subworker.side_effect = lambda name: {
        "alpha": alpha, "beta": beta,
    }.get(name)
    def _update_sw(name: str, updates: dict) -> MagicMock:
        sw = _make_sw(name, enabled=updates.get("enabled", True))
        if "agent_id" in updates:
            sw.agent_id = updates["agent_id"]
        if "model" in updates:
            sw.model = updates["model"]
        if "timeout_minutes" in updates:
            sw.timeout_minutes = updates["timeout_minutes"]
        if "max_retries" in updates:
            sw.max_retries = updates["max_retries"]
        if "schedule" in updates:
            sw.schedule = updates["schedule"]
        return sw

    mock_config.update_subworker.side_effect = _update_sw

    mock_scheduler = MagicMock()
    mock_scheduler.get_status.return_value = {"scheduler_running": True, "job_count": 2, "jobs": []}
    mock_scheduler.get_running.return_value = []
    mock_scheduler.get_next_run.return_value = None
    mock_scheduler.trigger_now = AsyncMock(return_value={"status": "triggered", "name": "alpha"})
    mock_scheduler.add_subworker = MagicMock()
    mock_scheduler.reload_schedules = AsyncMock()

    mock_health = MagicMock()
    type(mock_health).state = MagicMock(value="running")
    type(mock_health).health_status = MagicMock(value="healthy")
    type(mock_health).pid = 12345
    type(mock_health).base_url = "http://127.0.0.1:5655"
    type(mock_health).restart_count = 0
    type(mock_health).last_health_check = None
    mock_health.restart = AsyncMock()

    import app.main as main_mod
    main_mod._config_manager = mock_config
    main_mod._scheduler = mock_scheduler
    main_mod._health_manager = mock_health

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_config, mock_scheduler, mock_health


# ── GET /health ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint(client):
    ac, *_ = client
    resp = await ac.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "uptime" in data
    assert data["version"] == "0.1.0"


# ── GET /status ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_status(client):
    ac, _, mock_sched, _ = client
    resp = await ac.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["scheduler_running"] is True
    assert data["total"] == 2
    names = {sw["name"] for sw in data["subworkers"]}
    assert names == {"alpha", "beta"}


@pytest.mark.asyncio
async def test_get_all_status_shows_enabled(client):
    ac, *_ = client
    resp = await ac.get("/status")
    subworkers = resp.json()["subworkers"]
    alpha = next(sw for sw in subworkers if sw["name"] == "alpha")
    beta = next(sw for sw in subworkers if sw["name"] == "beta")
    assert alpha["enabled"] is True
    assert beta["enabled"] is False


@pytest.mark.asyncio
async def test_get_all_status_schedule_type(client):
    ac, *_ = client
    resp = await ac.get("/status")
    for sw in resp.json()["subworkers"]:
        assert sw["schedule_type"] == "interval"


# ── GET /status/{name} ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_subworker_detail(client):
    ac, *_ = client
    resp = await ac.get("/status/alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "alpha"
    assert data["enabled"] is True
    assert data["agent_id"] == "test-agent"
    assert data["timeout_minutes"] == 30
    assert data["max_retries"] == 3
    assert "schedule" in data


@pytest.mark.asyncio
async def test_get_subworker_detail_not_found(client):
    ac, *_ = client
    resp = await ac.get("/status/nonexistent")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_subworker_detail_shows_disabled(client):
    ac, *_ = client
    resp = await ac.get("/status/beta")
    assert resp.status_code == 200
    assert resp.json()["enabled"] is False


# ── POST /trigger/{name} ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_trigger_success(client):
    ac, _, mock_sched, _ = client
    resp = await ac.post("/trigger/alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    assert data["name"] == "alpha"
    mock_sched.trigger_now.assert_called_once_with("alpha", prompt=None, model=None)


@pytest.mark.asyncio
async def test_trigger_error(client):
    ac, _, mock_sched, _ = client
    mock_sched.trigger_now.return_value = {"status": "error", "name": "alpha", "message": "already running"}
    resp = await ac.post("/trigger/alpha")
    assert resp.status_code == 200
    assert resp.json()["status"] == "error"
    assert "already running" in resp.json()["message"]


@pytest.mark.asyncio
async def test_trigger_not_found(client):
    ac, *_ = client
    resp = await ac.post("/trigger/nonexistent")
    assert resp.status_code == 404


# ── POST /enable/{name} ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_enable_success(client):
    ac, mock_cfg, mock_sched, _ = client
    resp = await ac.post("/enable/beta")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "enabled"
    assert data["enabled"] is True
    mock_cfg.update_subworker.assert_called_once_with("beta", {"enabled": True})
    mock_sched.add_subworker.assert_called_once()


@pytest.mark.asyncio
async def test_enable_already_enabled(client):
    ac, mock_cfg, _, _ = client
    resp = await ac.post("/enable/alpha")
    assert resp.status_code == 200
    assert resp.json()["status"] == "already_enabled"
    mock_cfg.update_subworker.assert_not_called()


@pytest.mark.asyncio
async def test_enable_not_found(client):
    ac, *_ = client
    resp = await ac.post("/enable/nonexistent")
    assert resp.status_code == 404


# ── POST /disable/{name} ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_disable_success(client):
    ac, mock_cfg, mock_sched, _ = client
    resp = await ac.post("/disable/alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "disabled"
    assert data["enabled"] is False
    mock_cfg.update_subworker.assert_called_once_with("alpha", {"enabled": False})
    mock_sched.add_subworker.assert_called_once()


@pytest.mark.asyncio
async def test_disable_already_disabled(client):
    ac, mock_cfg, _, _ = client
    resp = await ac.post("/disable/beta")
    assert resp.status_code == 200
    assert resp.json()["status"] == "already_disabled"
    mock_cfg.update_subworker.assert_not_called()


@pytest.mark.asyncio
async def test_disable_not_found(client):
    ac, *_ = client
    resp = await ac.post("/disable/nonexistent")
    assert resp.status_code == 404


# ── GET /logs/{name} ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_logs_no_log_dir(client):
    ac, *_ = client
    resp = await ac.get("/logs/alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "alpha"
    assert data["log_file"] is None
    assert data["lines"] == []


@pytest.mark.asyncio
async def test_logs_not_found(client):
    ac, *_ = client
    resp = await ac.get("/logs/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_logs_with_log_file(client, tmp_path):
    ac, mock_cfg, _, _ = client
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "run.log"
    log_file.write_text("line1\nline2\nline3\n")

    sw_with_workspace = _make_sw("alpha", enabled=True)
    sw_with_workspace.workspace = str(tmp_path)
    mock_cfg.get_subworker.side_effect = lambda name: {
        "alpha": sw_with_workspace, "beta": _make_sw("beta", enabled=False),
    }.get(name)

    resp = await ac.get("/logs/alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "alpha"
    assert data["log_file"] is not None
    assert data["total_lines"] == 3
    assert len(data["lines"]) == 3


@pytest.mark.asyncio
async def test_logs_lines_limit(client, tmp_path):
    ac, mock_cfg, _, _ = client
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "run.log"
    file_lines = [f"line{i}\n" for i in range(20)]
    log_file.write_text("".join(file_lines))

    sw_with_workspace = _make_sw("alpha", enabled=True)
    sw_with_workspace.workspace = str(tmp_path)
    mock_cfg.get_subworker.side_effect = lambda name: {
        "alpha": sw_with_workspace, "beta": _make_sw("beta", enabled=False),
    }.get(name)

    resp = await ac.get("/logs/alpha?lines=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_lines"] == 20
    assert len(data["lines"]) == 5


@pytest.mark.asyncio
async def test_logs_empty_log_dir(client, tmp_path):
    ac, mock_cfg, _, _ = client
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    sw_with_workspace = _make_sw("alpha", enabled=True)
    sw_with_workspace.workspace = str(tmp_path)
    mock_cfg.get_subworker.side_effect = lambda name: {
        "alpha": sw_with_workspace, "beta": _make_sw("beta", enabled=False),
    }.get(name)

    resp = await ac.get("/logs/alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["log_file"] is None
    assert data["lines"] == []


# ── GET /server/health ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_server_health(client):
    ac, *_ = client
    resp = await ac.get("/server/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"] == "running"
    assert data["health_status"] == "healthy"
    assert data["pid"] == 12345
    assert data["base_url"] == "http://127.0.0.1:5655"
    assert data["restart_count"] == 0


# ── POST /server/restart ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_server_restart_success(client):
    ac, _, _, mock_hm = client
    resp = await ac.post("/server/restart")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "restarted"
    assert data["message"] == "OpenCode server restarted successfully"
    mock_hm.restart.assert_called_once()


@pytest.mark.asyncio
async def test_server_restart_error(client):
    ac, _, _, mock_hm = client
    mock_hm.restart.side_effect = RuntimeError("Process not found")
    resp = await ac.post("/server/restart")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "error"
    assert "Process not found" in data["message"]


# ── PUT /status/{name} ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_subworker_model(client):
    ac, mock_cfg, mock_sched, _ = client
    resp = await ac.put("/status/alpha", json={"model": "big-pickle"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "alpha"
    mock_cfg.update_subworker.assert_called_once()
    mock_sched.add_subworker.assert_called_once()


@pytest.mark.asyncio
async def test_update_subworker_schedule_interval(client):
    ac, mock_cfg, mock_sched, _ = client
    schedule = {"type": "interval", "hours": [10, 12, 14], "minute": 30}
    resp = await ac.put("/status/alpha", json={"schedule": schedule})
    assert resp.status_code == 200
    assert resp.json()["schedule"]["type"] == "interval"
    mock_cfg.update_subworker.assert_called_once()


@pytest.mark.asyncio
async def test_update_subworker_schedule_cron(client):
    ac, mock_cfg, mock_sched, _ = client
    schedule = {"type": "cron", "expression": "0 10-18 * * *"}
    resp = await ac.put("/status/alpha", json={"schedule": schedule})
    assert resp.status_code == 200
    assert resp.json()["schedule"]["type"] == "cron"
    assert resp.json()["schedule"]["expression"] == "0 10-18 * * *"


@pytest.mark.asyncio
async def test_update_subworker_multiple_fields(client):
    ac, mock_cfg, mock_sched, _ = client
    resp = await ac.put("/status/alpha", json={
        "model": "big-pickle",
        "timeout_minutes": 60,
        "max_retries": 5,
    })
    assert resp.status_code == 200
    mock_cfg.update_subworker.assert_called_once()


@pytest.mark.asyncio
async def test_update_subworker_not_found(client):
    ac, *_ = client
    resp = await ac.put("/status/nonexistent", json={"model": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_subworker_empty_body(client):
    ac, *_ = client
    resp = await ac.put("/status/alpha", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_subworker_invalid_schedule_type(client):
    ac, *_ = client
    resp = await ac.put("/status/alpha", json={"schedule": {"type": "invalid"}})
    assert resp.status_code == 422


# ── POST /config/reload ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reload_config(client):
    ac, mock_cfg, _, _ = client
    mock_cfg.reload.return_value = {
        "added": ["new-sw"],
        "removed": [],
        "unchanged": ["alpha", "beta"],
        "total": 3,
    }
    resp = await ac.post("/config/reload")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "reloaded"
    assert data["added"] == ["new-sw"]
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_reload_config_no_changes(client):
    ac, mock_cfg, _, _ = client
    mock_cfg.reload.return_value = {
        "added": [],
        "removed": [],
        "unchanged": ["alpha", "beta"],
        "total": 2,
    }
    resp = await ac.post("/config/reload")
    assert resp.status_code == 200
    assert resp.json()["added"] == []
    assert resp.json()["removed"] == []
