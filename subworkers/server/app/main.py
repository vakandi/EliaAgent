"""EliaAI Subworker Server — FastAPI application."""
from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator

import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.manager import ConfigManager
from app.config.models import SubworkerConfig
from app.core.auth import require_token
from app.routes.subworkers import router as subworker_router
from app.routes.server import router as server_router
from app.routes.tunnel import router as tunnel_router
from app.routes.websocket import router as ws_router
from app.services.health_manager import DEFAULT_HOST, DEFAULT_PORT, HealthManager
from app.services.runner import SubworkerRunner
from app.services.scheduler import SubworkerScheduler

# ── Structured Logging Setup ────────────────────────────────────────────────

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Also configure stdlib logging so runner/scheduler loggers (which use
# logging.getLogger(__name__)) actually emit to stdout.
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stdout,
    force=True,
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, LOG_LEVEL, logging.INFO)),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# ── Config Directory ────────────────────────────────────────────────────────

_CONFIG_DIR = Path(os.getenv("CONFIG_DIR", str(Path(__file__).parent / "config")))
_SUBWORKERS_DIR = Path(os.getenv("SUBWORKERS_DIR", str(Path(__file__).parent.parent.parent)))

# ── App State ───────────────────────────────────────────────────────────────

_config_manager: ConfigManager | None = None
_scheduler: SubworkerScheduler | None = None
_health_manager: HealthManager | None = None
_start_time: float = 0.0


def get_config_manager() -> ConfigManager:
    """Dependency accessor for route handlers."""
    assert _config_manager is not None, "ConfigManager not initialized"
    return _config_manager


def get_scheduler() -> SubworkerScheduler:
    """Dependency accessor — scheduler instance."""
    assert _scheduler is not None, "SubworkerScheduler not initialized"
    return _scheduler


def get_health_manager() -> HealthManager:
    """Dependency accessor — health manager instance."""
    assert _health_manager is not None, "HealthManager not initialized"
    return _health_manager


async def _run_subworker(
    config: SubworkerConfig,
    prompt: str | None = None,
    model: str | None = None,
    variant: str | None = None,
) -> "SubworkerRunner.RunResult":
    """Run a subworker and return the RunResult.

    The scheduler captures session_id and run metadata from this result.
    Raises RuntimeError on failure so the scheduler records the error.
    """
    runner = SubworkerRunner(
        config,
        log_dir=Path(os.getenv("LOG_DIR", str(_SUBWORKERS_DIR / "logs"))),
        prompt_override=prompt,
        model_override=model,
        variant_override=variant,
    )
    result = await runner.run_subworker()
    if not result.success:
        raise RuntimeError(
            f"Subworker '{config.name}' failed after {result.total_attempts} attempt(s): "
            f"{result.error_message or 'validation failed'}"
        )
    return result


# ── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    global _config_manager, _scheduler, _health_manager, _start_time
    _start_time = time.time()

    _config_manager = ConfigManager(
        config_dir=_CONFIG_DIR,
        subworkers_base_dir=_SUBWORKERS_DIR,
    )
    _config_manager.load()
    logger.info(
        "server.startup",
        port=_config_manager.server.port,
        subworker_count=len(_config_manager.subworkers),
    )

    # Health manager — tracks the already-running OpenCode server (4096).
    # We do NOT start it: the server is managed by opencode-serve.sh.
    # Host must come from OPENCODE_SERVER_URL: inside the bridged container
    # 127.0.0.1 is the container itself, not the host where opencode runs.
    from urllib.parse import urlparse

    _opencode_url = urlparse(os.getenv("OPENCODE_SERVER_URL", "http://127.0.0.1:4096"))
    _health_manager = HealthManager(
        port=_opencode_url.port or 4096,
        host=_opencode_url.hostname or "127.0.0.1",
        work_dir=str(_SUBWORKERS_DIR),
        manage_process=False,
    )

    from app.routes.websocket import ws_manager as _ws_mgr

    async def _on_health_change(old, new, check_result):
        # Push immediately so clients flip their server-down icon in realtime.
        await _ws_mgr.broadcast_status_update()

    _health_manager.on_health_change(_on_health_change)
    await _health_manager.start_external_monitor()

    # Scheduler — one job per subworker, manual triggers supported.
    # state_file lives in LOG_DIR (bind-mounted) so it survives docker nuke.
    _log_dir = Path(os.getenv("LOG_DIR", str(_SUBWORKERS_DIR / "logs")))
    _scheduler = SubworkerScheduler(
        run_fn=_run_subworker,
        state_file=_log_dir / "scheduler_state.json",
    )
    for sw in _config_manager.subworkers:
        _scheduler.add_subworker(sw)

    # WS live events — without these registrations the server never
    # broadcasts anything after the initial snapshot.
    from app.routes.websocket import ws_manager

    def _status_snapshot() -> dict[str, Any] | None:
        running_names = set(_scheduler.get_running())
        return {
            "opencode_health": _health_manager.health_status.value
            if _health_manager else "unknown",
            "subworkers": [
                {
                    "name": sw.name,
                    "enabled": sw.enabled,
                    "running": sw.name in running_names,
                    "schedule_type": sw.schedule.type.value if sw.schedule else None,
                    "schedule": sw.schedule.model_dump() if sw.schedule else None,
                    "model": sw.model,
                    "variant": sw.variant,
                }
                for sw in _config_manager.subworkers
            ],
        }

    ws_manager.set_status_provider(_status_snapshot)
    _scheduler.on_run_complete(ws_manager.as_callback())
    _scheduler.on_run_start(ws_manager.as_start_callback())

    await _scheduler.start()
    logger.info(
        "scheduler.started",
        job_count=len(_config_manager.subworkers),
    )

    # Tunnel permanence — a previously configured tunnel must survive any
    # docker restart / down-up cycle: bring cloudflared back automatically.
    try:
        from app.routes.tunnel import _manager as _tunnel_manager

        _tunnel_state = _tunnel_manager.load_state() or {}
        if _tunnel_state.get("tunnel_token"):
            await _tunnel_manager.start()
            logger.info("tunnel.autostart", domain=_tunnel_state.get("domain"))
    except Exception as exc:
        logger.warning("tunnel.autostart_failed", error=str(exc))

    yield  # ── server is running ──

    await _scheduler.stop()
    logger.info("server.shutdown")


# ── FastAPI App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="EliaAI Subworker Server",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Register Routers ────────────────────────────────────────────────────────

# Auth is applied per-router (NOT globally): a global dependency also runs on
# WebSocket routes where header-security resolution crashes the handshake.
# /health is registered directly on the app and stays open for Docker.
app.include_router(subworker_router, dependencies=[Depends(require_token)])
app.include_router(server_router, dependencies=[Depends(require_token)])
app.include_router(tunnel_router, dependencies=[Depends(require_token)])
app.include_router(ws_router)

# CORS: localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Logging Middleware ──────────────────────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Log every request with method, path, status, and duration."""
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)
    logger.info(
        "http.request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
    )
    return response


# ── Global Exception Handler ────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — logs the exception and returns structured JSON."""
    logger.error(
        "server.unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# ── Health Endpoint ─────────────────────────────────────────────────────────

@app.get("/health")
async def health_check() -> dict:
    """Server health check for Docker healthcheck and external monitoring."""
    uptime = int(time.time() - _start_time) if _start_time else 0
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": uptime,
        "version": "0.1.0",
    }
