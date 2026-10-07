"""Qwen serve protocol client — session backend for the shim.

Qwen protocol (measured 2026-09-19 against daemon, qwen-code 0.24.1):
- POST /session               → 200 {sessionId, clientId, workspaceCwd}
- POST /session/:id/prompt    → 202 {promptId, lastEventId, eventEpoch}
  body {prompt: [{type: "text", text: str}]}, requires `x-qwen-client-id`
- POST /session/:id/model     → set session model {modelId} (best-effort per fallback step)
- GET  /session/:id/events    → SSE, requires `x-qwen-client-id` header
- GET  /health                → 200 (~2ms)
- GET  /daemon/status         → {uptime, version, workspaceCwd, ...}

Gap 9 (PROVEN): zen-free 429 FreeUsageLimitError admits prompts (202) but
emits zero SSE turn events. Mitigation here: exponential backoff + queue on
429 + model fallback across the 9 zen-free models (verified live against the
host gateway catalog 2026-09-19). Primary first: muse-spark-1.3.
"""
from __future__ import annotations

import asyncio
import json
import random
import time
from dataclasses import dataclass, field

import httpx
import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)

# 9 zen-free models, live gateway catalog 2026-09-19. Primary = spark-1.3
# (proven: 30/30 calls 200/202). Override via ZEN_FREE_MODELS env (CSV).
ZEN_FREE_MODELS: list[str] = [
    "muse-spark-1.3-contributor-free",
    "muse-spark-1.2-contributor-free",
    "big-pickle",
    "jev-1.13-free",
    "deepseek-v4-flash-free",
    "mimo-v2.5-free",
    "ling-3.0-flash-fin-free",
    "nemotron-3-ultra-free",
    "nemotron-3.5-lightning-free",
]

# Backoff schedule for 429 (seconds, with ±20% jitter): ~7min total per model.
BACKOFF_SCHEDULE: tuple[float, ...] = (5, 15, 30, 60, 120, 240)

QWEN_CLIENT_ID_HEADER = "x-qwen-client-id"


def fallback_models() -> list[str]:
    """Ordered model chain — env override wins, else ZEN_FREE_MODELS."""
    override = get_settings().MODEL_OVERRIDE
    return list(override) if override else list(ZEN_FREE_MODELS)


def is_rate_limited(status_code: int, body: str) -> bool:
    """True for 429s and provider FreeUsageLimitError payloads."""
    if status_code == 429:
        return True
    lowered = body.lower()
    return "freeusagelimit" in lowered or "rate limit" in lowered or "too many requests" in lowered


def backoff_delay(attempt: int) -> float:
    """Exponential backoff with jitter; clamps past the schedule end."""
    base = BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]
    return base * (0.8 + 0.4 * random.random())


@dataclass
class QwenSession:
    session_id: str
    client_id: str
    workspace_cwd: str
    model: str


@dataclass
class PromptResult:
    prompt_id: str
    model: str
    attempts: int
    waited_s: float
    last_event_id: int | None = None
    event_epoch: int | None = None


@dataclass
class QwenClient:
    """Thin async client over the Qwen daemon REST + SSE surface."""

    base_url: str = ""
    token: str = ""
    timeout_s: float = 30.0

    def __post_init__(self) -> None:
        settings = get_settings()
        if not self.base_url:
            self.base_url = settings.QWEN_URL
        if not self.token:
            self.token = settings.QWEN_SERVER_TOKEN

    def _headers(self, client_id: str | None = None) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self.token}"}
        if client_id:
            headers[QWEN_CLIENT_ID_HEADER] = client_id
        return headers

    async def health(self) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def daemon_status(self) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.get(
                f"{self.base_url}/daemon/status", headers=self._headers()
            )
            response.raise_for_status()
            return response.json()

    async def create_session(self, workspace_cwd: str) -> QwenSession:
        """POST /session → 200 {sessionId, clientId, workspaceCwd}."""
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.post(
                f"{self.base_url}/session",
                headers=self._headers(),
                json={"workspaceCwd": workspace_cwd},
            )
            response.raise_for_status()
            data = response.json()
            return QwenSession(
                session_id=data["sessionId"],
                client_id=data["clientId"],
                workspace_cwd=data.get("workspaceCwd", workspace_cwd),
                model=data.get("model", fallback_models()[0]),
            )

    async def send_prompt(
        self,
        session: QwenSession,
        prompt: str,
        *,
        models: list[str] | None = None,
    ) -> PromptResult:
        """POST /session/:id/prompt → 202 {promptId, lastEventId, eventEpoch}.

        Body is a content-block array: {prompt: [{type: "text", text}]}.
        Sends `x-qwen-client-id` header. 429 → backoff, then next model.

        Walks the fallback chain model by model; each model gets a full
        BACKOFF_SCHEDULE of prompt retries before falling through. Raises
        RuntimeError when every model is exhausted (caller queues + alerts).
        """
        chain = models or fallback_models()
        waited = 0.0
        attempts = 0
        last_error = "no models configured"
        for model in chain:
            for attempt in range(len(BACKOFF_SCHEDULE) + 1):
                attempts += 1
                try:
                    async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                        response = await client.post(
                            f"{self.base_url}/session/{session.session_id}/prompt",
                            headers=self._headers(session.client_id),
                            json={"prompt": [{"type": "text", "text": prompt}]},
                        )
                    if response.status_code == 202:
                        data = response.json()
                        logger.info(
                            "qwen.prompt_admitted",
                            session_id=session.session_id,
                            model=model,
                            attempts=attempts,
                        )
                        return PromptResult(
                            prompt_id=data["promptId"],
                            model=model,
                            attempts=attempts,
                            waited_s=waited,
                            last_event_id=data.get("lastEventId"),
                            event_epoch=data.get("eventEpoch"),
                        )
                    body = response.text
                    if is_rate_limited(response.status_code, body):
                        last_error = f"{model}: 429 (attempt {attempt + 1})"
                        logger.warning("qwen.rate_limited", model=model, attempt=attempt + 1)
                    else:
                        response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    last_error = f"{model}: HTTP {exc.response.status_code}"
                    logger.warning("qwen.prompt_http_error", model=model, error=last_error)
                except (httpx.ConnectError, httpx.TimeoutException) as exc:
                    last_error = f"{model}: transport {type(exc).__name__}"
                    logger.warning("qwen.prompt_transport_error", model=model, error=last_error)
                if attempt < len(BACKOFF_SCHEDULE):
                    delay = backoff_delay(attempt)
                    waited += delay
                    await asyncio.sleep(delay)
            logger.warning("qwen.model_exhausted", model=model, trying_next=True)
        raise RuntimeError(f"all {len(chain)} fallback models exhausted; last: {last_error}")

    async def stream_events(
        self,
        session: QwenSession,
        last_event_id: str | None = None,
    ) -> list[dict]:
        """GET /session/:id/events (SSE) — buffered read of pending events.

        Long-lived streaming belongs to the WS bridge; this returns whatever
        events are currently available so routers stay request-scoped.
        """
        url = f"{self.base_url}/session/{session.session_id}/events"
        params = {"lastEventId": last_event_id} if last_event_id else None
        events: list[dict] = []
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            try:
                async with client.stream(
                    "GET", url, headers=self._headers(session.client_id), params=params
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        payload = line[5:].strip()
                        if payload == "[DONE]":
                            break
                        try:
                            events.append(json.loads(payload))
                        except json.JSONDecodeError:
                            logger.warning("qwen.sse_unparseable", line=payload[:200])
            except httpx.RemoteProtocolError:
                # Daemon closes SSE streams abruptly on turn end/fail/disconnect.
                # Abrupt EOF is normal here: return frames collected so far.
                logger.info("qwen.sse_eof", frames=len(events))
        return events


@dataclass
class RunRecord:
    name: str
    session_id: str
    client_id: str
    prompt_id: str | None = None
    model: str = ""
    status: str = "running"
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
