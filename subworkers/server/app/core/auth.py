"""Shared-token auth for the EliaAI subworker server.

Single admin token model (docs/AUTHENTIFICATION.md):
- ELIA_AUTH_TOKEN set in the environment enables protection.
- Empty/missing token disables auth entirely (backward compatible).
- HTTP accepts ``Authorization: Bearer <token>`` OR ``X-Elia-Token``.
- WebSocket accepts ``?token=<token>`` OR the same two headers on the
  upgrade request (native clients can set headers; browsers cannot).
- ``/health`` stays open for the Docker healthcheck.

Note: header-based Security machinery (APIKeyHeader) is deliberately NOT
used — its dependency resolution crashes on WebSocket scope. Headers are
read directly off the request/connection objects instead.
"""
from __future__ import annotations

import os

from fastapi import HTTPException, Request, WebSocket, status

TOKEN = os.getenv("ELIA_AUTH_TOKEN", "").strip()

EXEMPT_PATHS = {"/health"}

WS_POLICY_VIOLATION = 1008


def _enabled() -> bool:
    return bool(TOKEN)


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
    if supplied != TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )


async def ws_require_token(websocket: WebSocket) -> bool:
    """Validate the WS handshake (query param or upgrade headers).

    Closes with 1008 (policy violation) and returns False on failure.
    """
    if not _enabled():
        return True
    supplied = _supplied_token(
        websocket.query_params.get("token"),
        websocket.headers.get("authorization"),
        websocket.headers.get("x-elia-token"),
    )
    if supplied == TOKEN:
        return True
    await websocket.close(code=WS_POLICY_VIOLATION)
    return False
