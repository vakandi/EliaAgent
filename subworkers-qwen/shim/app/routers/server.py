"""Qwen daemon passthrough — GET /daemon/status (+ server health shape).

Contract: GET /daemon/status passthrough to the Qwen daemon. No caching,
no transformation; transport errors surface as 502.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.config import get_settings
from app.qwen_client import QwenClient, fallback_models

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["server"])

_client = QwenClient()

class ServerHealthResponse(BaseModel):
    state: str
    health_status: str
    pid: int | None = None
    base_url: str | None = None
    restart_count: int = 0
    last_health_check: dict | None = None

class DaemonStatusResponse(BaseModel):
    ok: bool
    daemon: dict


@router.get("/daemon/status", response_model=DaemonStatusResponse)
async def daemon_status() -> DaemonStatusResponse:
    """Passthrough to Qwen GET /daemon/status (uptime, version, workspaceCwd)."""
    try:
        status = await _client.daemon_status()
    except Exception as exc:
        logger.warning("daemon.status_failed", error=type(exc).__name__)
        raise HTTPException(status_code=502, detail="Qwen daemon unreachable")
    return DaemonStatusResponse(ok=True, daemon=status)

@router.get("/server/health", response_model=ServerHealthResponse)
async def get_server_health() -> ServerHealthResponse:
    """TopBar 30s poll target — same shape as live GET /server/health."""
    import time as _time
    try:
        status = await _client.daemon_status()
        daemon = status.get("daemon", status) if isinstance(status, dict) else {}
        return ServerHealthResponse(
            state="healthy",
            health_status="healthy",
            pid=daemon.get("pid"),
            base_url="http://qwen:4170",
            last_health_check={"ts": _time.time(), "daemon": daemon.get("status", "ok")},
        )
    except Exception as exc:
        logger.warning("server.health_degraded", error=type(exc).__name__)
        return ServerHealthResponse(state="degraded", health_status="degraded")

# ── Live-parity routes (model names identical to live server/app/routes) ──
# Paths mirror live exactly: /server/* (server router prefix), /models,
# PUT /status/{name}, /config/reload, /sessions/{name} (root-level).
# Zero live-LLM-prompt budget used here: reads only (daemon status, zen
# catalog, disk config, buffered SSE). No turn is ever started.

ZEN_MODELS_URL = os.getenv(
    "ZEN_MODELS_URL", "http://host.docker.internal:18898/zen/v1/models"
)
# proxy-local zen gateway key is public by design; never log it anyway.
ZEN_API_KEY = os.getenv("ZEN_API_KEY", "public")

_restart_count = 0
_last_config_names: list[str] | None = None


class RestartResponse(BaseModel):
    status: str
    message: str
    state: str


class CleanupRequest(BaseModel):
    restart_opencode: bool = True
    run_idle_cleaner: bool = True


class CleanupProcess(BaseModel):
    pid: int
    label: str
    cmd: str | None = None


class CleanupStep(BaseModel):
    name: str
    ok: bool = True
    detail: str | None = None
    duration_ms: int = 0


class CleanupResponse(BaseModel):
    ok: bool
    opencode_restarted: bool = False
    idle_cleaned: bool = False
    old_pid: int | None = None
    new_pid: int | None = None
    rss_before_mb: int | None = None
    rss_after_mb: int | None = None
    freed_mb: int | None = None
    killed: dict[str, int] | None = None
    processes: list[CleanupProcess] | None = None
    steps: list[CleanupStep] | None = None
    duration_ms: int = 0
    error: str | None = None


class ModelOption(BaseModel):
    id: str
    name: str
    provider: str
    reasoning: bool = False
    variants: list[str] = []


class ModelsResponse(BaseModel):
    models: list[ModelOption]
    total: int


class UpdateSubworkerRequest(BaseModel):
    agent_id: str | None = None
    model: str | None = None
    variant: str | None = None
    timeout_minutes: int | None = Field(default=None, ge=1, le=120)
    max_retries: int | None = Field(default=None, ge=0, le=10)
    schedule: dict[str, Any] | None = None
    # Shim extension (live has no enabled field): PUT doubles as enable/schedule update.
    enabled: bool | None = None


class SubworkerDetail(BaseModel):
    name: str
    enabled: bool
    running: bool
    next_run: str | None = None
    schedule: dict[str, Any]
    agent_id: str
    timeout_minutes: int
    max_retries: int
    model: str | None = None
    variant: str | None = None


class ReloadResponse(BaseModel):
    status: str
    added: list[str]
    removed: list[str]
    unchanged: list[str]
    total: int


class SessionMessagePart(BaseModel):
    type: str
    text: str | None = None
    tool: str | None = None
    input: dict[str, Any] | None = None
    output: str | None = None


class SessionMessageInfo(BaseModel):
    role: str | None = None
    agent: str | None = None
    model: str | None = None
    variant: str | None = None
    time_created: int | None = None


class SessionMessage(BaseModel):
    info: SessionMessageInfo
    parts: list[SessionMessagePart]


class SessionResponse(BaseModel):
    name: str
    session_id: str | None = None
    messages: list[SessionMessage]
    total_messages: int


def _rss_mb() -> int | None:
    """Shim process RSS in MB (Linux container); None when unmeasurable."""
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    except Exception:
        return None


async def _shim_state() -> str:
    """healthy when the Qwen daemon answers, else degraded."""
    try:
        await _client.daemon_status()
        return "healthy"
    except Exception:
        return "degraded"


def _try_compose_recreate() -> tuple[bool, str]:
    """Recreate shim+qwen via compose — guarded: no docker socket/CLI in this
    container by design, so this refuses with a host-side command instead."""
    import shutil
    import subprocess
    if not Path("/var/run/docker.sock").exists():
        return False, (
            "Restart guarded: no Docker socket in shim container; "
            "run on host: docker compose up -d --force-recreate shim qwen"
        )
    if shutil.which("docker") is None:
        return False, "Restart guarded: docker CLI not installed in shim container"
    try:
        proc = subprocess.run(
            ["docker", "compose", "up", "-d", "--force-recreate", "shim", "qwen"],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as exc:
        return False, f"Restart failed: {type(exc).__name__}"
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "unknown error")[-300:]
        return False, f"Restart failed: {tail}"
    return True, "Shim+qwen recreated successfully"


def _next_run_for(name: str) -> str | None:
    """APScheduler next fire time for qwen-<name>; None when unscheduled."""
    try:
        import app.main as main_mod
        sched = main_mod._scheduler
        if sched is None:
            return None
        job = sched.get_job(f"qwen-{name}")
        if job is None or job.next_run_time is None:
            return None
        return job.next_run_time.isoformat()
    except Exception:
        return None


def _event_to_message(event: dict, model: str | None) -> SessionMessage:
    """Map one buffered Qwen SSE event to a live-shaped session message."""
    etype = str(event.get("type", "unknown"))
    text = event.get("text") or event.get("delta") or event.get("content")
    if isinstance(text, dict):
        text = text.get("text")
    raw_tool = event.get("tool")
    ts = event.get("ts") or event.get("time_created")
    return SessionMessage(
        info=SessionMessageInfo(
            role=event.get("role") if isinstance(event.get("role"), str) else None,
            model=model,
            time_created=int(ts) if isinstance(ts, (int, float)) else None,
        ),
        parts=[SessionMessagePart(
            type=etype,
            text=text if isinstance(text, str) else None,
            tool=raw_tool if isinstance(raw_tool, str) else None,
        )],
    )


@router.post("/server/restart", response_model=RestartResponse)
async def restart_server() -> RestartResponse:
    """Recreate shim+qwen via compose (guarded without a docker socket)."""
    global _restart_count
    ok, message = _try_compose_recreate()
    if ok:
        _restart_count += 1
        logger.info("server.restarted")
    else:
        logger.warning("server.restart_guarded", message=message[:120])
    return RestartResponse(
        status="restarted" if ok else "error",
        message=message,
        state=await _shim_state(),
    )


@router.post("/server/cleanup", response_model=CleanupResponse)
async def cleanup_server(body: CleanupRequest | None = None) -> CleanupResponse | JSONResponse:
    """Prune shim session/SSE history (+ optional guarded container recreate).

    Mirrors live's flow: per-step timeline, RSS before/after, graceful 500
    payload on failure.
    """
    global _restart_count
    body = body or CleanupRequest()
    t0 = time.time()
    logger.info(
        "cleanup.requested",
        restart=body.restart_opencode, prune=body.run_idle_cleaner,
    )
    steps: list[CleanupStep] = []
    restarted = False
    cleaned = False
    killed: dict[str, int] | None = None
    try:
        s0 = time.time()
        rss_before = _rss_mb()
        steps.append(CleanupStep(
            name="rss_snapshot",
            detail=f"{rss_before} MB" if rss_before is not None else "unreadable",
            duration_ms=int((time.time() - s0) * 1000),
        ))
        if body.restart_opencode:
            s0 = time.time()
            ok, msg = _try_compose_recreate()
            restarted = ok
            if ok:
                _restart_count += 1
            steps.append(CleanupStep(
                name="shim_qwen_recreate",
                ok=ok,
                detail=msg[:200],
                duration_ms=int((time.time() - s0) * 1000),
            ))
        if body.run_idle_cleaner:
            s0 = time.time()
            from app.routers import subworkers as sw_router
            n_sessions = sum(len(v) for v in sw_router._sessions.values())
            n_runs = len(sw_router._runs)
            sw_router._sessions.clear()
            sw_router._runs.clear()
            cleaned = True
            killed = {"sessions": n_sessions, "runs": n_runs}
            steps.append(CleanupStep(
                name="history_prune",
                detail=f"pruned {n_sessions} sessions, {n_runs} runs",
                duration_ms=int((time.time() - s0) * 1000),
            ))
    except Exception as exc:
        logger.exception("cleanup.failed")
        duration_ms = int((time.time() - t0) * 1000)
        return JSONResponse(
            status_code=500,
            content=CleanupResponse(
                ok=False,
                opencode_restarted=restarted,
                idle_cleaned=cleaned,
                killed=killed,
                steps=steps,
                duration_ms=duration_ms,
                error=str(exc),
            ).model_dump(),
        )
    rss_after = _rss_mb()
    freed = None
    if rss_before is not None and rss_after is not None:
        freed = rss_before - rss_after
    duration_ms = int((time.time() - t0) * 1000)
    logger.info("cleanup.done", restarted=restarted, cleaned=cleaned, killed=killed)
    return CleanupResponse(
        ok=True,
        opencode_restarted=restarted,
        idle_cleaned=cleaned,
        rss_before_mb=rss_before,
        rss_after_mb=rss_after,
        freed_mb=freed,
        killed=killed,
        steps=steps,
        duration_ms=duration_ms,
    )


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """Zen gateway catalog (OpenAI-style /zen/v1/models); static 9-model
    chain fallback when the gateway is unreachable."""
    options: list[ModelOption] = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                ZEN_MODELS_URL, headers={"Authorization": f"Bearer {ZEN_API_KEY}"}
            )
            resp.raise_for_status()
            data = resp.json()
        items = data.get("data") if isinstance(data, dict) else None
        for m in items or []:
            mid = str(m.get("id", ""))
            if mid:
                options.append(ModelOption(id=mid, name=mid, provider="zen"))
    except Exception as exc:
        logger.warning("models.gateway_unreachable", error=type(exc).__name__)
        options = [
            ModelOption(id=m, name=m, provider="zen") for m in fallback_models()
        ]
    options.sort(key=lambda o: o.id.lower())
    return ModelsResponse(models=options, total=len(options))


@router.put("/status/{name}", response_model=SubworkerDetail)
async def update_subworker(name: str, body: UpdateSubworkerRequest) -> SubworkerDetail:
    """Edit a subworker's config (enable flag, agent, model, timeouts, schedule).

    Unlike live (memory-only), the shim persists to subworkers.json — the shim
    re-reads disk per request, so disk IS the live config here.
    """
    from app.routers import subworkers as sw_router
    entry = sw_router._find(name)
    if body.enabled is not None:
        entry["enabled"] = body.enabled
    if body.agent_id is not None:
        entry["agent_id"] = body.agent_id
    if body.model is not None:
        entry["model"] = body.model
    if body.variant is not None:
        entry["variant"] = body.variant
    if body.timeout_minutes is not None:
        entry["timeout_minutes"] = body.timeout_minutes
    if body.max_retries is not None:
        entry["max_retries"] = body.max_retries
    if body.schedule is not None:
        schedule_type = body.schedule.get("type", "interval")
        if schedule_type == "cron":
            if "expression" not in body.schedule and "crontab" not in body.schedule:
                raise HTTPException(status_code=422, detail="cron schedule needs expression")
            # Shim scheduler reads `crontab`; keep both keys in sync.
            body.schedule.setdefault(
                "crontab", body.schedule.get("expression", body.schedule.get("crontab", ""))
            )
            entry["schedule"] = body.schedule
        elif schedule_type == "every":
            every_val = int(body.schedule.get("every", 0))
            if every_val < 1 or every_val > 1440:
                raise HTTPException(status_code=422, detail="every must be 1..1440 minutes")
            entry["schedule"] = body.schedule
        elif schedule_type == "interval":
            entry["schedule"] = body.schedule
        else:
            raise HTTPException(status_code=422, detail=f"Invalid schedule type: {schedule_type}")
    if entry == sw_router._find(name):
        raise HTTPException(status_code=422, detail="No fields to update")
    path = get_settings().CONFIG_DIR / "subworkers.json"
    try:
        cfg = json.loads(path.read_text())
        for i, e in enumerate(cfg.get("subworkers", [])):
            if e.get("name") == name:
                cfg["subworkers"][i] = entry
                break
        else:
            raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")
        path.write_text(json.dumps(cfg, indent=2) + "\n")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"subworkers.json not writable: {exc}")
    from app.routers import subworkers as sw_router2
    running = any(
        r.name == name and r.status == "running"
        for r in sw_router2._runs.values()
    )
    logger.info("subworker.updated", name=name)
    return SubworkerDetail(
        name=entry["name"],
        enabled=bool(entry.get("enabled", False)),
        running=running,
        next_run=_next_run_for(name),
        schedule=entry.get("schedule") or {},
        agent_id=entry.get("agent_id", ""),
        timeout_minutes=int(entry.get("timeout_minutes", 0)),
        max_retries=int(entry.get("max_retries", 0)),
        model=entry.get("model"),
        variant=entry.get("variant"),
    )


@router.post("/config/reload", response_model=ReloadResponse)
async def reload_config() -> ReloadResponse:
    """Hot-reload report: diff disk names vs the previous reload call.

    The shim already reads subworkers.json per request, so the config is
    always current; this endpoint reports what changed for TopBar parity.
    """
    global _last_config_names
    from app.routers import subworkers as sw_router
    current = [
        str(e.get("name"))
        for e in sw_router._load_config().get("subworkers", [])
        if e.get("name")
    ]
    if _last_config_names is None:
        added, removed, unchanged = [], [], list(current)
    else:
        prev, cur = set(_last_config_names), set(current)
        added = sorted(cur - prev)
        removed = sorted(prev - cur)
        unchanged = sorted(cur & prev)
    _last_config_names = list(current)
    logger.info("config.reloaded", total=len(current))
    return ReloadResponse(
        status="reloaded",
        added=added,
        removed=removed,
        unchanged=unchanged,
        total=len(current),
    )


@router.get("/sessions/{name}", response_model=SessionResponse)
async def get_subworker_sessions(
    name: str,
    limit: int = 50,
    session_id: str | None = None,
) -> SessionResponse:
    """Latest (or explicit) shim session → buffered daemon SSE events,
    live-shaped. Graceful empty on unknown session / daemon outage."""
    from app.routers import subworkers as sw_router
    sw_router._find(name)
    sessions = sw_router._sessions.get(name, {})
    sid = session_id
    target = sessions.get(sid) if sid is not None else None
    if sid is None and sessions:
        sid = next(reversed(sessions))
        target = sessions[sid]
    if target is None:
        return SessionResponse(name=name, session_id=sid, messages=[], total_messages=0)
    try:
        events = await _client.stream_events(target)
    except Exception as exc:
        logger.warning(
            "sessions.daemon_unreachable", name=name, error=type(exc).__name__
        )
        return SessionResponse(name=name, session_id=sid, messages=[], total_messages=0)
    messages = [_event_to_message(e, target.model) for e in events[:limit] if isinstance(e, dict)]
    return SessionResponse(
        name=name,
        session_id=sid,
        messages=messages,
        total_messages=len(messages),
    )
