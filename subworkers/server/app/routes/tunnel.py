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


# ── Endpoints ───────────────────────────────────────────────────────────

@router.get("/status", response_model=TunnelStatusResponse)
async def get_tunnel_status() -> TunnelStatusResponse:
    data = await _manager.status()
    return TunnelStatusResponse(**data)


@router.post("/check", response_model=TunnelCheckResponse)
async def check_tunnel(req: TunnelCheckRequest) -> TunnelCheckResponse:
    """Validate token + zone without creating anything.

    Accepts either Bearer or Global (global_key + email auto-mints).
    """
    try:
        # Use Global flow if provided
        effective_token = (req.api_token or "").strip()
        if req.global_key and req.global_key.strip().startswith("cfk_"):
            effective_token = await _manager.create_restricted_token_via_global(req.global_key.strip(), (req.email or "").strip(), req.domain)
        elif effective_token.startswith("cfk_") and req.email:
            effective_token = await _manager.create_restricted_token_via_global(effective_token, req.email.strip(), req.domain)
        account = await _manager.verify_token(effective_token)
        zone = await _manager.check_zone(effective_token, req.domain)
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
    """Kick off the full setup as a background task; poll GET /tunnel/status for progress.

    Accepts either a restricted Bearer token (api_token) or a Global API Key
    (global_key + email) which will be used to auto-mint the correct restricted
    token (Zone DNS Write + Tunnel Write) via the Cloudflare API.
    """
    if _manager.is_setup_running:
        return {"status": "already_running", "step": _manager.step, "message": "A setup is already running — poll GET /tunnel/status."}
    try:
        domain = req.domain.strip().lower()
        if not domain or "." not in domain:
            return {"status": "error", "message": "Invalid domain."}
        # Resolve the effective Bearer token: prefer explicit api_token, fallback to auto-minted via Global
        effective_token = (req.api_token or "").strip()
        global_key = (req.global_key or "").strip()
        email = (req.email or "").strip()
        # If api_token looks like a Global key (cfk_ or 37 hex) and email was pasted into same field by mistake, handle it
        if not effective_token and global_key:
            effective_token = ""
        # Auto-mint from Global if provided (or if api_token is a cfk_ Global)
        is_global = global_key.startswith("cfk_") or effective_token.startswith("cfk_")
        if is_global:
            gkey = global_key if global_key.startswith("cfk_") else effective_token
            gemail = email or (req.api_token or "")
            # If user pasted "email + global" into one field, try to split
            if "@" in gkey and "cfk_" in gkey:
                # shouldn't happen
                pass
            if not gemail or "@" not in gemail:
                # Try to find email in UserDefaults fallback or error
                return {"status": "error", "message": "Global API Key requires your Cloudflare email (wael.bousfira@gmail.com). Please fill the Email field."}
            # Mint restricted Bearer via Global
            try:
                effective_token = await _manager.create_restricted_token_via_global(gkey, gemail, domain)
            except TunnelError as exc:
                return {"status": "error", "message": f"Could not create restricted token from Global API Key: {exc}", "step": _manager.step}
        if not effective_token:
            return {"status": "error", "message": "Missing API token or Global API Key."}
        _manager.start_setup(domain, effective_token)
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
