"""Bearer auth for the qwen shim — mirrors server/app/core/auth.py.

- ELIA_AUTH_TOKEN empty/missing disables auth (dev/backward compatible).
- HTTP accepts ``Authorization: Bearer <token>`` OR ``X-Elia-Token``.
- WebSocket accepts ``?token=<token>`` OR the same two upgrade headers.
- ``/health`` stays open for the Docker healthcheck.
"""
from __future__ import annotations

from fastapi import HTTPException, Request, WebSocket, status

from app.config import get_settings

EXEMPT_PATHS = {"/health"}
WS_POLICY_VIOLATION = 1008


def _enabled() -> bool:
    return bool(get_settings().ELIA_AUTH_TOKEN)


def _supplied_token(*candidates: str | None) -> str | None:
    supplied: str | None = None
    for value in candidates:
        if not value:
            continue
        if value.lower().startswith("bearer "):
            value = value[7:].strip()
        supplied = value.strip() or supplied
        if supplied:
            break
    return supplied


async def require_token(request: Request) -> None:
    """HTTP dependency — raises 401 when the token check fails."""
    if not _enabled() or request.url.path in EXEMPT_PATHS:
        return
    supplied = _supplied_token(
        request.headers.get("authorization"),
        request.headers.get("x-elia-token"),
    )
    if supplied != get_settings().ELIA_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


async def ws_require_token(websocket: WebSocket) -> bool:
    """Validate the WS handshake (query param or upgrade headers)."""
    if not _enabled():
        return True
    supplied = _supplied_token(
        websocket.query_params.get("token"),
        websocket.headers.get("authorization"),
        websocket.headers.get("x-elia-token"),
    )
    if supplied == get_settings().ELIA_AUTH_TOKEN:
        return True
    await websocket.close(code=WS_POLICY_VIOLATION)
    return False
