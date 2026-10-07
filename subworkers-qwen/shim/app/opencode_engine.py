"""opencode run subprocess backend — ENGINE for trigger/continue turns.

Engine swap 2026-09-19: the Qwen daemon NEVER executes turns (provider
hard-gates non-opencode clients; proven 0/8 + 0/8 probes). This module runs
`opencode run --format json` as an async subprocess in the agent workspace
(same models/auth as live: zen-free provider via the baked-in opencode.json)
and translates line-delimited JSON events to (field, text) pairs for the
unchanged TopBar WS shapes: run_log{name,text,field}, run_banner,
subworker_completed / subworker_failed.

NOTE: QWEN path (app/qwen_client.py + app/stream_bridge.py) is intentionally
left dormant, not deleted.

Single attempt per turn, no retries: any 429 / FreeUsageLimit signal raises
OpencodeRateLimited immediately (caller marks queued_429). Max 3 live
`opencode run` invocations per swap ticket; stop on 429 and report.
"""
from __future__ import annotations

import asyncio
import json
import structlog
from collections.abc import AsyncIterator
from typing import Any

from app.qwen_client import fallback_models

logger = structlog.get_logger(__name__)

MAX_TEXT_LEN = 4000
MAX_TOOL_LEN = 1200
RUN_TIMEOUT_S = 300.0

RATE_MARKERS = ("429", "freeusagelimit", "rate limit", "too many requests")

STATS: dict[str, object] = {
    "runs_started": 0,
    "runs_completed": 0,
    "runs_error": 0,
    "runs_rate_limited": 0,
    "run_log_text": 0,
    "run_log_reasoning": 0,
    "run_log_tool": 0,
    "frames_ignored": 0,
    "frames_stored": 0,
    "lines_total": 0,
    "last_session": None,
}


class OpencodeRateLimited(RuntimeError):
    """Provider 429 / free-tier limit hit — caller queues, never retries."""


def stats_snapshot() -> dict[str, object]:
    """Copy of engine counters (no secrets)."""
    return dict(STATS)


def _bump(key: str) -> None:
    if key in STATS and isinstance(STATS[key], int):
        STATS[key] = int(STATS[key]) + 1


_FRAMES: dict[str, list[dict[str, str]]] = {}
MAX_FRAMES_PER_RUN = 2000


def store_frame(run_key: str, field: str, text: str) -> None:
    """Append one translated frame for later events-route replay (in-memory)."""
    frames = _FRAMES.setdefault(run_key, [])
    frames.append({"field": field, "text": text})
    if len(frames) > MAX_FRAMES_PER_RUN:
        del frames[: len(frames) - MAX_FRAMES_PER_RUN]
    _bump("frames_stored")


def get_frames(run_key: str) -> list[dict[str, str]]:
    """Replay stored frames (copies; reads never drain the store)."""
    return [dict(frame) for frame in _FRAMES.get(run_key, [])]


def _truncate(text: str, limit: int) -> str:
    return text[:limit] if len(text) > limit else text


def _tool_preview(tool: str, extra: dict[str, Any] | None = None) -> str:
    preview: dict[str, Any] = {"tool": str(tool)[:200]}
    if extra:
        for key in ("status", "state", "input", "title"):
            value = extra.get(key)
            if isinstance(value, str) and value:
                preview[key] = value[:400]
            elif isinstance(value, dict):
                try:
                    preview[key] = json.dumps(value, ensure_ascii=False)[:400]
                except (TypeError, ValueError):
                    pass
    return _truncate(json.dumps(preview, ensure_ascii=False), MAX_TOOL_LEN)


def _part_text(part: dict[str, Any], props: dict[str, Any]) -> str | None:
    for source in (part, props):
        for key in ("text", "delta", "content"):
            value = source.get(key)
            if isinstance(value, str) and value:
                return _truncate(value, MAX_TEXT_LEN)
    return None


def _extract_data_text(event: dict[str, Any]) -> str | None:
    """Legacy bridge shape: text nested under event['data'] (dict or str)."""
    data = event.get("data")
    if isinstance(data, dict):
        for key in ("content", "text"):
            value = data.get(key)
            if isinstance(value, dict):
                text = _part_text(value, {})
                if text:
                    return text
            elif isinstance(value, str) and value:
                return _truncate(value, MAX_TEXT_LEN)
    elif isinstance(data, str) and data:
        return _truncate(data, MAX_TEXT_LEN)
    return None


def translate_event(event: dict[str, Any]) -> tuple[str, str] | None:
    """Map one `opencode run --format json` event to a (field, text) pair.

    Tolerant by design: handles server-event envelopes
    {type, properties:{part, delta}}, flat part shapes {type, text}, and the
    legacy Qwen envelope kinds (message_chunk / agent_thought_chunk / tool_*).
    Returns None for ignorable frames (steps, heartbeats, session bookkeeping).
    """
    if not isinstance(event, dict):
        return None
    etype = str(event.get("type") or event.get("kind") or event.get("event") or "")
    props = event.get("properties")
    if not isinstance(props, dict):
        props = {}
    part = props.get("part")
    if not isinstance(part, dict):
        part = event.get("part")
    node = part if isinstance(part, dict) else event
    ptype = str(node.get("type") or "")

    # Legacy Qwen envelope kinds (kept so the map stays a superset of the bridge).
    if etype in ("message_chunk", "agent_message_chunk"):
        text = _part_text(node, props) or _extract_data_text(event)
        return ("text", text) if text else None
    if etype in ("reasoning", "agent_thought_chunk"):
        text = _part_text(node, props) or _extract_data_text(event)
        return ("reasoning", text) if text else None

    if ptype == "text":
        text = _part_text(node, props)
        return ("text", text) if text else None
    if ptype == "reasoning":
        text = _part_text(node, props)
        return ("reasoning", text) if text else None
    if ptype == "tool":
        return ("tool", _tool_preview(str(node.get("tool") or "tool"), node))
    if ptype in ("file", "patch", "agent"):
        label = str(node.get("filename") or node.get("name") or ptype)
        return ("tool", _tool_preview(label, node))
    if etype.startswith("tool_") or etype == "plan" or ptype.startswith("tool_"):
        return ("tool", _tool_preview(str(node.get("tool") or node.get("title") or "tool"), node))
    # Deltas without a part wrapper (message.part.updated flat shape).
    delta = props.get("delta")
    if isinstance(delta, str) and delta:
        if "reason" in etype or "think" in etype or "thought" in etype:
            return ("reasoning", _truncate(delta, MAX_TEXT_LEN))
        return ("text", _truncate(delta, MAX_TEXT_LEN))
    return None


def _captured_session_id(event: dict[str, Any]) -> str | None:
    """Scrape the opencode session id from any known nesting level."""
    candidates: list[Any] = [event.get("sessionID"), event.get("sessionId"), event.get("session_id")]
    props = event.get("properties")
    if isinstance(props, dict):
        candidates += [props.get("sessionID"), props.get("sessionId"), props.get("session_id")]
        info = props.get("info")
        if isinstance(info, dict):
            candidates += [info.get("sessionID"), info.get("sessionId"), info.get("session_id")]
    for value in candidates:
        if isinstance(value, str) and value:
            return value
    return None


def _is_rate_limited_blob(blob: str) -> bool:
    lowered = blob.lower()
    return any(marker in lowered for marker in RATE_MARKERS)


async def _rotate_egress() -> str:
    """Force pool rotation after an engine 429 (best-effort, never raises)."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("http://qwen:3128/__rotate")
            egress = resp.json().get("egress", "?")
            logger.warning("engine.rotated_on_429", egress=egress)
            return str(egress)
    except Exception as exc:
        logger.warning("engine.rotate_failed", error=type(exc).__name__)
        return "rotate-failed"


async def run_turn(
    workspace: str,
    prompt: str,
    model: str | None = None,
    session_id: str | None = None,
    *,
    capture: dict[str, str | None] | None = None,
    timeout_s: float = RUN_TIMEOUT_S,
    run_key: str | None = None,
    variant: str | None = None,
    _retried: bool = False,
) -> AsyncIterator[tuple[str, str]]:
    """Stream one turn as (field, text) pairs via `opencode run --format json`.

    New run: session_id=None (opencode mints one; scraped from events into
    capture["session_id"]). Follow-up: pass the stored opencode session id
    (continuation via --session). Single attempt, no retries. When run_key is
    set, translated frames are also stored for the events route replay.
    """
    resolved = model or fallback_models()[0]
    # Native `opencode/` provider: proven live in-container (PONG18); the
    # zen-free gateway path 403/500s non-opencode clients. Bare ids map here.
    full_model = resolved if "/" in resolved else f"opencode/{resolved}"
    cmd = ["opencode", "run", "--format", "json", "-m", full_model, "--dir", workspace]
    if session_id:
        cmd += ["-s", session_id]
    cmd.append(prompt)

    STATS["runs_started"] = int(STATS["runs_started"]) + 1
    logger.info("opencode.run_start", model=full_model, continuing=bool(session_id))
    # Egress rotation (2026-09-20): engine subprocesses exit via the
    # container-local rotating pool (qwen:3128, LRU + 4-min timer), NOT the
    # host gateway and never direct — otherwise they share one fixed egress
    # IP and eat raw 429s. Compose-internal + loopback targets bypass it.
    import os as _os
    _proxy_env = {
        "HTTP_PROXY": "http://qwen:3128",
        "HTTPS_PROXY": "http://qwen:3128",
        "http_proxy": "http://qwen:3128",
        "https_proxy": "http://qwen:3128",
        "NO_PROXY": "localhost,127.0.0.1,::1,qwen,shim",
        "no_proxy": "localhost,127.0.0.1,::1,qwen,shim",
    }
    _child_env = dict(_os.environ, **_proxy_env)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=workspace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=_child_env,
    )
    assert proc.stdout is not None
    assert proc.stderr is not None

    found_session: str | None = None
    saw_429 = False
    error_msg: str | None = None
    gen = _drain(proc, timeout_s)
    try:
        async for field, text in gen:
            if field == "__session__":
                found_session = text
                continue
            if field == "__rate_limited__":
                saw_429 = True
                continue
            if field == "__error__":
                error_msg = text
                continue
            _bump(f"run_log_{field}")
            if run_key is not None:
                store_frame(run_key, field, text)
            yield field, text
    finally:
        await gen.aclose()
        if capture is not None:
            capture["session_id"] = found_session or session_id
        if found_session:
            STATS["last_session"] = found_session

    stderr_tail = await _read_stderr_tail(proc)
    try:
        await asyncio.wait_for(proc.wait(), timeout=10)
    except asyncio.TimeoutError:
        proc.kill()
    returncode = proc.returncode
    if saw_429 or (stderr_tail and _is_rate_limited_blob(stderr_tail)):
        STATS["runs_rate_limited"] = int(STATS["runs_rate_limited"]) + 1
        if not _retried:
            # Same-turn recovery: fresh egress IP, then one more attempt.
            # A second 429 falls through to the queue path below as before.
            await _rotate_egress()
            async for pair in run_turn(
                workspace, prompt, model, session_id,
                capture=capture, timeout_s=timeout_s, run_key=run_key,
                variant=variant, _retried=True,
            ):
                yield pair
            return
        raise OpencodeRateLimited(f"zen-free 429 on model {full_model}")
    if returncode not in (0, None) or error_msg:
        STATS["runs_error"] = int(STATS["runs_error"]) + 1
        raise RuntimeError(f"opencode run failed (rc={returncode}): {(error_msg or stderr_tail or 'no output')[:300]}")
    STATS["runs_completed"] = int(STATS["runs_completed"]) + 1


async def _drain(
    proc: asyncio.subprocess.Process,
    timeout_s: float,
) -> AsyncIterator[tuple[str, str]]:
    """Read stdout JSON lines until EOF; internal control frames use __-fields."""
    try:
        async with asyncio.timeout(timeout_s):
            assert proc.stdout is not None
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                STATS["lines_total"] = int(STATS["lines_total"]) + 1
                raw = line.decode("utf-8", errors="replace").strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    if _is_rate_limited_blob(raw):
                        yield "__rate_limited__", raw[:200]
                    else:
                        STATS["frames_ignored"] = int(STATS["frames_ignored"]) + 1
                    continue
                if not isinstance(event, dict):
                    STATS["frames_ignored"] = int(STATS["frames_ignored"]) + 1
                    continue
                if _is_rate_limited_blob(raw):
                    yield "__rate_limited__", raw[:200]
                etype = str(event.get("type") or "")
                if etype in ("session.error", "error", "turn_error"):
                    detail = json.dumps(event, ensure_ascii=False)[:500]
                    yield "__error__", detail
                    continue
                scraped = _captured_session_id(event)
                if scraped:
                    yield "__session__", scraped
                pair = translate_event(event)
                if pair is None:
                    STATS["frames_ignored"] = int(STATS["frames_ignored"]) + 1
                    continue
                yield pair
    except (asyncio.TimeoutError, TimeoutError):
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        raise RuntimeError("opencode run timed out")
    finally:
        try:
            await asyncio.wait_for(proc.wait(), timeout=15.0)
        except (asyncio.TimeoutError, TimeoutError):
            try:
                proc.kill()
            except ProcessLookupError:
                pass


async def _read_stderr_tail(proc: asyncio.subprocess.Process) -> str:
    try:
        assert proc.stderr is not None
        raw = await asyncio.wait_for(proc.stderr.read(), timeout=10.0)
        text = raw.decode("utf-8", errors="replace").strip()
        return text[-2000:] if len(text) > 2000 else text
    except Exception:
        return ""
