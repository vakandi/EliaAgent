"""Async httpx wrapper for the OpenCode server API (port 4096).

OpenCode runs on the host at http://127.0.0.1:4096 (port 4096).
VERIFIED endpoints (server v1.18.18):
  - GET  /global/health            → health check
  - GET  /session/                 → list sessions
  - POST /session                  → create session
  - GET  /session/{id}             → session info
  - GET  /session/status           → status MAP keyed by sessionID ({"type": "idle"|"busy"})
  - POST /session/{id}/message     → send message (body: {model, parts})
  - GET  /session/{id}/message     → list messages (?limit=N)

NOTE: endpoints like /session/create, /message, /message/list do NOT exist
on v1.18.18 — they return the SPA HTML. Use the REST routes above.
MCP servers are inherited from the host OpenCode config automatically.
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx
import structlog

from app.utils.exceptions import (
    OpenCodeConnectionError,
    OpenCodeError,
    OpenCodeSessionError,
    OpenCodeTimeoutError,
    RateLimitError,
)

# ── Default MCP servers shared by all subworker sessions ─────────────────
# These mirror the host OpenCode config at ~/.config/opencode/opencode.json.
# codegraph, context7, grep_app, lsp, websearch are OpenCode built-ins.
# parallel-browser-mcp is external (npm package, launched via npx).
DEFAULT_MCP_SERVERS: list[str] = [
    "codegraph",
    "context7",
    "grep_app",
    "lsp",
    "parallel-browser-mcp",
    "websearch",
]

log = structlog.get_logger()


class OpenCodeClient:
    """Async HTTP client for the local OpenCode server.

    Usage::

        async with OpenCodeClient("http://127.0.0.1:4096") as client:
            health = await client.health()
            session = await client.create_session(directory="/path/to/workspace")
            await client.send_message(session_id=session["id"], content="Hello")
            status = await client.wait_for_response(session["id"], timeout=120)
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:4096",
        default_timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._default_timeout = default_timeout
        self._client: httpx.AsyncClient | None = None

    # ── Context manager ──────────────────────────────────────────────────

    async def __aenter__(self) -> OpenCodeClient:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._default_timeout),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5),
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── Internal helpers ─────────────────────────────────────────────────

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise OpenCodeConnectionError("Client not initialized — use `async with OpenCodeClient()`")
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Execute an HTTP request with error mapping."""
        client = self._ensure_client()
        try:
            resp = await client.request(
                method,
                path,
                json=json,
                params=params,
                timeout=timeout or self._default_timeout,
                headers=headers,
            )
        except httpx.ConnectError as exc:
            raise OpenCodeConnectionError(f"Cannot connect to OpenCode at {self._base_url}: {exc}") from exc
        except httpx.TimeoutException as exc:
            raise OpenCodeTimeoutError(f"OpenCode request timed out after {timeout or self._default_timeout}s: {exc}") from exc

        if resp.status_code == 429:
            raise RateLimitError("OpenCode API rate limit exceeded", status_code=429)

        if resp.status_code >= 400:
            detail = resp.text[:500]
            raise OpenCodeError(
                f"OpenCode API error {resp.status_code} on {method} {path}",
                status_code=resp.status_code,
                detail=detail,
            )

        # Some endpoints return empty body on success
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    # ── Public API ───────────────────────────────────────────────────────

    @staticmethod
    def _model_payload(model: str | None) -> dict[str, str] | None:
        """Convert a model string to the server's model payload.

        Accepts ``"big-pickle"``, ``"opencode/big-pickle"`` or
        ``"provider/model"``. Provider defaults to ``"opencode"``.
        """
        if not model:
            return None
        provider, _, model_id = model.rpartition("/")
        return {
            "modelID": model_id or model,
            "providerID": provider or "opencode",
        }

    async def health(self) -> dict[str, Any]:
        """Check OpenCode server health.

        Returns: ``{"healthy": true, "version": "1.18.18"}``
        """
        return await self._request("GET", "/global/health")

    async def is_healthy(self) -> bool:
        """Return True if OpenCode server is reachable and healthy."""
        try:
            result = await self.health()
            return result.get("healthy", False)
        except OpenCodeConnectionError:
            return False

    async def list_sessions(self, limit: int = 100) -> list[dict[str, Any]]:
        """List recent OpenCode sessions.

        Args:
            limit: Max sessions returned by the server. The OpenCode API
                defaults to the 100 most recent sessions; raise this to reach
                older history.

        Returns list of session objects with id, slug, directory, title,
        agent, model, time, cost, tokens fields.
        """
        data = await self._request("GET", "/session/", params={"limit": limit})
        return data if isinstance(data, list) else []

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get info for a specific session.

        Args:
            session_id: Session ID (e.g. ``ses_ffe3fdaabffeWF558vML3OUh5O``).
        """
        return await self._request("GET", f"/session/{session_id}")

    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get session status (idle, busy, etc.).

        Returns ``{"type": "idle"}`` if session not found.
        """
        status_map = await self._request("GET", "/session/status")
        if not isinstance(status_map, dict):
            return {"type": "idle"}
        return status_map.get(session_id, {"type": "idle"})

    async def create_session(
        self,
        *,
        directory: str = "/",
        agent_id: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Create a new OpenCode session.

        Args:
            directory: Working directory for the session.
            agent_id: Agent to use (e.g. ``"gilfoyle"``).
            model: Model override (e.g. ``"big-pickle"``). Ignored at
                creation — the server rejects ``model`` in the POST /session
                body (BadRequest). Pass it to ``send_message`` instead.

        Returns: Session object with ``id`` field.
        """
        payload: dict[str, Any] = {"directory": directory}
        if agent_id:
            payload["agent"] = agent_id
        # OpenCode ignores body.directory — only this undocumented header
        # sets the session cwd. Without it every session lands in the server CWD.
        return await self._request(
            "POST",
            "/session",
            json=payload,
            headers={"x-opencode-directory": directory},
        )

    async def delete_session(self, session_id: str) -> dict[str, Any]:
        """Delete/close a session (verified: DELETE /session/{id} → true)."""
        return await self._request("DELETE", f"/session/{session_id}")

    async def send_message(
        self,
        session_id: str,
        content: str,
        *,
        model: str | None = None,
        variant: str | None = None,
        agent: str | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Send a user message to a session.

        This is the call that starts the agent working. Verified payload::

            {"agent": "my-agent",
             "model": {"modelID": "big-pickle", "providerID": "opencode"},
             "parts": [{"type": "text", "text": content}]}

        Args:
            session_id: Target session ID.
            content: Message text (typically the prompt).
            model: Model string (e.g. ``"big-pickle"``).
            variant: Reasoning effort variant (low/medium/high/max) for models
                that expose one — sent as the top-level ``variant`` field of
                the prompt body (see opencode PromptInput schema).
            agent: Agent that executes this prompt. ⚠️ MUST be set on every
                message — the agent is a property of the PROMPT INPUT, not of
                the session; omitting it lets oh-my-opencode's default
                (Sisyphus) take over the run.
            timeout: Request timeout in seconds.
        """
        payload: dict[str, Any] = {"parts": [{"type": "text", "text": content}]}
        if agent:
            payload["agent"] = agent
        model_payload = self._model_payload(model)
        if model_payload:
            payload["model"] = model_payload
        if variant:
            payload["variant"] = variant
        return await self._request(
            "POST",
            f"/session/{session_id}/message",
            json=payload,
            timeout=timeout,
        )

    async def list_models(self) -> dict[str, Any]:
        """Fetch provider/model catalog from the OpenCode server.

        Returns the raw ``GET /provider`` payload: ``all`` (provider list with
        nested ``models`` dicts), ``connected`` (provider ids with credentials),
        ``default``.
        """
        return await self._request("GET", "/provider", timeout=30.0)

    async def list_messages(
        self,
        session_id: str,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List messages in a session.

        Each message has ``info`` (id, sessionID, role, time, summary, agent,
        model) and ``parts`` (type: text/reasoning/step-start). Assistant
        text is in parts of type ``"text"``.

        Args:
            session_id: Target session ID.
            limit: Max messages to return.
        """
        data = await self._request(
            "GET",
            f"/session/{session_id}/message",
            params={"limit": limit},
        )
        return data if isinstance(data, list) else []

    async def wait_for_response(
        self,
        session_id: str,
        *,
        timeout: float = 120.0,
        poll_interval: float = 2.0,
        busy_grace: float = 0.5,
    ) -> dict[str, Any]:
        """Wait for the assistant to finish responding.

        Pre-check  — If the session already has assistant messages before
        polling starts, the work is done (completed before we got here).
        Returns immediately without entering the polling loop.

        Phase 1 — Wait for the session to become ``"busy"`` (processing
        started). A freshly created session is ``"idle"`` before the model
        begins work, so returning on the first idle would be a race
        condition.

        Phase 2 — Wait for the session to return to ``"idle"``
        (processing complete).

        Args:
            session_id: Target session ID.
            timeout: Max seconds to wait (total, across both phases).
            poll_interval: Seconds between polls.
            busy_grace: Extra seconds to wait *after* first seeing
                ``"busy"`` before switching to idle-wait, ensuring the
                model has fully started its work.
        """
        deadline = asyncio.get_event_loop().time() + timeout

        # Pre-check: if the session already has assistant messages,
        # it completed before we started polling. Skip both phases.
        messages = await self.list_messages(session_id)
        if any(m.get("info", {}).get("role") == "assistant" for m in messages):
            log.info("wait_for_response.pre_completed", session_id=session_id)
            return {"type": "idle"}

        saw_busy = False

        # Phase 1: wait for session to become busy
        while True:
            status = await self.get_session_status(session_id)
            if status.get("type") == "busy":
                saw_busy = True
                await asyncio.sleep(busy_grace)
                break
            if asyncio.get_event_loop().time() >= deadline:
                raise OpenCodeTimeoutError(
                    f"Session {session_id} never became busy within {timeout}s",
                    status_code=408,
                )
            await asyncio.sleep(poll_interval)

        # Phase 2: wait for session to return to idle
        while True:
            status = await self.get_session_status(session_id)
            if status.get("type") == "idle":
                return status
            if asyncio.get_event_loop().time() >= deadline:
                raise OpenCodeTimeoutError(
                    f"Session {session_id} did not complete within {timeout}s",
                    status_code=408,
                )
            await asyncio.sleep(poll_interval)

    async def run_prompt(
        self,
        prompt: str,
        *,
        directory: str = "/",
        agent_id: str | None = None,
        model: str | None = None,
        timeout: float = 1800.0,
    ) -> dict[str, Any]:
        """High-level helper: create session → send prompt → wait for response.

        This is the main entry point for running subworkers.

        Args:
            prompt: The prompt text to send.
            directory: Working directory.
            agent_id: Agent to use.
            model: Model override (sent with the message, not at creation).
            timeout: Max seconds for the full operation (default 30 min).

        Returns: ``{"session_id": ..., "status": ..., "messages": [...], "text": ...}``
        """
        session = await self.create_session(
            directory=directory,
            agent_id=agent_id,
        )
        session_id = session.get("id", "")
        log.info("opencode.session_created", session_id=session_id, agent=agent_id)

        await self.send_message(session_id, content=prompt, model=model, timeout=30.0)

        final_status = await self.wait_for_response(session_id, timeout=timeout)
        messages = await self.list_messages(session_id)
        text = self.extract_assistant_text(messages)

        return {
            "session_id": session_id,
            "status": final_status.get("type", "unknown"),
            "messages": messages,
            "text": text,
        }

    @staticmethod
    def extract_assistant_text(messages: list[dict[str, Any]]) -> str:
        """Extract the final assistant text from a message list.

        Concatenates ``parts[].text`` (type == "text") of the last assistant
        message. Returns "" when no assistant text is present.
        """
        for msg in reversed(messages):
            info = msg.get("info", {})
            if info.get("role") != "assistant":
                continue
            parts = msg.get("parts", [])
            texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
            if texts:
                return "\n".join(texts)
        return ""
