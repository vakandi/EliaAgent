"""Alert manager for macOS subworker notifications.

Handles system beep, Electron desktop alerts, and ntfy.sh fallback
with per-type debouncing to prevent notification flooding.
"""

import asyncio
import structlog
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

logger = structlog.get_logger(__name__)

ELECTRON_ALERT_URL = "http://localhost:3000/api/subworker-alert"
NTFY_ALERT_URL = "https://ntfy.sh/AITeamHelper"
DEBOUNCE_WINDOW_SECONDS = 300  # 5 minutes
DEFAULT_TIMEOUT_SECONDS = 5.0


class AlertType(str, Enum):
    SUBWORKER_COMPLETED = "subworker_completed"
    SUBWORKER_FAILED = "subworker_failed"
    HEALTH_DEGRADED = "health_degraded"
    HEALTH_DOWN = "health_down"
    RATE_LIMITED = "rate_limited"
    SESSION_STUCK = "session_stuck"
    GENERIC = "generic"


@dataclass
class AlertPayload:
    title: str
    message: str
    alert_type: AlertType = AlertType.GENERIC
    urgent: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "message": self.message,
            "type": self.alert_type.value,
            "urgent": self.urgent,
        }


@dataclass
class AlertResult:
    sent: bool
    destination: str
    timestamp: float = field(default_factory=time.time)
    error: str | None = None


class AlertManager:
    """Sends alerts via macOS beep → Electron → ntfy.sh fallback chain."""

    def __init__(
        self,
        electron_url: str = ELECTRON_ALERT_URL,
        ntfy_url: str = NTFY_ALERT_URL,
        debounce_window: float = DEBOUNCE_WINDOW_SECONDS,
        http_timeout: float = DEFAULT_TIMEOUT_SECONDS,
        enable_beep: bool = True,
    ) -> None:
        self._electron_url = electron_url
        self._ntfy_url = ntfy_url
        self._debounce_window = debounce_window
        self._http_timeout = http_timeout
        self._enable_beep = enable_beep
        self._last_sent: dict[str, float] = {}
        self._history: list[AlertResult] = []

    @property
    def history(self) -> list[AlertResult]:
        return list(self._history)

    def _is_debounced(self, alert_type: AlertType) -> bool:
        last = self._last_sent.get(alert_type.value, 0.0)
        return (time.time() - last) < self._debounce_window

    def _record_sent(self, alert_type: AlertType, destination: str) -> AlertResult:
        self._last_sent[alert_type.value] = time.time()
        result = AlertResult(sent=True, destination=destination)
        self._history.append(result)
        logger.info(
            "alert_sent",
            extra={
                "alert_type": alert_type.value,
                "destination": destination,
            },
        )
        return result

    def _record_failure(
        self, alert_type: AlertType, destination: str, error: str
    ) -> AlertResult:
        result = AlertResult(sent=False, destination=destination, error=error)
        self._history.append(result)
        logger.warning(
            "alert_failed",
            extra={
                "alert_type": alert_type.value,
                "destination": destination,
                "error": error,
            },
        )
        return result

    def play_beep(self) -> bool:
        if not self._enable_beep:
            return False
        try:
            import subprocess

            result = subprocess.run(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                timeout=5,
                capture_output=True,
            )
            return result.returncode == 0
        except Exception as exc:
            logger.warning("beep_failed", extra={"error": str(exc)})
            return False

    async def post_electron_alert(self, payload: AlertPayload) -> AlertResult:
        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                resp = await client.post(self._electron_url, json=payload.to_dict())
                if resp.status_code < 400:
                    return self._record_sent(payload.alert_type, "electron")
                return self._record_failure(
                    payload.alert_type,
                    "electron",
                    f"HTTP {resp.status_code}",
                )
        except httpx.TimeoutException as exc:
            return self._record_failure(payload.alert_type, "electron", f"timeout: {exc}")
        except Exception as exc:
            return self._record_failure(payload.alert_type, "electron", str(exc))

    async def post_ntfy_alert(self, payload: AlertPayload) -> AlertResult:
        title = f"[{payload.alert_type.value}] {payload.title}"
        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                resp = await client.post(
                    self._ntfy_url,
                    content=payload.message,
                    headers={
                        "Title": title,
                        "Priority": "urgent" if payload.urgent else "default",
                    },
                )
                if resp.status_code < 400:
                    return self._record_sent(payload.alert_type, "ntfy")
                return self._record_failure(
                    payload.alert_type,
                    "ntfy",
                    f"HTTP {resp.status_code}",
                )
        except httpx.TimeoutException as exc:
            return self._record_failure(payload.alert_type, "ntfy", f"timeout: {exc}")
        except Exception as exc:
            return self._record_failure(payload.alert_type, "ntfy", str(exc))

    async def trigger_alert(self, payload: AlertPayload) -> list[AlertResult]:
        if self._is_debounced(payload.alert_type):
            logger.info(
                "alert_debounced",
                extra={"alert_type": payload.alert_type.value},
            )
            return []

        results: list[AlertResult] = []

        self.play_beep()

        electron_result = await self.post_electron_alert(payload)
        results.append(electron_result)

        if electron_result.sent:
            self._last_sent[payload.alert_type.value] = time.time()
            return results

        ntfy_result = await self.post_ntfy_alert(payload)
        results.append(ntfy_result)

        if ntfy_result.sent:
            self._last_sent[payload.alert_type.value] = time.time()

        return results
