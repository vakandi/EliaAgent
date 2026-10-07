"""Discord webhook notifier — gap 6 carry-over (run completed/failed).

Same contract as today: fire-and-forget POST to DISCORD_WEBHOOK_URL, never
raise into the caller, never log the URL or secret values.
"""
from __future__ import annotations

import structlog
import httpx

from app.config import get_settings

logger = structlog.get_logger(__name__)

_TIMEOUT_S = 5.0


async def notify(title: str, message: str, *, urgent: bool = False) -> bool:
    """Send one Discord webhook message. Returns True when delivered."""
    url = get_settings().DISCORD_WEBHOOK_URL
    if not url:
        logger.debug("discord.skipped_no_webhook")
        return False
    prefix = "🚨" if urgent else "✅"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
            response = await client.post(
                url, json={"content": f"{prefix} **{title}**\n{message}"}
            )
            response.raise_for_status()
        logger.info("discord.sent", title=title)
        return True
    except Exception as exc:
        logger.warning("discord.failed", title=title, error=type(exc).__name__)
        return False


async def notify_run_completed(name: str, session_id: str, model: str) -> bool:
    return await notify(
        f"subworker completed: {name}",
        f"session `{session_id}` finished (model `{model}`).",
    )


async def notify_run_failed(name: str, error: str) -> bool:
    return await notify(
        f"subworker failed: {name}",
        f"error: {error}",
        urgent=True,
    )
