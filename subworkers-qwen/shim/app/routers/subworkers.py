"""Elia-native subworker routes backed by the Qwen daemon.

Mirrors the live server surface (routes/subworkers.py) with the session
backend swapped: opencode serve → Qwen serve protocol via QwenClient.
NOTE (engine swap 2026-09-19): trigger/continue run via opencode_engine
(`opencode run` subprocess); QWEN path (QwenClient/stream_bridge) left dormant.

- POST /trigger/{name}                 manual trigger (PROMPT.md + date body)
- POST /sessions/{name}/{id}/continue  re-prompt an existing session (gap 5)
- GET  /sessions/{name}/list           shim-side session registry
- GET  /sessions/{name}/events         buffered SSE events for a session
- GET  /status  /  GET /status/{name}  registry + subworkers.json status
- POST /enable/{name} / /disable/{name} schedule toggles (in-memory)
- GET  /logs/{name}                    tail of the per-run log file
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import notifier
from app import opencode_engine
from app.config import get_settings
from app.qwen_client import QwenClient, QwenSession, RunRecord, fallback_models
from app.routers.websocket import ws_manager
from app.stream_bridge import start_stream

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["subworkers"])

_client = QwenClient()

# Shim-side registries (persisted to LOG_DIR/state.json on change; Qwen
# daemon sessions are the source of truth for transcripts).
_runs: dict[str, RunRecord] = {}
_sessions: dict[str, dict[str, QwenSession]] = {}
_opencode_sessions: dict[str, str] = {}
_overrides: dict[str, bool] = {}
MAX_TAIL = 4000


def _config_path() -> Path:
    return get_settings().CONFIG_DIR / "subworkers.json"


def _load_config() -> dict[str, Any]:
    return json.loads(_config_path().read_text())


def _find(name: str) -> dict[str, Any]:
    for entry in _load_config().get("subworkers", []):
        if entry.get("name") == name:
            return entry
    raise HTTPException(status_code=404, detail=f"Unknown subworker: {name}")


def _is_enabled(entry: dict[str, Any]) -> bool:
    return _overrides.get(entry["name"], bool(entry.get("enabled", False)))


def _workspace_cwd(name: str) -> str:
    """Per-subworker cwd under /srv/case/<name> (gap 2/3)."""
    return f"/srv/case/{name}"


def _prompt_file_path(name: str, prompt_file: str) -> Path:
    return get_settings().SUBWORKERS_DIR / name / prompt_file


def _run_log_path(name: str) -> Path:
    get_settings().LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return get_settings().LOG_DIR / f"{name}_{stamp}.log"


def _run_key(name: str, session_id: str) -> str:
    return f"{name}:{session_id}"


def _qwen_rss_mb() -> float | None:
    """Engine RSS mirror of live's opencode RSS gate.

    Sums RSS of local `qwen serve` processes. Returns None when unmeasurable
    (e.g. engine in sibling container without shared pid namespace) — the
    gate then passes and the container mem_limit remains the real guard.
    """
    try:
        out = subprocess.run(
            ["ps", "-o", "rss=", "-C", "qwen"],
            capture_output=True, text=True, timeout=5,
        )
        total_kb = sum(int(line.strip()) for line in out.stdout.splitlines() if line.strip().isdigit())
        if total_kb:
            return total_kb / 1024
    except Exception:
        pass
    try:
        out = subprocess.run(
            ["pgrep", "-f", "qwen serve"],
            capture_output=True, text=True, timeout=5,
        )
        pids = [p for p in out.stdout.split() if p.isdigit()]
        total_kb = 0
        for pid in pids:
            try:
                with open(f"/proc/{pid}/statm") as fh:
                    pages = int(fh.read().split()[1])
                import os as _os
                total_kb += pages * _os.sysconf("SC_PAGE_SIZE") // 1024
            except Exception:
                continue
        return total_kb / 1024 if total_kb else None
    except Exception:
        return None


def _load_gate() -> tuple[bool, str]:
    # RSS cap retired 2026-09-19: container mem_limit is the real guard.
    # RSS stays observable via _qwen_rss_mb (status routes) — never a refusal.
    return True, ""


async def _execute_run(name: str, entry: dict[str, Any], message: str | None) -> RunRecord:
    """ENGINE: mint shim session → stream `opencode run` turn in background."""
    gate_ok, gate_reason = _load_gate()
    if not gate_ok:
        logger.warning("load-gate blocked run", name=name, reason=gate_reason)
        raise HTTPException(status_code=503, detail=f"Load gate blocked run: {gate_reason}")
    prompt_path = _prompt_file_path(name, entry.get("prompt_file", "PROMPT.md"))
    if not prompt_path.exists():
        raise HTTPException(status_code=500, detail=f"PROMPT.md missing for {name}")
    body = prompt_path.read_text() + f"\n\nRun date: {datetime.now().isoformat()}"
    if message:
        body += f"\n\nOperator note: {message}"

    # Per-agent model + variant from config (live parity): claims-monitor runs
    # ling/medium, workspace-digest runs spark-1.2/xhigh, etc. The engine
    # default (spark-1.3, no variant) under-thinks every agent.
    model = entry.get("model") or fallback_models()[0]
    variant = entry.get("variant")
    workspace = str(get_settings().SUBWORKERS_DIR / name)
    shim_sid = uuid.uuid4().hex[:16]
    prompt_id = f"opencode-{shim_sid}"
    record = RunRecord(name=name, session_id=shim_sid, client_id="opencode")
    record.prompt_id = prompt_id
    record.model = model
    _runs[_run_key(name, shim_sid)] = record
    _sessions.setdefault(name, {})[shim_sid] = QwenSession(
        session_id=shim_sid, client_id="opencode", workspace_cwd=workspace, model=model
    )
    asyncio.ensure_future(_pump_opencode_run(name, shim_sid, workspace, body, model, prompt_id, variant))
    await ws_manager.broadcast({"type": "run_update", "name": name, "status": record.status})
    return record

async def _pump_opencode_run(
    name: str,
    shim_sid: str,
    workspace: str,
    body: str,
    model: str,
    prompt_id: str,
    variant: str | None = None,
) -> None:
    """Background turn pump: engine frames → run_log WS; terminal → record.

    A run that stops emitting frames is FAILED, never eternal: per-frame stall
    timeout (STALL_TIMEOUT_S) plus an overall run deadline (MAX_RUN_S) feed the
    existing RuntimeError path (failed record + error banner + WS events).
    """
    record = _runs.get(_run_key(name, shim_sid))
    log_path = _run_log_path(name)
    capture: dict[str, str | None] = {}
    counts = {"text": 0, "reasoning": 0, "tool": 0}
    tail = ""
    settings = get_settings()
    deadline = time.time() + settings.MAX_RUN_S
    stream = opencode_engine.run_turn(
        workspace, body, model, None, capture=capture, run_key=_run_key(name, shim_sid),
        variant=variant,
    ).__aiter__()
    try:
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise RuntimeError(f"run exceeded max duration ({settings.MAX_RUN_S}s)")
            try:
                field, text = await asyncio.wait_for(
                    stream.__anext__(), timeout=min(settings.STALL_TIMEOUT_S, remaining)
                )
            except StopAsyncIteration:
                break
            except asyncio.TimeoutError:
                raise RuntimeError(
                    f"turn stalled: no output for {settings.STALL_TIMEOUT_S}s "
                    f"(text={counts['text']} reasoning={counts['reasoning']} tool={counts['tool']})"
                )
            counts[field] = counts.get(field, 0) + 1
            if field == "text":
                tail = (tail + text)[-MAX_TAIL:]
            await ws_manager.broadcast_run_log(name, text, field)
        opencode_sid = capture.get("session_id") or shim_sid
        _opencode_sessions[_run_key(name, shim_sid)] = opencode_sid
        if record is not None:
            record.status = "completed"
            record.ended_at = time.time()
        log_path.write_text(
            f"session={shim_sid} opencode_session={opencode_sid} prompt={prompt_id} "
            f"model={model} text={counts['text']} reasoning={counts['reasoning']} "
            f"tool={counts['tool']} tail={tail[-500:]}\n"
        )
        await notifier.notify_run_completed(name, shim_sid, model)
        await ws_manager.broadcast({"event": "subworker_completed", "name": name})
    except RuntimeError as exc:
        # 429 → queue + alert, keep record. Anything else (stall, deadline,
        # engine failure) is terminal FAILED so TopBar shows the error
        # instead of "running" forever.
        terminal_failed = "429" not in str(exc)
        if record is not None:
            record.status = "failed" if terminal_failed else "queued_429"
            record.ended_at = time.time()
        log_path.write_text(f"{record.status if record else 'failed'} session={shim_sid} error={exc}\n")
        await notifier.notify_run_failed(name, str(exc)[:500])
        await ws_manager.broadcast({
            "event": "run_banner",
            "name": name,
            "banner": {"type": "error", "message": str(exc)[:500]},
        })
        await ws_manager.broadcast({"event": "subworker_failed", "name": name, "error": str(exc)[:500]})
    await ws_manager.broadcast({
        "type": "run_update", "name": name, "status": record.status if record else "queued_429",
    })


# ── Response Models ─────────────────────────────────────────────────────────


class SubworkerStatus(BaseModel):
    name: str
    enabled: bool
    status: str = "idle"
    running: bool = False
    last_run: float | None = None


class StatusResponse(BaseModel):
    scheduler_running: bool
    total: int
    subworkers: list[SubworkerStatus]


class TriggerRequest(BaseModel):
    message: str | None = None


class TriggerResponse(BaseModel):
    status: str
    name: str
    session_id: str | None = None


class EnableResponse(BaseModel):
    status: str
    name: str
    enabled: bool


class ContinueRequest(BaseModel):
    message: str | None = Field(
        default=None, description="Message to send to the session (default: 'continue the tasks')"
    )


class ContinueResponse(BaseModel):
    status: str
    name: str
    session_id: str
    prompt_id: str
    message: str


class SessionListItem(BaseModel):
    session_id: str
    workspace_cwd: str
    model: str


class SessionListResponse(BaseModel):
    name: str
    sessions: list[SessionListItem]


class EventsResponse(BaseModel):
    name: str
    session_id: str
    events: list[dict]


class LogsResponse(BaseModel):
    name: str
    lines: list[str]
    total_lines: int


# ── Endpoints ───────────────────────────────────────────────────────────────


@router.get("/status", response_model=StatusResponse)
async def get_all_status() -> StatusResponse:
    config = _load_config()
    items = [
        SubworkerStatus(
            name=entry["name"],
            enabled=_is_enabled(entry),
            status=next(
                (r.status for r in _runs.values() if r.name == entry["name"]),
                "idle",
            ),
            running=any(r.name == entry["name"] and r.status == "running" for r in _runs.values()),
        )
        for entry in config.get("subworkers", [])
    ]
    return StatusResponse(scheduler_running=True, total=len(items), subworkers=items)


@router.get("/status/{name}", response_model=SubworkerStatus)
async def get_subworker_status(name: str) -> SubworkerStatus:
    entry = _find(name)
    latest = next((r for r in _runs.values() if r.name == name), None)
    return SubworkerStatus(
        name=name,
        enabled=_is_enabled(entry),
        status=latest.status if latest else "idle",
        running=bool(latest and latest.status == "running"),
        last_run=latest.started_at if latest else None,
    )


@router.post("/trigger/{name}", response_model=TriggerResponse)
async def trigger_subworker(name: str, body: TriggerRequest | None = None) -> TriggerResponse:
    """Manually trigger a subworker immediately (gap 4: PROMPT.md + date)."""
    entry = _find(name)
    if len([r for r in _runs.values() if r.status == "running"]) >= get_settings().MAX_CONCURRENT_RUNS:
        raise HTTPException(status_code=429, detail="Max concurrent runs reached")
    record = await _execute_run(name, entry, body.message if body else None)
    return TriggerResponse(status=record.status, name=name, session_id=record.session_id)


@router.post("/enable/{name}", response_model=EnableResponse)
async def enable_subworker(name: str) -> EnableResponse:
    _find(name)
    _overrides[name] = True
    return EnableResponse(status="enabled", name=name, enabled=True)


@router.post("/disable/{name}", response_model=EnableResponse)
async def disable_subworker(name: str) -> EnableResponse:
    _find(name)
    _overrides[name] = False
    return EnableResponse(status="disabled", name=name, enabled=False)


@router.get("/sessions/{name}/list", response_model=SessionListResponse)
async def list_subworker_sessions(name: str) -> SessionListResponse:
    _find(name)
    items = [
        SessionListItem(
            session_id=session.session_id,
            workspace_cwd=session.workspace_cwd,
            model=session.model,
        )
        for session in _sessions.get(name, {}).values()
    ]
    return SessionListResponse(name=name, sessions=items)


@router.get("/sessions/{name}/{session_id}/events", response_model=EventsResponse)
async def get_session_events(name: str, session_id: str) -> EventsResponse:
    """Buffered turn events for a session (gap 10 observability).

    Owner resolution: engine-owned sessions (client_id "opencode", minted by
    trigger/continue) replay stored engine frames — 200 with a possibly empty
    list while the turn is still running. Daemon-owned sessions keep the QWEN
    path, degraded to 200-empty on daemon outage. Unknown sessions return
    200-empty (TopBar treats empty as waiting); never 404/500 here.
    """
    _find(name)
    key = _run_key(name, session_id)
    session = _sessions.get(name, {}).get(session_id)
    if session is None or session.client_id == "opencode":
        frames = opencode_engine.get_frames(key)
        return EventsResponse(
            name=name,
            session_id=session_id,
            events=[
                {"event": "run_log", "name": name, "field": frame["field"], "text": frame["text"]}
                for frame in frames
            ],
        )
    try:
        events = await _client.stream_events(session)
    except Exception as exc:
        logger.warning("events.daemon_unreachable", name=name, error=type(exc).__name__)
        events = []
    return EventsResponse(name=name, session_id=session_id, events=events)


@router.post("/sessions/{name}/{session_id}/continue", response_model=ContinueResponse)
async def continue_session(name: str, session_id: str, body: ContinueRequest | None = None) -> ContinueResponse:
    """ENGINE: follow-up turn on the stored opencode session (gap 5)."""
    session = _sessions.get(name, {}).get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")
    message = (body.message if body and body.message else "continue the tasks")
    prompt_id = f"opencode-{uuid.uuid4().hex[:12]}"
    workspace = str(get_settings().SUBWORKERS_DIR / name)
    opencode_sid = _opencode_sessions.get(_run_key(name, session_id))
    asyncio.ensure_future(
        _pump_continue(name, session_id, workspace, message, session.model, prompt_id, opencode_sid,
                        _find(name).get("variant"))
    )
    record = _runs.get(_run_key(name, session_id))
    if record is not None:
        record.prompt_id = prompt_id
        record.status = "running"
        record.ended_at = None
    await ws_manager.broadcast({"type": "run_update", "name": name, "status": "running"})
    return ContinueResponse(
        status="admitted",
        name=name,
        session_id=session_id,
        prompt_id=prompt_id,
        message=message,
    )


async def _pump_continue(
    name: str,
    shim_sid: str,
    workspace: str,
    message: str,
    model: str,
    prompt_id: str,
    opencode_sid: str | None,
    variant: str | None = None,
) -> None:
    """Background follow-up pump: engine frames → run_log WS; terminal → record."""
    record = _runs.get(_run_key(name, shim_sid))
    capture: dict[str, str | None] = {}
    try:
        async for field, text in opencode_engine.run_turn(
            workspace, message, model, opencode_sid, capture=capture, run_key=_run_key(name, shim_sid),
            variant=variant,
        ):
            await ws_manager.broadcast_run_log(name, text, field)
        if capture.get("session_id"):
            _opencode_sessions[_run_key(name, shim_sid)] = str(capture["session_id"])
        if record is not None:
            record.status = "completed"
    except RuntimeError as exc:
        terminal_failed = "429" not in str(exc)
        if record is not None:
            record.status = "failed" if terminal_failed else "queued_429"
            record.ended_at = time.time()
        await notifier.notify_run_failed(name, str(exc)[:500])
        await ws_manager.broadcast({
            "event": "run_banner",
            "name": name,
            "banner": {"type": "error", "message": str(exc)[:500]},
        })
        await ws_manager.broadcast({"event": "subworker_failed", "name": name, "error": str(exc)[:500]})
    await ws_manager.broadcast({
        "type": "run_update", "name": name, "status": record.status if record else "queued_429",
    })


@router.get("/logs/{name}", response_model=LogsResponse)
async def get_subworker_logs(name: str, lines: int = 100) -> LogsResponse:
    log_dir = get_settings().LOG_DIR
    candidates = sorted(log_dir.glob(f"{name}_*.log"))
    if not candidates:
        return LogsResponse(name=name, lines=[], total_lines=0)
    content = candidates[-1].read_text().splitlines()
    return LogsResponse(name=name, lines=content[-lines:], total_lines=len(content))


def run_scheduled(name: str) -> None:
    """APScheduler entrypoint — fire-and-forget trigger for enabled agents."""
    try:
        entry = _find(name)
    except HTTPException:
        logger.warning("scheduler.unknown_subworker", name=name)
        return
    if not _is_enabled(entry):
        return
    asyncio.get_event_loop().call_soon(
        lambda: asyncio.ensure_future(_execute_run(name, entry, None))
    )
    logger.info("scheduler.triggered", name=name, at=time.time())
