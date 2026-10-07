"""Cloudflare Tunnel remote-access API — same paths and shapes as live.

GET  /tunnel/status
POST /tunnel/check   {domain, api_token} — validate without creating
POST /tunnel/setup   {domain, api_token} — full orchestration (background)
POST /tunnel/stop
POST /tunnel/remove
"""
from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.qwen_tunnel import QwenTunnelManager, TunnelError

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/tunnel", tags=["tunnel"])


def _manager() -> QwenTunnelManager:
    return QwenTunnelManager(config_dir=get_settings().CONFIG_DIR)


class TunnelCheckRequest(BaseModel):
    domain: str = Field(..., description="Public hostname, e.g. elia.example.com")
    api_token: str | None = Field(default=None, description="Cloudflare API token (Zone:DNS:Edit + Account:Tunnel:Edit)")
    global_key: str | None = None
    email: str | None = None


class TunnelSetupRequest(BaseModel):
    domain: str
    api_token: str | None = None
    global_key: str | None = None
    email: str | None = None


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


@router.get("/status", response_model=TunnelStatusResponse)
async def get_tunnel_status() -> TunnelStatusResponse:
    return TunnelStatusResponse(**await _manager().status())


@router.post("/check", response_model=TunnelCheckResponse)
async def check_tunnel(req: TunnelCheckRequest) -> TunnelCheckResponse:
    """Validate token + zone without creating anything."""
    try:
        effective_token = (req.api_token or "").strip()
        if not effective_token:
            return TunnelCheckResponse(token_ok=False, message="Missing API token.")
        manager = _manager()
        account = await manager.verify_token(effective_token)
        zone = await manager.check_zone(effective_token, req.domain.strip().lower())
        return TunnelCheckResponse(
            token_ok=True,
            account_id=account.get("account_id") or zone.get("account_id"),
            account_name=account.get("account_name") or zone.get("account_name"),
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
    """Kick off the full setup as a background task; poll GET /tunnel/status."""
    manager = _manager()
    if manager.is_setup_running:
        return {"status": "already_running", "step": manager.step,
                "message": "A setup is already running — poll GET /tunnel/status."}
    domain = req.domain.strip().lower()
    if not domain or "." not in domain:
        return {"status": "error", "message": "Invalid domain."}
    effective_token = (req.api_token or "").strip()
    if not effective_token:
        return {"status": "error", "message": "Missing API token (Global-key minting lives in the live stack; use a restricted Bearer here)."}
    manager.start_setup(domain, effective_token)
    return {"status": "started", "step": manager.step, "domain": domain}


@router.post("/stop")
async def stop_tunnel() -> dict[str, Any]:
    try:
        await _manager().stop()
        return {"status": "stopped"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.post("/remove")
async def remove_tunnel() -> dict[str, Any]:
    try:
        result = await _manager().remove()
        return {"status": "removed", **result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
