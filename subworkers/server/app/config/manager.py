"""Configuration manager — loads, validates, and hot-reloads JSON configs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import structlog
from pydantic import ValidationError

from app.config.models import ServerConfig, SubworkerConfig, SubworkersFile

logger = structlog.get_logger(__name__)

_DEFAULT_SERVER = ServerConfig()
_DEFAULT_SUBWORKERS = SubworkersFile()


class ConfigManager:
    """Loads and manages server.json + subworkers.json with hot-reload support."""

    def __init__(
        self,
        config_dir: str | Path,
        subworkers_base_dir: str | Path | None = None,
    ) -> None:
        self.config_dir = Path(config_dir)
        self.subworkers_base_dir = Path(subworkers_base_dir) if subworkers_base_dir else None
        self._server: ServerConfig = _DEFAULT_SERVER
        self._subworkers: SubworkersFile = _DEFAULT_SUBWORKERS
        self._subworker_map: dict[str, SubworkerConfig] = {}

    # ── Public API ──────────────────────────────────────────────────────

    def load(self) -> None:
        """Load all config files. Raises on invalid JSON/schema."""
        self._server = self._load_server()
        self._subworkers = self._load_subworkers()
        self._build_map()
        logger.info(
            "config.loaded",
            server_port=self._server.port,
            subworker_count=len(self._subworkers.subworkers),
        )

    def reload(self) -> dict[str, object]:
        """Hot-reload configs. Returns summary of what changed."""
        old_names = set(self._subworker_map.keys())
        self.load()
        new_names = set(self._subworker_map.keys())
        added = new_names - old_names
        removed = old_names - new_names
        unchanged = old_names & new_names
        if added:
            logger.info("config.subworkers_added", names=sorted(added))
        if removed:
            logger.info("config.subworkers_removed", names=sorted(removed))
        return {
            "added": sorted(added),
            "removed": sorted(removed),
            "unchanged": sorted(unchanged),
            "total": len(self._subworker_map),
        }

    @property
    def server(self) -> ServerConfig:
        return self._server

    @property
    def subworkers(self) -> list[SubworkerConfig]:
        return list(self._subworker_map.values())

    def get_subworker(self, name: str) -> SubworkerConfig | None:
        return self._subworker_map.get(name)

    def get_enabled(self) -> list[SubworkerConfig]:
        return [sw for sw in self._subworker_map.values() if sw.enabled]

    def get_disabled(self) -> list[SubworkerConfig]:
        return [sw for sw in self._subworker_map.values() if not sw.enabled]

    def update_subworker(self, name: str, updates: dict[str, object]) -> SubworkerConfig:
        """Update a single subworker's config in memory and persist to disk."""
        existing = self._subworker_map.get(name)
        if not existing:
            raise KeyError(f"Subworker '{name}' not found")
        updated_data = existing.model_dump()
        updated_data.update(updates)
        new_config = SubworkerConfig(**updated_data)
        self._subworker_map[name] = new_config
        self._persist_subworkers()
        return new_config

    def _persist_subworkers(self) -> None:
        """Write current subworker state back to subworkers.json on disk."""
        path = self.config_dir / "subworkers.json"
        try:
            file_data = SubworkersFile(subworkers=list(self._subworker_map.values()))
            with open(path, "w") as f:
                json.dump(file_data.model_dump(), f, indent=2)
            logger.info("config.subworkers_persisted", path=str(path))
        except Exception as e:
            logger.error("config.persist_failed", path=str(path), error=str(e))

    # ── Private ─────────────────────────────────────────────────────────

    def _load_server(self) -> ServerConfig:
        path = self.config_dir / "server.json"
        if not path.exists():
            logger.warning("config.server_missing", path=str(path))
            return _DEFAULT_SERVER
        return self._parse_model(path, ServerConfig)

    def _load_subworkers(self) -> SubworkersFile:
        path = self.config_dir / "subworkers.json"
        if not path.exists():
            logger.warning("config.subworkers_missing", path=str(path))
            return _DEFAULT_SUBWORKERS
        raw = self._read_json(path)
        return SubworkersFile(**raw)

    def _build_map(self) -> None:
        self._subworker_map = {sw.name: sw for sw in self._subworkers.subworkers}
        # Apply per-subworker schedule overrides if present
        if self.subworkers_base_dir:
            for name, sw in self._subworker_map.items():
                override = self._load_schedule_override(name)
                if override:
                    self._subworker_map[name] = sw.model_copy(
                        update={"schedule": override}
                    )

    def _load_schedule_override(self, name: str) -> object | None:
        path = self.config_dir / "schedules" / f"{name}.json"
        if not path.exists():
            return None
        try:
            raw = self._read_json(path)
            return raw.get("schedule")
        except Exception as e:
            logger.warning("config.schedule_override_error", name=name, error=str(e))
            return None

    @staticmethod
    def _read_json(path: Path) -> dict:
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def _parse_model(path: Path, model_cls: type) -> object:
        raw = ConfigManager._read_json(path)
        try:
            return model_cls(**raw)
        except ValidationError as e:
            logger.error("config.validation_error", path=str(path), errors=e.errors())
            raise
