"""Qwen SSE → WS bridge — background poller translating daemon events.

Polls GET /session/:id/events (Last-Event-ID resume + x-qwen-client-id) and
forwards live WS shapes WITHOUT changing them:

- agent text chunk  → run_log{name, text, field: "text"}
- agent thought     → run_log{name, text, field: "reasoning"}
- tool_*            → run_log{name, text, field: "tool"}
- turn_error        → failure banner + run completion broadcast
- turn_complete     → completion broadcast

Parser is tolerant: ignores ping/heartbeat/unknown frames, maps by
event-type string match (both Envelope {v,type,data} and flat shapes).
Stops on turn_complete / turn_error / session terminal / timeout.
"""
from __future__ import annotations

import asyncio
import json
import time

import httpx
import structlog

from app.config import get_settings
from app.qwen_client import QWEN_CLIENT_ID_HEADER, QwenSession

logger = structlog.get_logger(__name__)

STREAM_TIMEOUT_S = 600.0
SSE_READ_TIMEOUT_S = 660.0
MAX_TEXT_LEN = 4000
MAX_TOOL_LEN = 1200

STATS: dict[str, object] = {
    "streams_started": 0,
    "streams_completed": 0,
    "streams_error": 0,
    "streams_timeout": 0,
    "streams_stalled": 0,
    "run_log_text": 0,
    "run_log_reasoning": 0,
    "run_log_tool": 0,
    "banners": 0,
    "frames_ignored": 0,
    "frames_total": 0,
    "last_terminal": None,
}

_TASKS: dict[str, asyncio.Task] = {}


def stats_snapshot() -> dict[str, object]:
    """Copy of bridge counters + active stream count (no secrets)."""
    snap = dict(STATS)
    snap["active_streams"] = sum(1 for t in _TASKS.values() if not t.done())
    return snap


def start_stream(
    name: str,
    session: QwenSession,
    prompt_id: str | None,
    last_event_id: int | None = None,
) -> asyncio.Task:
    """Fire-and-forget SSE poller for one admitted prompt. Never raises."""
    key = f"{name}:{session.session_id}:{prompt_id or 'noid'}"
    STATS["streams_started"] = int(STATS["streams_started"]) + 1
    task = asyncio.ensure_future(_run_stream(name, session, prompt_id, last_event_id, key))
    _TASKS[key] = task
    task.add_done_callback(lambda _t: _TASKS.pop(key, None))
    return task


async def _run_stream(
    name: str,
    session: QwenSession,
    prompt_id: str | None,
    last_event_id: int | None,
    key: str,
) -> None:
    from app.routers.websocket import ws_manager

    settings = get_settings()
    headers = {
        "Authorization": f"Bearer {settings.QWEN_SERVER_TOKEN}",
        "Accept": "text/event-stream",
        QWEN_CLIENT_ID_HEADER: session.client_id,
    }
    if last_event_id is not None:
        headers["Last-Event-ID"] = str(last_event_id)
    url = f"{settings.QWEN_URL}/session/{session.session_id}/events"
    outcome = "stalled"
    try:
        async with asyncio.timeout(STREAM_TIMEOUT_S):
            async with httpx.AsyncClient(timeout=SSE_READ_TIMEOUT_S) as client:
                async with client.stream(
                    "GET", url, headers=headers, params={"connectReason": "prompt_restart"}
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        outcome = await _handle_line(
                            ws_manager, name, session.session_id, prompt_id, line
                        ) or outcome
                        if outcome in ("completed", "error"):
                            break
    except (asyncio.TimeoutError, TimeoutError):
        outcome = "timeout"
        logger.warning("bridge.timeout", name=name, session_id=session.session_id)
        await _broadcast(ws_manager, {
            "event": "run_banner",
            "name": name,
            "banner": {"type": "timeout", "session_id": session.session_id},
        })
        STATS["banners"] = int(STATS["banners"]) + 1
    except Exception as exc:
        outcome = "error"
        logger.warning("bridge.stream_error", name=name, error=type(exc).__name__)
    if outcome == "completed":
        STATS["streams_completed"] = int(STATS["streams_completed"]) + 1
    elif outcome == "error":
        STATS["streams_error"] = int(STATS["streams_error"]) + 1
    elif outcome == "timeout":
        STATS["streams_timeout"] = int(STATS["streams_timeout"]) + 1
    else:
        STATS["streams_stalled"] = int(STATS["streams_stalled"]) + 1
    STATS["last_terminal"] = f"{key} -> {outcome}"
    _mark_record(session.session_id, name, outcome)


async def _handle_line(ws_manager, name: str, session_id: str, prompt_id: str | None, line: str) -> str | None:
    """Parse one SSE line; forward WS events. Returns terminal outcome or None."""
    line = line.strip()
    if not line or line.startswith(":") or line.startswith("retry:"):
        return None
    if line.startswith("id:") or line.startswith("event:"):
        return None
    if not line.startswith("data:"):
        return None
    payload = line[5:].strip()
    if not payload or payload == "[DONE]":
        return None
    try:
        envelope = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(envelope, dict):
        return None
    STATS["frames_total"] = int(STATS["frames_total"]) + 1
    return await translate_envelope(ws_manager, name, session_id, prompt_id, envelope)


async def translate_envelope(ws_manager, name: str, session_id: str, prompt_id: str | None, envelope: dict) -> str | None:
    """Map one Qwen envelope to live WS shapes. Returns terminal outcome or None."""
    env_prompt = envelope.get("promptId")
    if prompt_id and isinstance(env_prompt, str) and env_prompt and env_prompt != prompt_id:
        STATS["frames_ignored"] = int(STATS["frames_ignored"]) + 1
        return None
    etype = str(envelope.get("type") or "")
    data = envelope.get("data")
    if not isinstance(data, dict):
        data = {}

    if etype == "session_update":
        await _forward_session_update(ws_manager, name, data)
        return None
    # Flat/legacy shapes (map by event-type string match).
    if etype in ("message_chunk", "agent_message_chunk"):
        text = _extract_text(data)
        if text:
            await _log(ws_manager, name, text, "text")
        return None
    if etype in ("reasoning", "agent_thought_chunk"):
        text = _extract_text(data)
        if text:
            await _log(ws_manager, name, text, "reasoning")
        return None
    if etype.startswith("tool_") or etype == "plan":
        await _log(ws_manager, name, _tool_preview(data), "tool")
        return None
    if etype == "turn_complete":
        if prompt_id and data.get("promptId") not in (None, prompt_id):
            return None
        await _broadcast(ws_manager, {"event": "subworker_completed", "name": name})
        return "completed"
    if etype == "turn_error":
        if prompt_id and data.get("promptId") not in (None, prompt_id):
            return None
        message = str(data.get("message") or "turn failed")
        code = data.get("code")
        await _broadcast(ws_manager, {
            "event": "run_banner",
            "name": name,
            "banner": {"type": "error", "code": code, "message": message[:1000]},
        })
        STATS["banners"] = int(STATS["banners"]) + 1
        await _broadcast(ws_manager, {"event": "subworker_failed", "name": name, "error": message[:500]})
        return "error"
    if etype in ("session_died", "session_closed"):
        reason = str(data.get("reason") or etype)
        await _broadcast(ws_manager, {
            "event": "run_banner",
            "name": name,
            "banner": {"type": "error", "message": f"session {etype}: {reason}"[:500]},
        })
        STATS["banners"] = int(STATS["banners"]) + 1
        await _broadcast(ws_manager, {"event": "subworker_failed", "name": name, "error": reason[:500]})
        return "error"
    STATS["frames_ignored"] = int(STATS["frames_ignored"]) + 1
    return None


async def _forward_session_update(ws_manager, name: str, data: dict) -> None:
    """Unwrap ACP sessionUpdate notifications into run_log fields."""
    update = data.get("update")
    if not isinstance(update, dict):
        update = data
    kind = str(update.get("sessionUpdate") or "")
    if kind == "agent_message_chunk":
        text = _extract_text(update.get("content"))
        if text:
            await _log(ws_manager, name, text, "text")
    elif kind == "agent_thought_chunk":
        text = _extract_text(update.get("content"))
        if text:
            await _log(ws_manager, name, text, "reasoning")
    elif kind.startswith("tool_") or kind == "plan":
        await _log(ws_manager, name, _tool_preview(update), "tool")
    else:
        STATS["frames_ignored"] = int(STATS["frames_ignored"]) + 1


def _extract_text(content: object) -> str | None:
    if isinstance(content, dict):
        if content.get("type") not in (None, "text"):
            return None
        text = content.get("text")
    elif isinstance(content, str):
        text = content
    else:
        return None
    if isinstance(text, str) and text:
        return text[:MAX_TEXT_LEN]
    return None


def _tool_preview(update: dict) -> str:
    title = update.get("title") or update.get("toolCallId") or update.get("kind") or "tool"
    status = update.get("status") or ""
    preview = {"tool": str(title)[:200]}
    if status:
        preview["status"] = str(status)[:50]
    raw = update.get("rawInput") or update.get("content")
    if isinstance(raw, dict):
        try:
            preview["input"] = json.dumps(raw, ensure_ascii=False)[:400]
        except (TypeError, ValueError):
            pass
    elif isinstance(raw, str) and raw:
        preview["input"] = raw[:400]
    return json.dumps(preview, ensure_ascii=False)[:MAX_TOOL_LEN]


async def _log(ws_manager, name: str, text: str, field: str) -> None:
    await _broadcast(ws_manager, {"event": "run_log", "name": name, "text": text, "field": field})
    key = f"run_log_{field}"
    if key in STATS:
        STATS[key] = int(STATS[key]) + 1


async def _broadcast(ws_manager, event: dict) -> None:
    try:
        await ws_manager.broadcast(event)
    except Exception as exc:
        logger.warning("bridge.broadcast_failed", error=type(exc).__name__)


def _mark_record(session_id: str, name: str, outcome: str) -> None:
    """Best-effort RunRecord close-out (lazy import avoids a router cycle)."""
    try:
        from app.routers import subworkers as subworkers_router

        for key, record in subworkers_router._runs.items():
            if record.session_id == session_id and record.name == name:
                if outcome == "completed":
                    record.status = "completed"
                elif outcome == "error":
                    record.status = "failed"
                if outcome in ("completed", "error") and record.ended_at is None:
                    record.ended_at = time.time()
                break
    except Exception:
        pass
