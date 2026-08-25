"""SubworkerRunner — HTTP client invocation, retry, session recovery, validation.

Orchestrates: health check → invoke OpenCode via HTTP → capture output → validate → retry.
"""
from __future__ import annotations

import asyncio
import os
import random
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Coroutine

from app.config.models import SubworkerConfig
from app.services.error_parser import ErrorParser, ErrorType
from app.utils.exceptions import (
    OpenCodeConnectionError,
    OpenCodeError,
    OpenCodeSessionError,
    OpenCodeTimeoutError,
    RateLimitError,
)
import structlog

from app.utils.opencode_client import OpenCodeClient

log = structlog.get_logger(__name__)

# ── Constants ───────────────────────────────────────────────────────────
COMPLETION_MARKER = "<promise>DONE</promise>"
SESSION_ID_PATTERN = re.compile(r"ses_[A-Za-z0-9]+")
EXIT_TIMEOUT = 124
EXIT_CRASH = 137
BACKOFF_MIN_SECONDS = 20.0
BACKOFF_MAX_SECONDS = 35.0
MIN_OUTPUT_LINES = 5


# ── Enums & dataclasses ────────────────────────────────────────────────

class RunPhase(str, Enum):
    HEALTH_CHECK = "health_check"
    INVOKE = "invoke"
    VALIDATE = "validate"
    RETRY = "retry"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RunAttempt:
    """Record of a single execution attempt."""
    attempt_number: int
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    session_id: str | None = None
    retriable: bool = False
    error_type: ErrorType | None = None


@dataclass
class RunResult:
    """Final result of a subworker run (after all attempts)."""
    success: bool
    subworker_name: str
    total_attempts: int = 0
    final_phase: RunPhase = RunPhase.FAILED
    attempts: list[RunAttempt] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    session_id: str | None = None
    stdout: str = ""
    stderr: str = ""
    error_message: str | None = None


# ── Type aliases ────────────────────────────────────────────────────────
RunCallback = Callable[[RunPhase, str], Coroutine[Any, Any, None]]


# ── Runner ──────────────────────────────────────────────────────────────

class SubworkerRunner:
    """Invokes the opencode CLI for a subworker with retry + session recovery.

    Usage::

        runner = SubworkerRunner(config)
        result = await runner.run_subworker()
    """

    def __init__(
        self,
        config: SubworkerConfig,
        *,
        opencode_bin: str = "opencode",
        log_dir: str | Path | None = None,
        health_check_fn: Callable[[], Coroutine[Any, Any, bool]] | None = None,
        prompt_override: str | None = None,
        model_override: str | None = None,
        variant_override: str | None = None,
    ) -> None:
        self._config = config
        self._opencode_bin = opencode_bin
        self._log_dir = Path(log_dir) if log_dir else None
        self._health_check = health_check_fn
        self._prompt_override = prompt_override
        self._model_override = model_override
        self._variant_override = variant_override
        self._callbacks: list[RunCallback] = []

    # ── Public API ───────────────────────────────────────────────────────

    def on_phase_change(self, callback: RunCallback) -> None:
        self._callbacks.append(callback)

    async def run_subworker(self) -> RunResult:
        """Orchestrate: health check → invoke → validate → retry."""
        result = RunResult(
            success=False,
            subworker_name=self._config.name,
        )
        start_time = time.time()

        # ── Health check ─────────────────────────────────────────────
        await self._notify(RunPhase.HEALTH_CHECK, "checking OpenCode health")
        if self._health_check:
            healthy = await self._health_check()
            if not healthy:
                result.error_message = "OpenCode health check failed"
                result.final_phase = RunPhase.FAILED
                result.total_duration_seconds = time.time() - start_time
                return result

        # ── Execution loop ───────────────────────────────────────────
        max_attempts = self._config.max_retries + 1
        recovered_session_id: str | None = None

        for attempt_num in range(1, max_attempts + 1):
            attempt = await self._execute_single_attempt(
                attempt_num,
                recovered_session_id,
            )
            result.attempts.append(attempt)
            result.total_attempts = attempt_num

            # ── Extract session for recovery ─────────────────────────
            extracted = attempt.session_id or self._extract_session_id(attempt.stdout)
            if extracted:
                attempt.session_id = extracted
                result.session_id = extracted
                recovered_session_id = extracted

            # ── Success ──────────────────────────────────────────────
            if attempt.exit_code == 0:
                validation = self._validate_run(attempt)
                if validation["valid"]:
                    result.success = True
                    result.final_phase = RunPhase.COMPLETED
                    result.stdout = attempt.stdout
                    result.stderr = attempt.stderr
                    break

            # ── Should retry? ────────────────────────────────────────
            if attempt_num < max_attempts and attempt.retriable:
                delay = random.uniform(BACKOFF_MIN_SECONDS, BACKOFF_MAX_SECONDS)
                await self._notify(
                    RunPhase.RETRY,
                    f"attempt {attempt_num} failed ({attempt.error_type}), "
                    f"retrying in {delay:.0f}s",
                )
                await asyncio.sleep(delay)
            else:
                result.final_phase = RunPhase.FAILED
                result.error_message = (
                    attempt.stderr[:500] if attempt.stderr
                    else f"exit code {attempt.exit_code}"
                )
                break

        result.stdout = result.stdout or (
            result.attempts[-1].stdout if result.attempts else ""
        )
        result.stderr = result.stderr or (
            result.attempts[-1].stderr if result.attempts else ""
        )
        result.total_duration_seconds = time.time() - start_time

        # ── Write per-run log ────────────────────────────────────────
        self._write_run_log(result)
        self._log_aggregate(result)

        return result

    # ── Single attempt ───────────────────────────────────────────────────

    async def _execute_single_attempt(
        self,
        attempt_num: int,
        session_id: str | None = None,
    ) -> RunAttempt:
        """Invoke OpenCode via HTTP and capture output."""
        await self._notify(RunPhase.INVOKE, f"attempt {attempt_num}")
        attempt = RunAttempt(attempt_number=attempt_num)
        prompt = self._read_prompt()
        model = self._model_override or self._config.model
        variant = self._variant_override or self._config.variant
        server_url = os.environ.get("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")
        timeout = self._config.timeout_minutes * 60

        log.info("runner.invoke subworker=%s attempt=%d session=%s", self._config.name, attempt_num, session_id or "new")

        start = time.time()
        try:
            async with OpenCodeClient(server_url, default_timeout=timeout) as client:
                if session_id:
                    log.info("runner.recover session=%s subworker=%s", session_id, self._config.name)
                    await client.send_message(
                        session_id, content=prompt, model=model, variant=variant,
                        agent=self._config.agent_id, timeout=timeout,
                    )
                else:
                    openworkspace = os.environ.get("OPENCODE_WORKSPACE", "")
                    workspace = self._config.workspace
                    if not workspace:
                        # Compute from agent_id, matching old trigger_template.js:
                        # main agent → project root; others → subworkers/<id>/workspace
                        main_name = self._read_main_agent_name()
                        if self._config.agent_id == main_name:
                            workspace = "/data"
                        else:
                            workspace = f"/data/subworkers/{self._config.agent_id}/workspace"
                    # Map /data/ paths to host via OPENCODE_WORKSPACE
                    if openworkspace and workspace.startswith("/data/"):
                        directory = workspace.replace("/data/", f"{openworkspace}/", 1)
                    elif openworkspace and workspace == "/data":
                        directory = openworkspace
                    else:
                        directory = openworkspace or workspace
                    log.info(
                        "runner.create_session subworker=%s directory=%s agent_id=%s",
                        self._config.name, directory, self._config.agent_id,
                    )
                    sess = await client.create_session(
                        directory=directory,
                        agent_id=self._config.agent_id,
                    )
                    log.info(
                        "runner.session_created subworker=%s session_id=%s response_agent=%s",
                        self._config.name, sess.get("id", ""), sess.get("agent", "unknown"),
                    )
                    session_id = sess.get("id") or ""
                    if not session_id:
                        raise OpenCodeSessionError("No session ID returned from create_session")
                    # NOTE: send_message blocks until the agent finishes —
                    # the progress streamer MUST start before it.
                    stream_task = asyncio.create_task(
                        self._stream_progress(session_id, directory)
                    )
                    try:
                        await client.send_message(
                        session_id, content=prompt, model=model, variant=variant,
                        agent=self._config.agent_id, timeout=timeout,
                    )
                    finally:
                        stream_task.cancel()

                attempt.session_id = session_id
                messages = await client.list_messages(session_id)
                attempt.stdout = OpenCodeClient.extract_assistant_text(messages)
                attempt.exit_code = 0
                attempt.duration_seconds = time.time() - start
                log.info("runner.success session=%s subworker=%s lines=%d",
                         session_id, self._config.name, len(attempt.stdout.splitlines()))

        except asyncio.TimeoutError:
            attempt.duration_seconds = time.time() - start
            attempt.exit_code = EXIT_TIMEOUT
            attempt.retriable = True
            attempt.error_type = ErrorType.TIMEOUT
            log.warning("runner.timeout subworker=%s attempt=%d timeout=%dm",
                        self._config.name, attempt_num, self._config.timeout_minutes)

        except OpenCodeTimeoutError as exc:
            attempt.duration_seconds = time.time() - start
            attempt.exit_code = EXIT_TIMEOUT
            attempt.retriable = True
            attempt.error_type = ErrorType.TIMEOUT
            attempt.stderr = str(exc)

        except RateLimitError as exc:
            attempt.duration_seconds = time.time() - start
            attempt.exit_code = 1
            attempt.retriable = True
            attempt.error_type = ErrorType.RATE_LIMIT
            attempt.stderr = str(exc)

        except OpenCodeConnectionError as exc:
            attempt.duration_seconds = time.time() - start
            attempt.exit_code = 1
            attempt.retriable = True
            attempt.error_type = ErrorType.SERVER_ERROR
            attempt.stderr = str(exc)

        except OpenCodeError as exc:
            attempt.duration_seconds = time.time() - start
            attempt.exit_code = 1
            attempt.error_type = ErrorParser.parse_http_status(exc.status_code or 500, exc.detail or "").error_type
            attempt.retriable = exc.status_code is not None and 500 <= exc.status_code < 600
            attempt.stderr = str(exc)

        except Exception as exc:
            attempt.duration_seconds = time.time() - start
            attempt.exit_code = 1
            attempt.stderr = str(exc)
            attempt.retriable = False
            log.exception("runner.invoke_error subworker=%s", self._config.name)

        return attempt

    # ── Validation ───────────────────────────────────────────────────────

    @staticmethod
    def _read_main_agent_name() -> str:
        import json as _json
        candidates = [
            Path("/data/subworkers/main-agent.json"),
            Path.home() / "EliaAI" / "subworkers" / "main-agent.json",
        ]
        for p in candidates:
            if p.exists():
                try:
                    data = _json.loads(p.read_text())
                    if data and isinstance(data.get("name"), str) and data["name"]:
                        return data["name"]
                except Exception:
                    pass
        return "elia"

    def _read_prompt(self) -> str:
        """Read the prompt from the subworker's PROMPT.md file.

        PROMPT.md IS the task instructions (workspace constraints, handoff
        protocol, business logic) — it MUST be sent as the user message on
        every run. The agent personality file (~/.config/opencode/agents/
        <id>.md) only carries identity/workflow and does NOT replace it.

        Resolution order:
          1. ``prompt_override`` (manual trigger body)
          2. ``<workspace>/<prompt_file>``              (as configured / legacy)
          3. ``<workspace>/../<prompt_file>``           (standard: next to workspace/)
          4. ``/data/subworkers/<name>/<prompt_file>``  (container layout)
        """
        if self._prompt_override:
            return self._prompt_override

        workspace = Path(self._config.workspace or ".")
        candidates = [
            workspace / self._config.prompt_file,
            workspace.parent / self._config.prompt_file,
            Path("/data/subworkers") / self._config.name / self._config.prompt_file,
        ]
        checked: list[str] = []
        for candidate in candidates:
            key = str(candidate)
            if key in checked:
                continue
            checked.append(key)
            try:
                if candidate.exists():
                    text = candidate.read_text(encoding="utf-8").strip()
                    if text:
                        log.info("runner.prompt_loaded subworker=%s path=%s chars=%d",
                                 self._config.name, key, len(text))
                        return text
            except OSError as exc:
                log.warning("runner.prompt_read_error subworker=%s path=%s error=%s",
                            self._config.name, key, exc)

        log.warning("runner.prompt_missing subworker=%s checked=%s", self._config.name, checked)
        return (
            f"Execute the {self._config.name} subworker task.\n"
            "Your PROMPT.md could not be located by the runner. Read your "
            "agent definition plus any handoff/state files in your workspace, "
            "complete the scheduled work, and report status when done.\n"
            "Output <promise>DONE</promise> when complete."
        )

    async def _stream_progress(self, session_id: str, directory: str) -> None:
        """Stream live agent output over WS while the run executes.

        Subscribes to the opencode SSE event stream scoped to the run's
        workspace and forwards text deltas as ``run_log`` WS events, so
        clients get realtime logs without polling HTTP.
        """
        import json as _json
        import os as _os
        from urllib.parse import quote

        import httpx

        from app.routes.websocket import ws_manager

        name = self._config.name
        server_url = _os.environ.get("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")
        url = f"{server_url}/event?directory={quote(directory)}"

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", url) as resp:
                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        try:
                            evt = _json.loads(line[5:].strip())
                        except Exception:
                            continue
                        if evt.get("type") != "message.part.delta":
                            continue
                        props = evt.get("properties") or {}
                        if props.get("sessionID") != session_id:
                            continue
                        if props.get("field") not in (None, "text"):
                            continue
                        delta = props.get("delta") or ""
                        if delta:
                            await ws_manager.broadcast_run_log(name, delta)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("runner.stream_error subworker=%s error=%s", name, exc)

    def _validate_run(self, attempt: RunAttempt) -> dict[str, Any]:
        """Validate a completed run (exit code 0).

        Success = exit_code == 0 AND (completion_marker OR min_lines).
        The marker is often absent from HTTP responses, so min_lines is a
        fallback.
        """
        checks: dict[str, bool] = {}
        checks["exit_code"] = attempt.exit_code == 0
        checks["completion_marker"] = COMPLETION_MARKER in attempt.stdout
        line_count = len(attempt.stdout.strip().splitlines()) if attempt.stdout.strip() else 0
        checks["min_lines"] = line_count >= MIN_OUTPUT_LINES

        valid = checks["exit_code"] and (checks["completion_marker"] or checks["min_lines"])
        if not valid:
            failed = [k for k, v in checks.items() if not v]
            log.warning("runner.validation_failed subworker=%s failed_checks=%s", self._config.name, failed)
        return {"valid": valid, "checks": checks}

    # ── Session recovery ─────────────────────────────────────────────────

    def _extract_session_id(self, stdout: str) -> str | None:
        """Extract the latest session ID from CLI stdout."""
        matches = SESSION_ID_PATTERN.findall(stdout)
        return matches[-1] if matches else None

    # ── Logging ──────────────────────────────────────────────────────────

    def _write_run_log(self, result: RunResult) -> None:
        """Write a per-run log file."""
        if not self._log_dir:
            return
        self._log_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self._config.name}_{ts}.log"
        path = self._log_dir / filename
        lines = [
            f"Subworker: {self._config.name}",
            f"Success: {result.success}",
            f"Attempts: {result.total_attempts}",
            f"Duration: {result.total_duration_seconds:.1f}s",
            f"Session: {result.session_id or 'N/A'}",
            "---",
        ]
        for att in result.attempts:
            lines.append(
                f"[Attempt {att.attempt_number}] exit={att.exit_code} "
                f"duration={att.duration_seconds:.1f}s error={att.error_type}"
            )
        lines.append("--- STDOUT ---")
        lines.append(result.stdout or "(empty)")
        lines.append("--- STDERR ---")
        lines.append(result.stderr or "(empty)")
        path.write_text("\n".join(lines), encoding="utf-8")

    def _log_aggregate(self, result: RunResult) -> None:
        """Log aggregate result via structured logger."""
        log_fn = log.info if result.success else log.warning
        log_fn(
            "runner.run_complete subworker=%s success=%s attempts=%d duration=%s session_id=%s error=%s",
            self._config.name, result.success, result.total_attempts,
            f"{result.total_duration_seconds:.1f}s", result.session_id, result.error_message,
        )

    # ── Callbacks ────────────────────────────────────────────────────────

    async def _notify(self, phase: RunPhase, message: str) -> None:
        for cb in self._callbacks:
            try:
                await cb(phase, message)
            except Exception:
                log.exception("runner.callback_error phase=%s", phase.value)
