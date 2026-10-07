"""Main-agent endpoint — gap 7 carry-over (GET/POST /main-agent).

Same file contract as the live server: main-agent.json holds {"name": ...}.
Path resolution: container bind-mount first, repo workspaces fallback, so
local dev works without Docker.
"""
from __future__ import annotations

import json
from pathlib import Path

import structlog
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import get_settings
from app.routers.websocket import ws_manager

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["main-agent"])


def _main_agent_file() -> Path:
    data_path = Path("/data/subworkers-qwen/main-agent.json")
    if data_path.parent.exists():
        return data_path
    return get_settings().SUBWORKERS_DIR.parent / "main-agent.json"


class MainAgentResponse(BaseModel):
    name: str


class MainAgentSetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")


@router.get("/main-agent", response_model=MainAgentResponse)
async def get_main_agent() -> MainAgentResponse:
    try:
        return MainAgentResponse(name=json.loads(_main_agent_file().read_text())["name"])
    except (OSError, KeyError, json.JSONDecodeError):
        return MainAgentResponse(name="elia")


@router.post("/main-agent", response_model=MainAgentResponse)
async def set_main_agent(body: MainAgentSetRequest) -> MainAgentResponse:
    path = _main_agent_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"name": body.name}, indent=2) + "\n")
    await ws_manager.broadcast({"type": "main_agent", "name": body.name})
    logger.info("main_agent.set", name=body.name)
    return MainAgentResponse(name=body.name)
