"""OpenCode server management API endpoints.

Provides health check and restart for the OpenCode subprocess.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/server", tags=["server"])


# ── Response Models ────────────────────────────────────────────────────────

class ServerHealthResponse(BaseModel):
    state: str
    health_status: str
    pid: int | None = None
    base_url: str | None = None
    restart_count: int
    last_health_check: dict[str, Any] | None = None


class RestartResponse(BaseModel):
    status: str
    message: str
    state: str


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_health_manager():
    """Import and return the health manager from app state."""
    from app.main import get_health_manager
    return get_health_manager()


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/health", response_model=ServerHealthResponse)
async def get_server_health() -> ServerHealthResponse:
    """Return the current health of the OpenCode server subprocess."""
    health = _get_health_manager()

    return ServerHealthResponse(
        state=health.state.value,
        health_status=health.health_status.value,
        pid=health.pid,
        base_url=health.base_url,
        restart_count=health.restart_count,
        last_health_check=health.last_health_check,
    )


@router.post("/restart", response_model=RestartResponse)
async def restart_server() -> RestartResponse:
    """Restart the OpenCode server subprocess."""
    health = _get_health_manager()

    try:
        await health.restart()
        return RestartResponse(
            status="restarted",
            message="OpenCode server restarted successfully",
            state=health.state.value,
        )
    except RuntimeError as exc:
        return RestartResponse(
            status="error",
            message=str(exc),
            state=health.state.value,
        )
