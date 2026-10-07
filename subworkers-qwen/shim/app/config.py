"""Shim settings — env-driven, placeholders only, never log secrets."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


def _csv(name: str) -> list[str] | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return [part.strip() for part in raw.split(",") if part.strip()]


class Settings:
    PORT: int = int(os.getenv("PORT", "5676"))
    QWEN_URL: str = os.getenv("QWEN_URL", "http://qwen:4170").rstrip("/")
    QWEN_SERVER_TOKEN: str = os.getenv("QWEN_SERVER_TOKEN", "")
    ELIA_AUTH_TOKEN: str = os.getenv("ELIA_AUTH_TOKEN", "").strip()
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    CONFIG_DIR: Path = Path(os.getenv("CONFIG_DIR", str(Path(__file__).parent / "config")))
    SUBWORKERS_DIR: Path = Path(os.getenv("SUBWORKERS_DIR", str(Path(__file__).parent.parent.parent / "workspaces")))
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(Path(__file__).parent.parent.parent / "logs")))
    MAX_CONCURRENT_RUNS: int = int(os.getenv("MAX_CONCURRENT_RUNS", "8"))
    STALL_TIMEOUT_S: int = int(os.getenv("STALL_TIMEOUT_S", "300"))
    MAX_RUN_S: int = int(os.getenv("MAX_RUN_S", "3600"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    MODEL_OVERRIDE: list[str] | None = _csv("ZEN_FREE_MODELS")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
