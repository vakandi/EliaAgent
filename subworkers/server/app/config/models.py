"""Pydantic models for subworker server configuration."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Schedule ────────────────────────────────────────────────────────────────

class ScheduleType(str, Enum):
    INTERVAL = "interval"
    EVERY = "every"
    CRON = "cron"


class IntervalSchedule(BaseModel):
    """Run at specific hours: e.g. hours=[9,10,...,23], minute=0 → every hour from 9-23.

    days: optional weekday filter (0=Sunday..6=Saturday, cron convention).
    None or empty = run every day. [1,2,3,4,5] = weekdays only.
    """
    type: ScheduleType = ScheduleType.INTERVAL
    hours: list[int] = Field(..., min_length=1, description="Hours to run (0-23)")
    minute: int = Field(0, ge=0, le=59)
    days: list[int] | None = Field(None, description="Weekdays 0=Sun..6=Sat; None/empty = every day")


class EverySchedule(BaseModel):
    """Run every N minutes (5,10,15,20,30,45…), optionally restricted to hours/days.

    Generates a CronTrigger under the hood (minute = */N or explicit minute list)
    so the job stays clock-aligned (00, 10, 20 …), matching user expectation for
    “every 10 min”. For intervals that do not divide 60 evenly (e.g. 45) we use
    the cron minute list [0,45] — two runs per hour, still predictable.

    hours: if provided, only fire in those hours; None/empty = every hour.
    days: weekday filter 0=Sun..6=Sat; None/empty = every day.
    """
    type: ScheduleType = ScheduleType.EVERY
    every: int = Field(..., ge=1, le=1440, description="Interval in minutes (e.g. 10, 20, 30, 45)")
    hours: list[int] | None = Field(None, description="Restrict to these hours 0-23; None = every hour")
    days: list[int] | None = Field(None, description="Weekdays 0=Sun..6=Sat; None/empty = every day")


class CronSchedule(BaseModel):
    """Run on a cron expression: e.g. '0 9-23 * * *'."""
    type: ScheduleType = ScheduleType.CRON
    expression: str = Field(..., description="Standard 5-field cron expression")


Schedule = IntervalSchedule | EverySchedule | CronSchedule


# ── Server Config ───────────────────────────────────────────────────────────

class AlertConfig(BaseModel):
    enabled: bool = True
    electron_url: str = "http://localhost:3000"
    ntfy_topic: str = "AITeamHelper"
    debounce_seconds: int = 300  # 5 min


class OpenCodeConfig(BaseModel):
    server_url: str = "http://127.0.0.1:5655"
    health_check_interval: int = 10  # seconds
    max_restarts: int = 10
    backoff_max: int = 30  # seconds
    startup_timeout: int = 60  # seconds


class ServerConfig(BaseModel):
    """Top-level config for the subworker server itself."""
    port: int = 5656
    log_level: str = "INFO"
    opencode: OpenCodeConfig = Field(default_factory=OpenCodeConfig)
    alert: AlertConfig = Field(default_factory=AlertConfig)


# ── Subworker Config ───────────────────────────────────────────────────────

class SubworkerConfig(BaseModel):
    """Configuration for a single subworker."""
    name: str = Field(..., description="Unique subworker name (matches directory name)")
    enabled: bool = True
    schedule: Schedule
    prompt_file: str = Field(
        default="PROMPT.md",
        description="Filename inside the subworker directory (relative to workspace)",
    )
    workspace: Optional[str] = Field(
        default=None,
        description="Working directory path; defaults to subworkers/<name>/workspace",
    )
    agent_id: str = Field(
        ...,
        description="OpenCode agent ID (matches ~/.config/opencode/agents/<id>.md)",
    )
    model: Optional[str] = Field(default=None, description="Override model for this subworker")
    variant: Optional[str] = Field(default=None, description="Reasoning effort variant (low/medium/high/max) when the model supports it")
    max_retries: int = Field(3, ge=0, le=10)
    timeout_minutes: int = Field(30, ge=1, le=120)
    proxy_enabled: bool = False
    mcp_servers: list[str] = Field(
        default_factory=lambda: [
            "codegraph",
            "context7",
            "grep_app",
            "lsp",
            "parallel-browser-mcp",
            "websearch",
        ],
    )
    notify_discord: bool = False


# ── Combined Config ─────────────────────────────────────────────────────────

class SubworkersFile(BaseModel):
    """Contents of subworkers.json — the full subworker registry."""
    subworkers: list[SubworkerConfig] = Field(default_factory=list)
    version: str = "1.0"
    last_modified: Optional[datetime] = None
