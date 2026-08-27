"""Cloudflare Tunnel remote-access API (PLAN.md §9.1 — Unit L).

Only reachable when the phone is on the local network (the trigger condition).
After setup the server is reachable everywhere via the custom domain.

Endpoints
    GET  /tunnel/status
    POST /tunnel/check   {domain, api_token}  — validate without creating
    POST /tunnel/setup   {domain, api_token}  — full orchestration (background)
    POST /tunnel/stop
    POST /tunnel/remove
"""
from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.tunnel_manager import TunnelError, TunnelManager

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/tunnel", tags=["tunnel"])

_manager = TunnelManager()


# ── Models ────────────────────────────────────────────────────────────────

class TunnelCheckRequest(BaseModel):
    domain: str = Field(..., description="Public hostname, e.g. elia.surfai.tech")
    api_token: str = Field(..., description="Cloudflare API token (Zone:DNS:Edit + Account:Tunnel:Edit)")


class TunnelSetupRequest(BaseModel):
    domain: str
    api_token: str


class TunnelStatusResponse(BaseModel):
    configured: bool
    domain: str | None
    tunnel_id: str | None
    cloudflared_running: bool
    public_ok: bool
    last_error: str | None
    step: str
    api_token_masked: str | None = None
    tunnel_token_masked: str | None = None


class TunnelCheckResponse(BaseModel):
    token_ok: bool
    account_id: str | None = None
    account_name: str | None = None
    zone_id: str | None = None
    zone_name: str | None = None
    message: str


# ── Endpoints ───────────────────────────────────────────────────────────

@router.get("/status", response_model=TunnelStatusResponse)
async def get_tunnel_status() -> TunnelStatusResponse:
    data = await _manager.status()
    return TunnelStatusResponse(**data)


@router.post("/check", response_model=TunnelCheckResponse)
async def check_tunnel(req: TunnelCheckRequest) -> TunnelCheckResponse:
    """Validate token + zone without creating anything."""
    try:
        account = await _manager.verify_token(req.api_token)
        zone = await _manager.check_zone(req.api_token, req.domain)
        return TunnelCheckResponse(
            token_ok=True,
            account_id=account.get("account_id"),
            account_name=account.get("account_name"),
            zone_id=zone.get("zone_id"),
            zone_name=zone.get("zone_name"),
            message="Token and zone verified — ready to create the tunnel.",
        )
    except TunnelError as exc:
        return TunnelCheckResponse(token_ok=False, message=str(exc))
    except Exception as exc:  # pragma: no cover
        log.error("tunnel.check_failed", error=str(exc))
        return TunnelCheckResponse(token_ok=False, message=str(exc))


@router.post("/setup")
async def setup_tunnel(req: TunnelSetupRequest) -> dict[str, Any]:
    """Kick off the full setup as a background task; poll GET /tunnel/status for progress."""
    if _manager.is_setup_running:
        return {"status": "already_running", "step": _manager.step, "message": "A setup is already running — poll GET /tunnel/status."}
    try:
        domain = req.domain.strip().lower()
        if not domain or "." not in domain:
            return {"status": "error", "message": "Invalid domain."}
        _manager.start_setup(domain, req.api_token)
        return {"status": "started", "step": _manager.step, "domain": domain}
    except TunnelError as exc:
        return {"status": "error", "message": str(exc), "step": _manager.step}
    except Exception as exc:  # pragma: no cover
        log.error("tunnel.setup_start_failed", error=str(exc))
        return {"status": "error", "message": str(exc)}


@router.post("/stop")
async def stop_tunnel() -> dict[str, Any]:
    try:
        await _manager.stop()
        return {"status": "stopped"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.post("/remove")
async def remove_tunnel() -> dict[str, Any]:
    try:
        result = await _manager.remove()
        return {"status": "removed", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
