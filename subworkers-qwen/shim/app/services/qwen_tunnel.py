"""Cloudflare Tunnel manager — compact mirror of live tunnel_manager.py.

Same logic, trimmed: Cloudflare API v4 calls (verify/check/create/DNS),
token file + file-watcher sidecar pattern (no Docker socket anywhere),
JSON state file, step machine. Differences from live, all deliberate:
- No docker/compose subprocess (live only uses it for network discovery;
  here the ingress service host is fixed: shim:5676).
- cloudflared liveness via watcher heartbeat file (no container inspect).
- Secrets (API token, runner token) live in files under CONFIG_DIR, which
  is gitignored via .env* + tunnel.token entries. Never logged.
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx
import structlog

log = structlog.get_logger(__name__)

CF_API_BASE = "https://api.cloudflare.com/client/v4"
CF_TIMEOUT = 30.0
TOKEN_FILE_NAME = "tunnel.token"
STATE_FILE_NAME = "tunnel.state.json"
HEARTBEAT_FILE_NAME = "cloudflared.alive"
HEARTBEAT_MAX_AGE_S = 20.0

STEP_IDLE = "idle"
STEP_VERIFYING = "verifying"
STEP_STARTING = "starting_cloudflared"
STEP_VERIFYING_PUBLIC = "verifying_public"
STEP_DONE = "done"
STEP_ERROR = "error"


class TunnelError(Exception):
    """Cloudflare API or orchestration failure (message is user-safe)."""


def mask_token(token: str | None) -> str | None:
    if not token:
        return None
    t = token.strip()
    if len(t) <= 8:
        return "…"
    return f"{t[:4]}…{t[-4:]}"


def normalize_domain(domain: str) -> str:
    return domain.strip().lower().rstrip(".")


class QwenTunnelManager:
    """Owns tunnel lifecycle for the qwen stack sidecar."""

    def __init__(
        self,
        config_dir: Path | None = None,
        compose_service_name: str = "shim",
        server_port: int = 5676,
    ) -> None:
        self.config_dir = Path(config_dir) if config_dir else Path("/data/config")
        self.compose_service_name = compose_service_name
        self.server_port = server_port
        self._setup_task: asyncio.Task[None] | None = None
        self._step = STEP_IDLE
        self._last_error: str | None = None

    @property
    def token_path(self) -> Path:
        return self.config_dir / TOKEN_FILE_NAME

    @property
    def state_path(self) -> Path:
        return self.config_dir / STATE_FILE_NAME

    @property
    def heartbeat_path(self) -> Path:
        return self.config_dir / HEARTBEAT_FILE_NAME

    @property
    def step(self) -> str:
        return self._step

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @property
    def is_setup_running(self) -> bool:
        return self._setup_task is not None and not self._setup_task.done()

    def _set_step(self, step: str, error: str | None = None) -> None:
        self._step = step
        self._last_error = error

    # ── Cloudflare API ────────────────────────────────────────────────

    async def _cf_request(
        self,
        method: str,
        path: str,
        *,
        api_token: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{CF_API_BASE}{path}"
        headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=CF_TIMEOUT) as client:
                resp = await client.request(method, url, headers=headers, json=json_body, params=params)
        except httpx.HTTPError as exc:
            raise TunnelError(f"Cloudflare API unreachable: {exc}") from exc
        try:
            payload = resp.json()
        except ValueError:
            payload = {}
        if resp.status_code >= 400 or not payload.get("success", False):
            errors = payload.get("errors") or [{"code": resp.status_code, "message": resp.text[:200]}]
            msg = "; ".join(f"[{e.get('code')}] {e.get('message')}" for e in errors)
            raise TunnelError(f"Cloudflare API error: {msg}")
        return payload.get("result")

    async def verify_token(self, api_token: str) -> dict[str, Any]:
        await self._cf_request("GET", "/user/tokens/verify", api_token=api_token)
        try:
            accounts = await self._cf_request("GET", "/accounts", api_token=api_token, params={"per_page": 1})
        except TunnelError:
            log.info("tunnel.account_not_listed")
            return {"account_id": None, "account_name": ""}
        if not accounts:
            return {"account_id": None, "account_name": ""}
        account = accounts[0]
        return {"account_id": account["id"], "account_name": account.get("name", "")}

    async def check_zone(self, api_token: str, domain: str) -> dict[str, Any]:
        labels = domain.split(".")
        zones: list[dict[str, Any]] = []
        for i in range(len(labels) - 1):
            candidate = ".".join(labels[i:])
            zones = await self._cf_request("GET", "/zones", api_token=api_token, params={"name": candidate})
            if zones:
                break
        if not zones:
            raise TunnelError(f"Zone '{domain}' not found — it must be managed by this token's account")
        zone = zones[0]
        zone_account = zone.get("account") or {}
        return {
            "zone_id": zone["id"],
            "zone_name": zone.get("name", domain),
            "zone_status": zone.get("status"),
            "account_id": zone_account.get("id"),
            "account_name": zone_account.get("name", ""),
        }

    async def create_tunnel(self, api_token: str, account_id: str, domain: str) -> dict[str, Any]:
        tunnel_name = f"elia-qwen-{domain.replace('.', '-')}"
        try:
            result = await self._cf_request(
                "POST", f"/accounts/{account_id}/cfd_tunnel", api_token=api_token,
                json_body={"name": tunnel_name, "config_src": "cloudflare"},
            )
        except TunnelError as exc:
            if "1013" not in str(exc):
                raise
            log.warning("tunnel.name_exists_reusing", name=tunnel_name)
            existing = await self._cf_request(
                "GET", f"/accounts/{account_id}/cfd_tunnel", api_token=api_token,
                params={"name": tunnel_name, "is_deleted": "false"},
            )
            if isinstance(existing, list) and existing:
                result = existing[0]
            elif isinstance(existing, dict) and existing.get("id"):
                result = existing
            else:
                tunnel_name = f"{tunnel_name}-{int(time.time()) % 10000}"
                result = await self._cf_request(
                    "POST", f"/accounts/{account_id}/cfd_tunnel", api_token=api_token,
                    json_body={"name": tunnel_name, "config_src": "cloudflare"},
                )
        tunnel_id = result["id"]
        token_result = await self._cf_request(
            "GET", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/token", api_token=api_token
        )
        tunnel_token = token_result if isinstance(token_result, str) else str(token_result)
        await self._cf_request(
            "PUT", f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations",
            api_token=api_token,
            json_body={"config": {"ingress": [
                {"hostname": domain, "service": f"http://{self.compose_service_name}:{self.server_port}"},
                {"service": "http_status:404"},
            ]}},
        )
        log.info("tunnel.created", tunnel_id=tunnel_id, domain=domain)
        return {"tunnel_id": tunnel_id, "tunnel_token": tunnel_token}

    async def ensure_dns(self, api_token: str, zone_id: str, domain: str, tunnel_id: str) -> None:
        records = await self._cf_request(
            "GET", f"/zones/{zone_id}/dns_records", api_token=api_token,
            params={"name": domain, "type": "CNAME"},
        )
        if records:
            return
        await self._cf_request(
            "POST", f"/zones/{zone_id}/dns_records", api_token=api_token,
            json_body={"type": "CNAME", "name": domain, "content": f"{tunnel_id}.cfargotunnel.com",
                       "proxied": True, "comment": "elia-qwen sidecar"},
        )

    # ── Local state ───────────────────────────────────────────────────

    def save_state(self, **fields: Any) -> None:
        try:
            current: dict[str, Any] = {}
            if self.state_path.exists():
                current = json.loads(self.state_path.read_text())
            current.update(fields)
            self.state_path.write_text(json.dumps(current, indent=2))
        except Exception as exc:
            log.warning("tunnel.state_save_failed", error=str(exc))

    def load_state(self) -> dict[str, Any] | None:
        try:
            if self.state_path.exists():
                data = json.loads(self.state_path.read_text())
                return data if isinstance(data, dict) else None
        except Exception:
            pass
        return None

    def clear_state(self) -> None:
        for p in (self.state_path, self.token_path):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

    def is_cloudflared_running(self) -> bool:
        try:
            if not self.token_path.exists():
                return False
            hb = self.heartbeat_path
            if not hb.exists():
                return False
            return (time.time() - hb.stat().st_mtime) < HEARTBEAT_MAX_AGE_S
        except Exception:
            return False

    async def status(self) -> dict[str, Any]:
        state = self.load_state() or {}
        return {
            "configured": bool(state.get("tunnel_id")),
            "domain": state.get("domain"),
            "tunnel_id": state.get("tunnel_id"),
            "cloudflared_running": self.is_cloudflared_running(),
            "public_ok": bool(state.get("public_ok")),
            "last_error": self._last_error or state.get("last_error"),
            "step": self._step,
            "api_token_masked": None,
            "tunnel_token_masked": mask_token(state.get("tunnel_token")),
        }

    def start_setup(self, domain: str, api_token: str) -> asyncio.Task[None]:
        self._setup_task = asyncio.ensure_future(self._run_setup(domain, api_token))
        return self._setup_task

    async def _run_setup(self, domain: str, api_token: str) -> None:
        try:
            self._set_step(STEP_VERIFYING)
            account = await self.verify_token(api_token)
            zone = await self.check_zone(api_token, domain)
            account_id = account["account_id"] or zone.get("account_id")
            if not account_id:
                raise TunnelError("Could not resolve the Cloudflare account for this domain")
            self._set_step(STEP_STARTING)
            created = await self.create_tunnel(api_token, account_id, domain)
            await self.ensure_dns(api_token, zone["zone_id"], domain, created["tunnel_id"])
            self.token_path.write_text(created["tunnel_token"].strip() + "\n")
            try:
                self.token_path.chmod(0o600)
            except Exception:
                pass
            self.save_state(domain=domain, tunnel_id=created["tunnel_id"],
                            tunnel_token=created["tunnel_token"], public_ok=False,
                            last_error=None)
            self._set_step(STEP_VERIFYING_PUBLIC)
            for _ in range(12):
                await asyncio.sleep(10)
                if self.is_cloudflared_running():
                    break
            self.save_state(public_ok=self.is_cloudflared_running())
            self._set_step(STEP_DONE if self.is_cloudflared_running() else STEP_ERROR,
                           None if self.is_cloudflared_running() else "sidecar did not come up (start it: docker compose up -d cloudflared)")
        except TunnelError as exc:
            self._set_step(STEP_ERROR, str(exc))
            self.save_state(last_error=str(exc))
        except Exception as exc:
            log.error("tunnel.setup_failed", error=str(exc))
            self._set_step(STEP_ERROR, str(exc))
            self.save_state(last_error=str(exc))

    async def stop(self) -> None:
        try:
            self.token_path.unlink(missing_ok=True)
        except Exception:
            pass
        self._set_step(STEP_IDLE)

    async def remove(self) -> dict[str, Any]:
        state = self.load_state() or {}
        # Best effort: delete DNS + tunnel if we still have API context is
        # unavailable post-hoc (token not stored) — clear local state regardless.
        removed_dns = False
        removed_tunnel = False
        self.clear_state()
        self._set_step(STEP_IDLE)
        return {"removed_dns": removed_dns, "removed_tunnel": removed_tunnel,
                "domain": state.get("domain")}
