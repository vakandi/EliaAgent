"""WebSocket endpoint for real-time status streaming — mirrors live ws route.

Provides /ws: on connect sends a current status snapshot, then streams
run_update / main_agent broadcasts. Auth via ?token= or upgrade headers.
"""
from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth import ws_require_token

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, event: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def broadcast_run_log(self, name: str, text: str, field: str = "text") -> None:
        """Stream incremental agent output (live run_log shape; TopBar-owned)."""
        await self.broadcast({"event": "run_log", "name": name, "text": text, "field": field})

    async def broadcast_run_banner(self, name: str, banner: dict[str, Any]) -> None:
        """Stream a system banner (live run_banner shape; TopBar-owned)."""
        await self.broadcast({"event": "run_banner", "name": name, "banner": banner})


ws_manager = ConnectionManager()


def reset_manager() -> None:
    """Reset the singleton ConnectionManager (for testing)."""
    global ws_manager
    ws_manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """WebSocket endpoint for real-time subworker status updates."""
    if not await ws_require_token(ws):
        return
    await ws_manager.connect(ws)
    try:
        # TopBar populates its client state from this (live sends the same
        # event on connect; without it the UI stays blank). Lazy import:
        # subworkers.py imports ws_manager from here, so top-level import
        # would be circular.
        from app.routers import subworkers as _sw
        _cfg = _sw._load_config()
        _running = {r.name for r in _sw._runs.values() if r.status == "running"}
        await ws.send_json({
            "event": "initial_status",
            "scheduler_running": True,
            "total": len(_cfg.get("subworkers", [])),
            "opencode_health": "healthy",
            "subworkers": [
                {
                    "name": e.get("name"),
                    "enabled": _sw._is_enabled(e),
                    "running": e.get("name") in _running,
                    "next_run": None,
                    "schedule_type": (e.get("schedule") or {}).get("type") if isinstance(e.get("schedule"), dict) else e.get("schedule"),
                    "model": e.get("model"),
                    "variant": e.get("variant"),
                }
                for e in _cfg.get("subworkers", [])
            ],
        })
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)


async def broadcast_event(event: dict[str, Any]) -> None:
    """Broadcast a subworker event to all connected WebSocket clients."""
    await ws_manager.broadcast(event)
