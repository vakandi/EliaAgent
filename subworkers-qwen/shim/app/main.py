"""EliaAI Subworker Qwen Shim — Elia routes over the Qwen serve protocol.

Same FastAPI surface as the live server (trigger/continue/sessions/
main-agent/WS); only the session backend changes (Qwen daemon :4170).
Interval schedules keep APScheduler as-is, reusing subworkers.json
(interval + every + cron). No routine translation needed.
"""
from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import require_token
from app.config import get_settings
from app.routers import main_agent as main_agent_router
from app.routers import server as server_router
from app.routers import subworkers as subworkers_router
from app.routers import tunnel as tunnel_router
from app.routers import websocket as websocket_router

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVEL, format="%(message)s")

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, LOG_LEVEL, logging.INFO)
    ),
)

logger = structlog.get_logger()

_scheduler: AsyncIOScheduler | None = None
_start_time: float = 0.0


def _schedule_kwargs(entry: dict) -> dict | None:
    """Map a subworkers.json schedule to an APScheduler trigger kwarg set."""
    schedule = entry.get("schedule") or {}
    kind = schedule.get("type")
    if kind == "every":
        return {"trigger": IntervalTrigger(minutes=int(schedule.get("every", 30)))}
    if kind == "interval":
        hours = schedule.get("hours") or []
        minute = int(schedule.get("minute", 0))
        if not hours:
            return None
        return {
            "trigger": CronTrigger(
                hour=",".join(str(h) for h in hours), minute=minute
            )
        }
    if kind == "cron":
        return {"trigger": CronTrigger.from_crontab(schedule.get("crontab", ""))}
    logger.warning("scheduler.unknown_type", name=entry.get("name"), type=kind)
    return None


def _load_entries() -> list[dict]:
    path = Path(get_settings().CONFIG_DIR) / "subworkers.json"
    try:
        return json.loads(path.read_text()).get("subworkers", [])
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("scheduler.config_unreadable", error=str(exc)[:200])
        return []


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup: schedule enabled subworkers. Shutdown: stop scheduler."""
    global _scheduler, _start_time
    import time

    _start_time = time.time()
    _scheduler = AsyncIOScheduler(timezone="Africa/Casablanca")
    scheduled = 0
    for entry in _load_entries():
        if not entry.get("enabled", False):
            continue
        kwargs = _schedule_kwargs(entry)
        if kwargs is None:
            continue
        _scheduler.add_job(
            subworkers_router.run_scheduled,
            args=[entry["name"]],
            id=f"qwen-{entry['name']}",
            replace_existing=True,
            **kwargs,
        )
        scheduled += 1
    _scheduler.start()
    logger.info("server.startup", scheduled=scheduled, port=get_settings().PORT)
    yield
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
    logger.info("server.shutdown")


app = FastAPI(title="EliaAI Subworker Qwen Shim", version="0.1.0", lifespan=lifespan)

# Auth is applied per-router (NOT globally): a global dependency also runs on
# WebSocket routes where header-security resolution crashes the handshake.
# /health is registered directly on the app and stays open for Docker.
app.include_router(subworkers_router.router, dependencies=[Depends(require_token)])
app.include_router(server_router.router, dependencies=[Depends(require_token)])
app.include_router(main_agent_router.router, dependencies=[Depends(require_token)])
app.include_router(tunnel_router.router, dependencies=[Depends(require_token)])
app.include_router(websocket_router.router)

# CORS: localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:  # type: ignore[no-untyped-def]
    """Catch-all handler — logs the exception and returns structured JSON."""
    logger.error("server.unhandled", path=request.url.path, error=str(exc)[:500])
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health_check() -> dict:
    """Shim health check for Docker healthcheck and external monitoring."""
    import time

    return {
        "status": "ok",
        "service": "subworker-qwen-shim",
        "uptime_s": round(time.time() - _start_time, 1) if _start_time else 0.0,
    }


@app.get("/daemon/status")
async def daemon_status_alias() -> dict:
    """Alias so ColimaBar-style clients find daemon status at root too."""
    return await server_router.daemon_status()
