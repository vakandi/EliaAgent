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

from app.routes.websocket import ws_manager
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
    schedule: dict[str, Any] | None = None
    model: str | None = None
    variant: str | None = None


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
            schedule=sw.schedule.model_dump() if sw.schedule else None,
            model=sw.model,
            variant=sw.variant,
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
    variant: str | None = None


class UpdateSubworkerRequest(BaseModel):
    """Editable fields for a subworker config."""
    agent_id: str | None = Field(default=None, description="OpenCode agent ID")
    model: str | None = Field(default=None, description="Model override (e.g. 'big-pickle')")
    variant: str | None = Field(default=None, description="Reasoning effort variant (low/medium/high/max)")
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
        variant=body.variant if body else None,
    )

    await ws_manager.broadcast_status_update()
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
    await ws_manager.broadcast_status_update()
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
    await ws_manager.broadcast_status_update()
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
    if body.variant is not None:
        updates["variant"] = body.variant
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
    await ws_manager.broadcast_status_update()
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
        variant=updated.variant,
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

    async with OpenCodeClient(server_url, default_timeout=10.0) as client:
        if not session_id:
            # Newest session in the agent's workspace wins — the scheduler
            # state can be stale after container restarts.
            ws_dir = _effective_workspace(sw)
            all_sessions = await client.list_sessions(limit=2000)
            matching = [
                s for s in all_sessions
                if s.get("agent") == sw.agent_id
                or s.get("directory", "").startswith(ws_dir)
                or _title_matches_subworker(s, sw)
            ]
            if matching:
                matching.sort(
                    key=lambda x: (x.get("time") or {}).get("created", 0) or 0,
                    reverse=True,
                )
                session_id = matching[0].get("id")

        if not session_id:
            session_id = scheduler.get_last_session_id(name)

        if not session_id:
            return SessionResponse(name=name, session_id=None, messages=[], total_messages=0)

        raw_messages = await client.list_messages(session_id, limit=limit)

    messages: list[SessionMessage] = []
    for msg in raw_messages:
        info_raw = msg.get("info", {})
        parts_raw = msg.get("parts", [])

        raw_model = info_raw.get("model")
        if isinstance(raw_model, dict):
            msg_model = raw_model.get("modelID")
            msg_variant = raw_model.get("variant")
        else:
            # assistant messages carry flat modelID/variant fields
            msg_model = info_raw.get("modelID")
            msg_variant = info_raw.get("variant")
        info = SessionMessageInfo(
            role=info_raw.get("role"),
            agent=info_raw.get("agent"),
            model=msg_model,
            variant=msg_variant if isinstance(msg_variant, str) else None,
            time_created=(info_raw.get("time") or {}).get("created"),
        )

        parts: list[SessionMessagePart] = []
        for p in parts_raw:
            # OpenCode nests tool payload under state: {status, input, output, ...}
            state = p.get("state") if isinstance(p.get("state"), dict) else {}
            tool_input = state.get("input", p.get("input"))
            tool_output = state.get("output", p.get("output"))
            if isinstance(tool_output, str) and len(tool_output) > 8000:
                tool_output = tool_output[:8000] + "\n… (truncated)"
            parts.append(SessionMessagePart(
                type=p.get("type", "unknown"),
                text=p.get("text"),
                tool=p.get("tool"),
                input=tool_input if isinstance(tool_input, dict) else None,
                output=tool_output if isinstance(tool_output, str) else None,
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



def _effective_workspace(sw) -> str:
    """HOST-side workspace for a subworker — mirrors SubworkerRunner logic,
    including the /data → OPENCODE_WORKSPACE mapping (config stores
    container paths; opencode sessions carry host paths)."""
    import os as _os

    root = _os.environ.get("OPENCODE_WORKSPACE") or str(Path.home() / "EliaAI")
    workspace = sw.workspace
    if not workspace:
        try:
            main_file = _main_agent_file()
            if main_file.exists():
                data = __import__("json").loads(main_file.read_text())
                if isinstance(data, dict) and data.get("name") == sw.agent_id:
                    return root
        except Exception:
            pass
        workspace = f"/data/subworkers/{sw.name}/workspace"
    if root and workspace.startswith("/data/"):
        workspace = workspace.replace("/data/", f"{root}/", 1)
    elif root and workspace == "/data":
        workspace = root
    return workspace


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

    ws_dir = _effective_workspace(sw)
    matching = [
        s for s in all_sessions
        if s.get("agent") == sw.agent_id
        or s.get("directory", "").startswith(ws_dir)
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

# Favorites surface first in UI model lists; everything else follows.
FAVORITE_MODELS = [
    "opencode/x-preview-f-free",
    "opencode/big-pickle",
    "opencode/nemotron-3.5-lightning-free",
    "opencode/nemotron-3-ultra-free",
    "opencode/hy3-free",
    "opencode/laguna-s-2.1-free",
    "opencode/mimo-v2.5-free",
    "opencode/deepseek-v4-flash-free",
    "google/gemini-2.5-flash-lite",
    "google/gemma-4-26b-a4b-it",
    "google/gemma-4-31b-it",
]


class ModelOption(BaseModel):
    id: str
    name: str
    provider: str
    reasoning: bool = False
    variants: list[str] = []


class ModelsResponse(BaseModel):
    models: list[ModelOption]
    total: int


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """All models from connected OpenCode providers, favorites first."""
    import os

    from app.utils.opencode_client import OpenCodeClient

    server_url = os.environ.get("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")
    async with OpenCodeClient(server_url, default_timeout=30.0) as client:
        raw = await client.list_models()

    connected = set(raw.get("connected") or [])
    options: list[ModelOption] = []
    for provider in raw.get("all", []):
        pid = provider.get("id", "")
        if connected and pid not in connected:
            continue
        for mid, m in (provider.get("models") or {}).items():
            variants = sorted((m.get("variants") or {}).keys())
            options.append(
                ModelOption(
                    id=f"{pid}/{mid}",
                    name=m.get("name") or mid,
                    provider=pid,
                    reasoning=bool((m.get("capabilities") or {}).get("reasoning")),
                    variants=variants,
                )
            )

    by_id = {o.id: o for o in options}
    ordered = [by_id.pop(fid) for fid in FAVORITE_MODELS if fid in by_id]
    ordered.extend(sorted(by_id.values(), key=lambda o: o.id.lower()))
    return ModelsResponse(models=ordered, total=len(ordered))


def _main_agent_file() -> Path:
    # Must match SubworkerRunner._read_main_agent_name(): bind-mounted
    # subworkers dir in Docker, repo fallback for local dev.
    data_path = Path("/data/subworkers/main-agent.json")
    if data_path.parent.is_dir():
        return data_path
    return Path.home() / "EliaAI" / "subworkers" / "main-agent.json"


class MainAgentResponse(BaseModel):
    name: str


class MainAgentSetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")


@router.get("/main-agent", response_model=MainAgentResponse)
async def get_main_agent() -> MainAgentResponse:
    try:
        main_file = _main_agent_file()
        if main_file.exists():
            data = __import__("json").loads(main_file.read_text())
            if isinstance(data, dict) and data.get("name"):
                return MainAgentResponse(name=data["name"])
    except Exception:
        pass
    return MainAgentResponse(name="elia")


@router.post("/main-agent", response_model=MainAgentResponse)
async def set_main_agent(body: MainAgentSetRequest) -> MainAgentResponse:
    _main_agent_file().write_text(__import__("json").dumps({"name": body.name}, indent=2) + "\n")
    await ws_manager.broadcast_status_update()
    return MainAgentResponse(name=body.name)
