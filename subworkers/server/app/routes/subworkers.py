"""Subworker management API endpoints.

Provides status, trigger, enable/disable, config editing, and log viewing.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config.manager import ConfigManager
import structlog

from app.services.scheduler import SubworkerScheduler

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["subworkers"])


# ── Response Models ────────────────────────────────────────────────────────

class SubworkerStatus(BaseModel):
    name: str
    enabled: bool
    running: bool
    next_run: str | None = None
    schedule_type: str | None = None


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


class StatusResponse(BaseModel):
    scheduler_running: bool
    total: int
    subworkers: list[SubworkerStatus]


class TriggerResponse(BaseModel):
    status: str
    name: str
    message: str | None = None


class EnableResponse(BaseModel):
    status: str
    name: str
    enabled: bool


class LogsResponse(BaseModel):
    name: str
    log_file: str | None = None
    lines: list[str]
    total_lines: int


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_scheduler() -> SubworkerScheduler:
    """Import and return the scheduler from app state.

    Avoids circular import by importing lazily.
    """
    from app.main import get_scheduler
    return get_scheduler()


def _get_config() -> ConfigManager:
    """Import and return the config manager from app state."""
    from app.main import get_config_manager
    return get_config_manager()


def _log_dir_for(name: str) -> Path | None:
    """Find the log directory for a subworker."""
    config = _get_config()
    sw = config.get_subworker(name)
    if not sw:
        return None
    if sw.workspace:
        return Path(sw.workspace) / "logs"
    base = config.subworkers_base_dir or Path.cwd()
    return base / "subworkers" / name / "workspace" / "logs"


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/status", response_model=StatusResponse)
async def get_all_status() -> StatusResponse:
    """Return status of all registered subworkers."""
    scheduler = _get_scheduler()
    config = _get_config()

    scheduler_status = scheduler.get_status()
    running_names = set(scheduler.get_running())

    subworkers = []
    for sw in config.subworkers:
        next_run = scheduler.get_next_run(sw.name)
        subworkers.append(SubworkerStatus(
            name=sw.name,
            enabled=sw.enabled,
            running=sw.name in running_names,
            next_run=next_run.isoformat() if next_run else None,
            schedule_type=sw.schedule.type.value if sw.schedule else None,
        ))

    return StatusResponse(
        scheduler_running=scheduler_status["scheduler_running"],
        total=len(subworkers),
        subworkers=subworkers,
    )


@router.get("/status/{name}", response_model=SubworkerDetail)
async def get_subworker_status(name: str) -> SubworkerDetail:
    """Return detailed status for a single subworker."""
    config = _get_config()
    scheduler = _get_scheduler()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    running_names = set(scheduler.get_running())
    next_run = scheduler.get_next_run(name)

    return SubworkerDetail(
        name=sw.name,
        enabled=sw.enabled,
        running=sw.name in running_names,
        next_run=next_run.isoformat() if next_run else None,
        schedule=sw.schedule.model_dump(),
        agent_id=sw.agent_id,
        timeout_minutes=sw.timeout_minutes,
        max_retries=sw.max_retries,
        model=sw.model,
    )


class TriggerRequest(BaseModel):
    """Optional prompt/model override for a manual trigger."""
    prompt: str | None = None
    model: str | None = None


class UpdateSubworkerRequest(BaseModel):
    """Editable fields for a subworker config."""
    agent_id: str | None = Field(default=None, description="OpenCode agent ID")
    model: str | None = Field(default=None, description="Model override (e.g. 'big-pickle')")
    timeout_minutes: int | None = Field(default=None, ge=1, le=120)
    max_retries: int | None = Field(default=None, ge=0, le=10)
    schedule: dict[str, Any] | None = Field(
        default=None,
        description="Schedule config: {'type':'interval','hours':[9,10,...],'minute':0} or {'type':'cron','expression':'0 9-23 * * *'}",
    )


class ReloadResponse(BaseModel):
    status: str
    added: list[str]
    removed: list[str]
    unchanged: list[str]
    total: int


@router.post("/trigger/{name}", response_model=TriggerResponse)
async def trigger_subworker(name: str, body: TriggerRequest | None = None) -> TriggerResponse:
    """Manually trigger a subworker immediately."""
    config = _get_config()
    scheduler = _get_scheduler()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    result = await scheduler.trigger_now(
        name,
        prompt=body.prompt if body else None,
        model=body.model if body else None,
    )

    if result.get("status") == "error":
        return TriggerResponse(
            status="error",
            name=name,
            message=result.get("message", "Unknown error"),
        )

    return TriggerResponse(
        status="triggered",
        name=name,
        message=f"Subworker '{name}' triggered successfully",
    )


@router.post("/enable/{name}", response_model=EnableResponse)
async def enable_subworker(name: str) -> EnableResponse:
    """Enable a subworker and add it to the scheduler."""
    config = _get_config()
    scheduler = _get_scheduler()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    if sw.enabled:
        return EnableResponse(status="already_enabled", name=name, enabled=True)

    updated = config.update_subworker(name, {"enabled": True})
    scheduler.add_subworker(updated)

    logger.info("subworker.enabled name=%s", name)
    return EnableResponse(status="enabled", name=name, enabled=True)


@router.post("/disable/{name}", response_model=EnableResponse)
async def disable_subworker(name: str) -> EnableResponse:
    """Disable a subworker and remove it from the scheduler."""
    config = _get_config()
    scheduler = _get_scheduler()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    if not sw.enabled:
        return EnableResponse(status="already_disabled", name=name, enabled=False)

    updated = config.update_subworker(name, {"enabled": False})
    scheduler.add_subworker(updated)

    logger.info("subworker.disabled name=%s", name)
    return EnableResponse(status="disabled", name=name, enabled=False)


@router.put("/status/{name}", response_model=SubworkerDetail)
async def update_subworker(name: str, body: UpdateSubworkerRequest) -> SubworkerDetail:
    """Edit a subworker's config (schedule, agent, model, timeouts).

    Updates in memory and refreshes the scheduler. Does NOT persist to disk.
    """
    config = _get_config()
    scheduler = _get_scheduler()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    updates: dict[str, object] = {}
    if body.agent_id is not None:
        updates["agent_id"] = body.agent_id
    if body.model is not None:
        updates["model"] = body.model
    if body.timeout_minutes is not None:
        updates["timeout_minutes"] = body.timeout_minutes
    if body.max_retries is not None:
        updates["max_retries"] = body.max_retries
    if body.schedule is not None:
        from app.config.models import CronSchedule, IntervalSchedule
        schedule_data = body.schedule
        schedule_type = schedule_data.get("type", "interval")
        if schedule_type == "cron":
            updates["schedule"] = CronSchedule(
                expression=schedule_data["expression"],
            )
        elif schedule_type == "interval":
            updates["schedule"] = IntervalSchedule(
                hours=schedule_data.get("hours", []),
                minute=schedule_data.get("minute", 0),
            )
        else:
            raise HTTPException(status_code=422, detail=f"Invalid schedule type: {schedule_type}")

    if not updates:
        raise HTTPException(status_code=422, detail="No fields to update")

    updated = config.update_subworker(name, updates)
    scheduler.add_subworker(updated)

    running_names = set(scheduler.get_running())
    next_run = scheduler.get_next_run(name)

    logger.info("subworker.updated name=%s fields=%s", name, list(updates.keys()))
    return SubworkerDetail(
        name=updated.name,
        enabled=updated.enabled,
        running=updated.name in running_names,
        next_run=next_run.isoformat() if next_run else None,
        schedule=updated.schedule.model_dump(),
        agent_id=updated.agent_id,
        timeout_minutes=updated.timeout_minutes,
        max_retries=updated.max_retries,
        model=updated.model,
    )


@router.post("/config/reload", response_model=ReloadResponse)
async def reload_config() -> ReloadResponse:
    """Hot-reload subworker configs from disk."""
    config = _get_config()
    scheduler = _get_scheduler()

    result = config.reload()
    await scheduler.reload_schedules(config.subworkers)

    logger.info("config.reloaded result=%s", result)
    return ReloadResponse(
        status="reloaded",
        added=result.get("added", []),
        removed=result.get("removed", []),
        unchanged=result.get("unchanged", []),
        total=result.get("total", 0),
    )


@router.get("/logs/{name}", response_model=LogsResponse)
async def get_subworker_logs(
    name: str,
    lines: int = 100,
) -> LogsResponse:
    """Return recent log lines for a subworker."""
    config = _get_config()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    log_dir = _log_dir_for(name)
    if not log_dir or not log_dir.exists():
        return LogsResponse(
            name=name,
            log_file=None,
            lines=[],
            total_lines=0,
        )

    # Find the most recent .log file
    log_files = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return LogsResponse(
            name=name,
            log_file=None,
            lines=[],
            total_lines=0,
        )

    log_file = log_files[0]
    try:
        all_lines = log_file.read_text().splitlines()
        recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return LogsResponse(
            name=name,
            log_file=str(log_file),
            lines=recent,
            total_lines=len(all_lines),
        )
    except OSError as exc:
        logger.warning("logs.read_error name=%s error=%s", name, str(exc))
        return LogsResponse(
            name=name,
            log_file=str(log_file),
            lines=[],
            total_lines=0,
        )


# ── Session Messages ───────────────────────────────────────────────────────

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
    time_created: int | None = None


class SessionMessage(BaseModel):
    info: SessionMessageInfo
    parts: list[SessionMessagePart]


class SessionResponse(BaseModel):
    name: str
    session_id: str | None = None
    messages: list[SessionMessage]
    total_messages: int


def _title_matches_subworker(session: dict, sw: Any) -> bool:
    """Check if a session title contains the subworker name.

    Normalizes hyphens/spaces so 'tiktok-content' matches 'TikTok content'.
    Subworker runs go through 'Sisyphus - ultraworker' agent, not the
    subworker's own agent_id, so we match by title instead.
    """
    if not sw.name:
        return False
    title = (session.get("title") or "").lower()
    name_normalized = sw.name.replace("-", " ")
    return name_normalized in title


@router.get("/sessions/{name}", response_model=SessionResponse)
async def get_subworker_sessions(
    name: str,
    limit: int = 50,
    session_id: str | None = None,
) -> SessionResponse:
    """Fetch OpenCode session messages for a subworker."""
    config = _get_config()
    scheduler = _get_scheduler()

    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    import os
    from app.utils.opencode_client import OpenCodeClient

    server_url = os.environ.get("OPENCODE_SERVER_URL", "http://host.docker.internal:4096")

    if not session_id:
        session_id = scheduler.get_last_session_id(name)

    async with OpenCodeClient(server_url, default_timeout=10.0) as client:
        if not session_id:
            all_sessions = await client.list_sessions(limit=2000)
            matching = [
                s for s in all_sessions
                if s.get("agent") == sw.agent_id
                or (sw.workspace and s.get("directory", "").startswith(sw.workspace))
                or _title_matches_subworker(s, sw)
            ]
            if matching:
                session_id = matching[-1].get("id")

        if not session_id:
            return SessionResponse(name=name, session_id=None, messages=[], total_messages=0)

        raw_messages = await client.list_messages(session_id, limit=limit)

    messages: list[SessionMessage] = []
    for msg in raw_messages:
        info_raw = msg.get("info", {})
        parts_raw = msg.get("parts", [])

        info = SessionMessageInfo(
            role=info_raw.get("role"),
            agent=info_raw.get("agent"),
            model=(info_raw.get("model") or {}).get("modelID"),
            time_created=(info_raw.get("time") or {}).get("created"),
        )

        parts: list[SessionMessagePart] = []
        for p in parts_raw:
            parts.append(SessionMessagePart(
                type=p.get("type", "unknown"),
                text=p.get("text"),
                tool=p.get("tool"),
                input=p.get("input") if isinstance(p.get("input"), dict) else None,
                output=p.get("output") if isinstance(p.get("output"), str) else None,
            ))

        messages.append(SessionMessage(info=info, parts=parts))

    return SessionResponse(
        name=name,
        session_id=session_id,
        messages=messages,
        total_messages=len(messages),
    )


class SessionListItem(BaseModel):
    session_id: str
    title: str | None = None
    agent: str | None = None
    model: str | None = None
    time_created: int | None = None
    message_count: int | None = None


class SessionListResponse(BaseModel):
    name: str
    sessions: list[SessionListItem]


@router.get("/sessions/{name}/list", response_model=SessionListResponse)
async def list_subworker_sessions(name: str) -> SessionListResponse:
    config = _get_config()
    sw = config.get_subworker(name)
    if not sw:
        raise HTTPException(status_code=404, detail=f"Subworker '{name}' not found")

    import os
    from app.utils.opencode_client import OpenCodeClient
    from app.utils.exceptions import OpenCodeConnectionError

    server_url = os.environ.get("OPENCODE_SERVER_URL", "http://host.docker.internal:4096")

    try:
        async with OpenCodeClient(server_url, default_timeout=10.0) as client:
            all_sessions = await client.list_sessions(limit=2000)
    except (OpenCodeConnectionError, Exception):
        return SessionListResponse(name=name, sessions=[])

    matching = [
        s for s in all_sessions
        if s.get("agent") == sw.agent_id
        or (sw.workspace and s.get("directory", "").startswith(sw.workspace))
        or _title_matches_subworker(s, sw)
    ]

    items = []
    for s in sorted(matching, key=lambda x: x.get("time", {}).get("created", 0) or 0, reverse=True):
        items.append(SessionListItem(
            session_id=s.get("id", ""),
            title=s.get("title"),
            agent=s.get("agent"),
            model=(s.get("model") or {}).get("modelID") if isinstance(s.get("model"), dict) else s.get("model"),
            time_created=(s.get("time") or {}).get("created"),
            message_count=s.get("messages"),
        ))

    return SessionListResponse(name=name, sessions=items)


# ── Main Agent Management ────────────────────────────────────────────────

MAIN_AGENT_FILE = Path(__file__).resolve().parent.parent / "config" / "main-agent.json"


class MainAgentResponse(BaseModel):
    name: str


class MainAgentSetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")


@router.get("/main-agent", response_model=MainAgentResponse)
async def get_main_agent() -> MainAgentResponse:
    try:
        if MAIN_AGENT_FILE.exists():
            data = __import__("json").loads(MAIN_AGENT_FILE.read_text())
            if isinstance(data, dict) and data.get("name"):
                return MainAgentResponse(name=data["name"])
    except Exception:
        pass
    return MainAgentResponse(name="elia")


@router.post("/main-agent", response_model=MainAgentResponse)
async def set_main_agent(body: MainAgentSetRequest) -> MainAgentResponse:
    MAIN_AGENT_FILE.write_text(__import__("json").dumps({"name": body.name}, indent=2) + "\n")
    return MainAgentResponse(name=body.name)
