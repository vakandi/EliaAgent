"""WebSocket endpoint for real-time status streaming to Electron UI.

Provides /ws endpoint that broadcasts subworker state changes to all
connected clients. On connect, sends current status snapshot.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["websocket"])


# ── Connection Manager ──────────────────────────────────────────────────────

class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []
        self._status_provider: Any = None

    def set_status_provider(self, provider: Any) -> None:
        """Register a callable returning the full subworker status list."""
        self._status_provider = provider

    @property
    def count(self) -> int:
        return len(self._connections)

    async def connect(self, ws: WebSocket) -> None:
        """Accept a new WebSocket connection and track it."""
        await ws.accept()
        self._connections.append(ws)
        logger.info("ws.connected total=%d", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        """Remove a disconnected WebSocket from tracking."""
        if ws in self._connections:
            self._connections.remove(ws)
        logger.info("ws.disconnected total=%d", len(self._connections))

    def as_callback(self):
        """Return an async callable(name, status) for scheduler on_run_complete."""
        return self._on_run_complete

    def as_start_callback(self):
        """Return an async callable(name) for scheduler on_run_start."""
        return self._on_run_start

    async def _on_run_start(self, name: str) -> None:
        """Scheduler callback — broadcasts run start so clients can show live state."""
        await self.broadcast({"event": "subworker_started", "name": name})
        await self.broadcast_status_update()
        logger.info("ws.broadcast event=subworker_started name=%s", name)

    async def _on_run_complete(self, name: str, status: str) -> None:
        """Scheduler callback — broadcasts subworker completion to all clients."""
        await self.broadcast({"event": f"subworker_{status}", "name": name})
        await self.broadcast_status_update()
        logger.info("ws.broadcast event=subworker_%s name=%s", status, name)

    async def broadcast_status_update(self) -> None:
        """Push a full status snapshot so clients drop their HTTP polling."""
        if not self._status_provider:
            return
        try:
            subs = self._status_provider()
            if subs is not None:
                await self.broadcast({"event": "status_update", "subworkers": subs})
        except Exception as exc:
            logger.warning("ws.status_update_failed error=%s", exc)

    async def broadcast_run_log(self, name: str, text: str) -> None:
        """Stream incremental agent output to clients (hover log popovers)."""
        await self.broadcast({"event": "run_log", "name": name, "text": text})

    async def broadcast(self, event: dict[str, Any]) -> None:
        """Send a JSON event to all connected clients.

        Removes clients that fail to receive the message.
        """
        message = json.dumps(event)
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    def get_status_snapshot(self) -> dict[str, Any]:
        """Build a snapshot of all subworker statuses.

        Imports lazily to avoid circular dependencies.
        """
        from app.main import get_config_manager, get_health_manager, get_scheduler

        config = get_config_manager()
        scheduler = get_scheduler()
        health = get_health_manager()

        scheduler_status = scheduler.get_status()
        running_names = set(scheduler.get_running())

        subworkers = []
        for sw in config.subworkers:
            next_run = scheduler.get_next_run(sw.name)
            subworkers.append({
                "name": sw.name,
                "enabled": sw.enabled,
                "running": sw.name in running_names,
                "next_run": next_run.isoformat() if next_run else None,
                "schedule_type": sw.schedule.type.value if sw.schedule else None,
                "model": sw.model,
                "variant": sw.variant,
            })

        return {
            "event": "initial_status",
            "scheduler_running": scheduler_status["scheduler_running"],
            "total": len(subworkers),
            "opencode_health": health.health_status.value if health else "unknown",
            "subworkers": subworkers,
        }


# ── Module-level singleton ──────────────────────────────────────────────────

ws_manager = ConnectionManager()


def reset_manager() -> None:
    """Reset the singleton ConnectionManager (for testing)."""
    global ws_manager
    ws_manager = ConnectionManager()


# ── WebSocket Endpoint ──────────────────────────────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """WebSocket endpoint for real-time subworker status updates.

    On connect: sends current status of all subworkers.
    On state change: broadcasts event to all connected clients.
    On disconnect: cleans up connection gracefully.
    """
    from app.core.auth import ws_require_token

    if not await ws_require_token(ws):
        return
    await ws_manager.connect(ws)
    try:
        # ── Send initial status snapshot ──
        snapshot = ws_manager.get_status_snapshot()
        await ws.send_text(json.dumps(snapshot))

        # ── Keep connection alive, listen for client messages ──
        while True:
            # Wait for messages from client (ping/pong, commands, etc.)
            data = await ws.receive_text()
            # Currently we only handle ping from clients
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws.send_text(json.dumps({"event": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception as exc:
        logger.error("ws.error error=%s", str(exc))
        ws_manager.disconnect(ws)


# ── Broadcast Helper ────────────────────────────────────────────────────────

async def broadcast_event(
    event_type: str,
    name: str,
    status: dict[str, Any] | None = None,
) -> None:
    """Broadcast a subworker event to all connected WebSocket clients.

    Called by the scheduler callback when a subworker starts, completes, or errors.
    """
    event: dict[str, Any] = {
        "event": event_type,
        "name": name,
    }
    if status:
        event["status"] = status
    await ws_manager.broadcast(event)
