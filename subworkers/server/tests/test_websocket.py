"""Tests for WebSocket endpoint (ConnectionManager + /ws)."""
from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from app.routes.websocket import ConnectionManager, broadcast_event, ws_manager


# ── Fixtures ────────────────────────────────────────────────────────────────


def _make_ws() -> MagicMock:
    """Create a mock WebSocket that behaves like a real one for testing."""
    ws = AsyncMock()
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    return ws


@pytest_asyncio.fixture
async def manager():
    """Fresh ConnectionManager for each test (reset singleton)."""
    from app.routes.websocket import reset_manager
    reset_manager()
    mgr = ConnectionManager()
    yield mgr
    # Cleanup
    mgr._connections.clear()


# ── ConnectionManager tests ─────────────────────────────────────────────


class TestConnect:
    @pytest.mark.asyncio
    async def test_connect_adds_client(self, manager: ConnectionManager):
        ws = _make_ws()
        await manager.connect(ws)
        assert manager.count == 1
        ws.accept.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_connect_multiple_clients(self, manager: ConnectionManager):
        ws1, ws2, ws3 = _make_ws(), _make_ws(), _make_ws()
        await manager.connect(ws1)
        await manager.connect(ws2)
        await manager.connect(ws3)
        assert manager.count == 3

    @pytest.mark.asyncio
    async def test_connect_accept_called(self, manager: ConnectionManager):
        ws = _make_ws()
        await manager.connect(ws)
        ws.accept.assert_awaited_once()


class TestDisconnect:
    @pytest.mark.asyncio
    async def test_disconnect_removes_client(self, manager: ConnectionManager):
        ws = _make_ws()
        await manager.connect(ws)
        assert manager.count == 1
        manager.disconnect(ws)
        assert manager.count == 0

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_safe(self, manager: ConnectionManager):
        ws = _make_ws()
        # Should not raise
        manager.disconnect(ws)
        assert manager.count == 0

    @pytest.mark.asyncio
    async def test_disconnect_only_removes_target(self, manager: ConnectionManager):
        ws1, ws2 = _make_ws(), _make_ws()
        await manager.connect(ws1)
        await manager.connect(ws2)
        manager.disconnect(ws1)
        assert manager.count == 1


class TestBroadcast:
    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all(self, manager: ConnectionManager):
        ws1, ws2 = _make_ws(), _make_ws()
        await manager.connect(ws1)
        await manager.connect(ws2)

        event = {"event": "subworker_success", "name": "alpha"}
        await manager.broadcast(event)

        payload = json.dumps(event)
        ws1.send_text.assert_awaited_once_with(payload)
        ws2.send_text.assert_awaited_once_with(payload)

    @pytest.mark.asyncio
    async def test_broadcast_removes_dead_connections(self, manager: ConnectionManager):
        ws_live = _make_ws()
        ws_dead = _make_ws()
        ws_dead.send_text.side_effect = ConnectionError("broken pipe")

        await manager.connect(ws_live)
        await manager.connect(ws_dead)

        await manager.broadcast({"event": "test"})

        # Dead connection removed, live one kept
        assert manager.count == 1
        assert ws_live in manager._connections

    @pytest.mark.asyncio
    async def test_broadcast_empty_no_crash(self, manager: ConnectionManager):
        # Broadcasting with no clients should not raise
        await manager.broadcast({"event": "test"})


# ── broadcast_event helper tests ────────────────────────────────────────


class TestBroadcastEvent:
    @pytest.mark.asyncio
    async def test_broadcast_event_sends_event(self, manager: ConnectionManager):
        from app.routes import websocket as ws_mod
        ws_mod.ws_manager = manager

        ws = _make_ws()
        await manager.connect(ws)

        await broadcast_event("subworker_success", "beta")

        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["event"] == "subworker_success"
        assert sent["name"] == "beta"
        assert "status" not in sent

    @pytest.mark.asyncio
    async def test_broadcast_event_with_status(self, manager: ConnectionManager):
        from app.routes import websocket as ws_mod
        ws_mod.ws_manager = manager

        ws = _make_ws()
        await manager.connect(ws)

        status = {"duration_ms": 1200, "exit_code": 0}
        await broadcast_event("subworker_error", "gamma", status=status)

        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["event"] == "subworker_error"
        assert sent["name"] == "gamma"
        assert sent["status"] == status


# ── ConnectionManager callback wiring tests ─────────────────────────────


class TestSchedulerCallback:
    @pytest.mark.asyncio
    async def test_as_callback_fires_broadcast(self, manager: ConnectionManager):
        """Verify the callback returned by as_callback() broadcasts correctly."""
        from app.routes import websocket as ws_mod
        ws_mod.ws_manager = manager

        ws = _make_ws()
        await manager.connect(ws)

        callback = manager.as_callback()
        await callback("delta", "success")

        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["event"] == "subworker_success"
        assert sent["name"] == "delta"

    @pytest.mark.asyncio
    async def test_as_callback_error_status(self, manager: ConnectionManager):
        from app.routes import websocket as ws_mod
        ws_mod.ws_manager = manager

        ws = _make_ws()
        await manager.connect(ws)

        callback = manager.as_callback()
        await callback("epsilon", "error")

        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["event"] == "subworker_error"
        assert sent["name"] == "epsilon"


# ── WebSocket endpoint integration test ─────────────────────────────────


@pytest.mark.asyncio
async def test_ws_endpoint_initial_status():
    """Integration test: connect via WebSocket, receive initial status snapshot."""
    import app.main as main_mod

    # Set up mocks
    mock_config = MagicMock()
    alpha = MagicMock()
    alpha.name = "alpha"
    alpha.enabled = True
    alpha.workspace = None
    alpha.schedule.type.value = "interval"
    mock_config.subworkers = [alpha]

    mock_scheduler = MagicMock()
    mock_scheduler.get_status.return_value = {"scheduler_running": True, "job_count": 1, "jobs": []}
    mock_scheduler.get_running.return_value = []
    mock_scheduler.get_next_run.return_value = None

    main_mod._config_manager = mock_config
    main_mod._scheduler = mock_scheduler

    # Use FastAPI test client for WebSocket
    from starlette.testclient import TestClient

    client = TestClient(main_mod.app)
    with client.websocket_connect("/ws") as ws:
        data = json.loads(ws.receive_text())
        assert data["event"] == "initial_status"
        assert data["scheduler_running"] is True
        assert data["total"] == 1
        assert data["subworkers"][0]["name"] == "alpha"
        assert data["subworkers"][0]["enabled"] is True
        assert data["subworkers"][0]["running"] is False
