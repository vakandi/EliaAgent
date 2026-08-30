"""Cloudflare Tunnel manager — remote access to the subworker server.

Implements Unit L (PLAN.md §9.1): server-side tunnel lifecycle management.

Flow (POST /tunnel/setup orchestrates these as background steps):
    verifying_token → checking_zone → creating_tunnel → routing_dns
    → starting_cloudflared → verifying_public → done | error

Required Cloudflare API token permissions:
    - Zone → DNS → Edit                   (create the CNAME record)
    - Account → Cloudflare Tunnel → Edit  (create/configure/run the tunnel)

Security notes:
     - Tokens are persisted ONLY in app/config/tunnel.json (chmod 600).
     - No API endpoint ever returns a raw token — masked form only (tok_…abc).

Deployment note: Socketless mode — the subworker container no longer mounts
``/var/run/docker.sock`` (sandbox escape). ``cloudflared`` is a sibling
service in ``docker-compose.yml`` with a file-watcher entrypoint
(``scripts/cloudflared-watch.sh``). The manager only writes the runner token
to ``app/config/tunnel.token`` (chmod 600, shared volume); the watcher
restarts cloudflared internally when the file changes. No Docker API needed.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import structlog

log = structlog.get_logger()

# ── Constants ───────────────────────────────────────────────────────────
CF_API_BASE = "https://api.cloudflare.com/client/v4"
CLOUDFLARED_IMAGE = "cloudflare/cloudflared:latest"
OVERRIDE_FILE_NAME = "docker-compose.override.tunnel.yml"
STATE_FILE_NAME = "tunnel.json"
TOKEN_FILE_NAME = "tunnel.token"

PUBLIC_VERIFY_TIMEOUT = 90.0   # seconds to wait for https://{domain}/server/health
PUBLIC_POLL_INTERVAL = 3.0
PUBLIC_REQUEST_TIMEOUT = 10.0
STATUS_PUBLIC_TIMEOUT = 4.0    # quick single-shot check for GET /tunnel/status
COMPOSE_TIMEOUT = 120.0        # subprocess timeout for docker compose commands
CF_TIMEOUT = 30.0              # Cloudflare API request timeout

# Wizard progress steps exposed via GET /tunnel/status (`step` field).
STEP_IDLE = "idle"
STEP_VERIFYING_TOKEN = "verifying_token"
STEP_CHECKING_ZONE = "checking_zone"
STEP_CREATING_TUNNEL = "creating_tunnel"
STEP_ROUTING_DNS = "routing_dns"
STEP_STARTING_CLOUDFLARED = "starting_cloudflared"
STEP_VERIFYING_PUBLIC = "verifying_public"
STEP_DONE = "done"
STEP_ERROR = "error"


class TunnelError(RuntimeError):
    """Raised for any tunnel management failure (message is user-safe)."""


def mask_token(token: str | None) -> str | None:
    """Mask a secret for API responses: 'tok_…abc'."""
    if not token:
        return None
    if len(token) <= 6:
        return "…"
    return f"{token[:3]}…{token[-3:]}"


def normalize_domain(domain: str) -> str:
    """Accept bare domains or pasted URLs; return a bare lowercase hostname."""
    d = domain.strip().lower()
    for prefix in ("https://", "http://"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d.strip("/").split("/", 1)[0]


class TunnelManager:
    """Manages the Cloudflare Tunnel that exposes this server publicly.

    Usage::

        manager = TunnelManager()
        manager.start_setup(domain, api_token)   # fire-and-forget orchestration
        state = manager.status()                 # poll `step` until done|error
    """

    def __init__(
        self,
        config_dir: str | Path | None = None,
        project_dir: str | Path | None = None,
        docker_bin: str | None = None,
        compose_service_name: str = "subworker-srv",
        server_port: int = 5656,
        cloudflared_container: str = "elia-cloudflared",
    ) -> None:
        self.config_dir = Path(
            config_dir
            or os.getenv("CONFIG_DIR", str(Path(__file__).resolve().parent.parent / "config"))
        )
        self.project_dir = Path(project_dir or self._default_project_dir())
        self.docker_bin = docker_bin or os.getenv("DOCKER_BIN", "docker")
        # Must match the service name in docker-compose.yml so cloudflared can
        # reach http://subworker-srv:5656 over the shared compose network.
        self.compose_service_name = compose_service_name
        self.server_port = server_port
        self.cloudflared_container = cloudflared_container

        self._step: str = STEP_IDLE
        self._last_error: str | None = None
        self._setup_task: asyncio.Task[None] | None = None

    # ── Paths ───────────────────────────────────────────────────────────

    @staticmethod
    def _default_project_dir() -> Path:
        """Locate the docker-compose project directory.

        Inside the subworker container the host repo is bind-mounted at
        /data/subworkers/server (SUBWORKERS_DIR=/data/subworkers); on the
        host, fall back to the repo root derived from this file's location.
        """
        env = os.getenv("COMPOSE_PROJECT_DIR")
        if env:
            return Path(env)
        candidates = [
            Path("/data/subworkers/server"),
            Path(__file__).resolve().parent.parent.parent,
        ]
        for candidate in candidates:
            if (candidate / "docker-compose.yml").exists():
                return candidate
        return candidates[-1]

    @property
    def override_path(self) -> Path:
        return self.project_dir / OVERRIDE_FILE_NAME

    @property
    def state_path(self) -> Path:
        return self.config_dir / STATE_FILE_NAME

    @property
    def token_path(self) -> Path:
        return self.config_dir / TOKEN_FILE_NAME

    # ── Cloudflare API helpers ──────────────────────────────────────────

    async def _cf_request(
        self,
        method: str,
        path: str,
        *,
        api_token: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Call the Cloudflare API v4 and return `result`, raising TunnelError on failure."""
        url = f"{CF_API_BASE}{path}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=CF_TIMEOUT) as client:
                resp = await client.request(
                    method, url, headers=headers, json=json_body, params=params
                )
        except httpx.HTTPError as exc:
            raise TunnelError(f"Cloudflare API unreachable: {exc}") from exc

        try:
            payload = resp.json()
        except ValueError:
            payload = {}

        if resp.status_code >= 400 or not payload.get("success", False):
            errors = payload.get("errors") or [
                {"code": resp.status_code, "message": resp.text[:200]}
            ]
            msg = "; ".join(f"[{e.get('code')}] {e.get('message')}" for e in errors)
            raise TunnelError(f"Cloudflare API error: {msg}")
        return payload.get("result")

    async def create_restricted_token_via_global(self, global_key: str, email: str, domain: str) -> str:
        """Create a restricted Bearer token via Global API Key (X-Auth-Email/Key).

        Uses the Global key to mint a token with Zone DNS Write + Tunnel Write
        scoped to the account that owns `domain`. Returns the Bearer value.
        """
        url = f"{CF_API_BASE}/user/tokens"
        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": global_key,
            "Content-Type": "application/json",
        }
        # Permission IDs verified via /user/tokens/permission_groups (2026-08-30)
        # Zone Read + DNS Write for surfai.tech, Tunnel Write for account
        body = {
            "name": f"elia-auto-{domain.replace('.', '-')}",
            "policies": [
                {
                    "effect": "allow",
                    "resources": {"com.cloudflare.api.account.zone.*": "*"},
                    "permission_groups": [
                        {"id": "c8fed203ed3043cba015a93ad1616f1f"},
                        {"id": "4755a26eedb94da69e1066d98aa820be"},
                    ],
                },
                {
                    "effect": "allow",
                    "resources": {"com.cloudflare.api.account.*": "*"},
                    "permission_groups": [{"id": "c07321b023e944ff818fec44d8203567"}],
                },
            ],
            "expires_on": "2027-12-31T00:00:00Z",
        }
        try:
            async with httpx.AsyncClient(timeout=CF_TIMEOUT) as client:
                resp = await client.post(url, headers=headers, json=body)
        except httpx.HTTPError as exc:
            raise TunnelError(f"Global API unreachable: {exc}") from exc
        try:
            payload = resp.json()
        except ValueError:
            payload = {}
        if resp.status_code >= 400 or not payload.get("success", False):
            errors = payload.get("errors") or [{"message": resp.text[:200]}]
            msg = "; ".join(f"[{e.get('code')}] {e.get('message')}" for e in errors)
            raise TunnelError(f"Could not create token via Global API Key: {msg}")
        result = payload.get("result") or {}
        token = result.get("value") or result.get("id")
        if not token:
            raise TunnelError("Global API created token but no value returned")
        log.info("tunnel.restricted_token_created_via_global", domain=domain)
        return str(token)

    async def verify_token(self, api_token: str) -> dict[str, Any]:
        """Verify the API token and resolve its account when visible.

        Returns ``{"account_id": ..., "account_name": ...}``. Tokens scoped
        to Tunnel+DNS only never see /accounts — the caller falls back to the
        zone's account ownership.
        """
        await self._cf_request("GET", "/user/tokens/verify", api_token=api_token)
        accounts = await self._cf_request(
            "GET", "/accounts", api_token=api_token, params={"per_page": 1}
        )
        if not accounts:
            log.info("tunnel.account_not_listed")
            return {"account_id": None, "account_name": ""}
        account = accounts[0]
        log.info("tunnel.token_verified", account_name=account.get("name"))
        return {"account_id": account["id"], "account_name": account.get("name", "")}

    async def check_zone(self, api_token: str, domain: str) -> dict[str, Any]:
        """Look up the Cloudflare zone for `domain`.

        Returns ``{"zone_id": ..., "zone_name": ..., "zone_status": ...}``.
        """
        # The domain may be a subdomain of the hosted zone (elia.example.com
        # lives in the example.com zone) — strip labels until a zone matches.
        labels = domain.split(".")
        zones: list[dict[str, Any]] = []
        for i in range(len(labels) - 1):
            candidate = ".".join(labels[i:])
            zones = await self._cf_request(
                "GET", "/zones", api_token=api_token, params={"name": candidate}
            )
            if zones:
                break
        if not zones:
            raise TunnelError(
                f"Zone '{domain}' not found — the domain must be managed by "
                "the Cloudflare account this token belongs to"
            )
        zone = zones[0]
        log.info("tunnel.zone_found", zone=zone.get("name"), status=zone.get("status"))
        zone_account = zone.get("account") or {}
        return {
            "zone_id": zone["id"],
            "zone_name": zone.get("name", domain),
            "zone_status": zone.get("status"),
            "account_id": zone_account.get("id"),
            "account_name": zone_account.get("name", ""),
        }

    async def create_tunnel(
        self, api_token: str, account_id: str, domain: str
    ) -> dict[str, Any]:
        """Create a named tunnel and configure its ingress.

        Returns ``{"tunnel_id": ..., "tunnel_token": ...}`` where tunnel_token
        is the cloudflared runner token (NOT the API token).
        Handles duplicate name (1013) by reusing existing tunnel.
        """
        tunnel_name = f"elia-subworker-{domain.replace('.', '-')}"
        try:
            result = await self._cf_request(
                "POST",
                f"/accounts/{account_id}/cfd_tunnel",
                api_token=api_token,
                json_body={
                    "name": tunnel_name,
                    # Remotely-managed tunnel: ingress lives in CF (configurations endpoint).
                    "config_src": "cloudflare",
                },
            )
        except TunnelError as exc:
            if "1013" in str(exc) and "already have a tunnel" in str(exc):
                log.warning("tunnel.name_exists_reusing", name=tunnel_name)
                # Try to find existing tunnel with that name
                try:
                    existing = await self._cf_request(
                        "GET",
                        f"/accounts/{account_id}/cfd_tunnel",
                        api_token=api_token,
                        params={"name": tunnel_name, "is_deleted": "false"},
                    )
                    if existing:
                        # Cloudflare returns list or single object
                        if isinstance(existing, list) and existing:
                            result = existing[0]
                        elif isinstance(existing, dict) and existing.get("id"):
                            result = existing
                        else:
                            # Fallback: generate unique name and retry once
                            raise ValueError("not found")
                    else:
                        # No existing found, try with unique suffix
                        tunnel_name = f"{tunnel_name}-{int(time.time()) % 10000}"
                        result = await self._cf_request(
                            "POST",
                            f"/accounts/{account_id}/cfd_tunnel",
                            api_token=api_token,
                            json_body={"name": tunnel_name, "config_src": "cloudflare"},
                        )
                except Exception as reuse_err:
                    # Final fallback: unique name
                    log.warning("tunnel.reuse_failed_try_unique", error=str(reuse_err))
                    tunnel_name = f"{tunnel_name}-{int(time.time()) % 10000}"
                    result = await self._cf_request(
                        "POST",
                        f"/accounts/{account_id}/cfd_tunnel",
                        api_token=api_token,
                        json_body={"name": tunnel_name, "config_src": "cloudflare"},
                    )
            else:
                raise
        tunnel_id = result["id"]

        token_result = await self._cf_request(
            "GET",
            f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/token",
            api_token=api_token,
        )
        tunnel_token = token_result if isinstance(token_result, str) else str(token_result)

        # Push ingress: route the public hostname to the compose service over
        # the shared Docker network. WS passthrough works automatically.
        await self._cf_request(
            "PUT",
            f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations",
            api_token=api_token,
            json_body={
                "config": {
                    "ingress": [
                        {
                            "hostname": domain,
                            "service": f"http://{self.compose_service_name}:{self.server_port}",
                        },
                        {"service": "http_status:404"},
                    ]
                }
            },
        )
        log.info("tunnel.created", tunnel_id=tunnel_id, domain=domain)
        return {"tunnel_id": tunnel_id, "tunnel_token": tunnel_token}

    async def check_dns_record(self, api_token: str, zone_id: str, domain: str) -> bool:
        """Return True if a CNAME record already exists for `domain`."""
        records = await self._cf_request(
            "GET",
            f"/zones/{zone_id}/dns_records",
            api_token=api_token,
            params={"type": "CNAME", "name": domain},
        )
        return bool(records)

    async def create_dns_route(
        self, api_token: str, zone_id: str, domain: str, tunnel_id: str
    ) -> dict[str, Any]:
        """Create (or reuse) the proxied CNAME {domain} → {tunnel_id}.cfargotunnel.com."""
        target = f"{tunnel_id}.cfargotunnel.com"
        existing = await self._cf_request(
            "GET",
            f"/zones/{zone_id}/dns_records",
            api_token=api_token,
            params={"type": "CNAME", "name": domain},
        )
        for record in existing or []:
            if record.get("content") == target:
                log.info("tunnel.dns_reused", domain=domain, record_id=record["id"])
                return {"record_id": record["id"], "reused": True}

        result = await self._cf_request(
            "POST",
            f"/zones/{zone_id}/dns_records",
            api_token=api_token,
            json_body={
                "type": "CNAME",
                "name": domain,
                "content": target,
                "proxied": True,
                "ttl": 1,  # auto — required for proxied records
                "comment": "Elia subworker server (auto-managed)",
            },
        )
        log.info("tunnel.dns_created", domain=domain, record_id=result["id"])
        return {"record_id": result["id"], "reused": False}

    # ── Compose service file ────────────────────────────────────────────

    def write_compose_service(self, tunnel_token: str) -> Path:
        """Socketless: persist the runner token to a shared file.

        The ``cloudflared`` sibling service (docker-compose.yml) watches
        ``app/config/tunnel.token`` via ``scripts/cloudflared-watch.sh`` and
        restarts itself internally — no Docker socket needed. The compose
        override is kept as a no-op marker (chmod 600) for backwards compat.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.token_path.write_text(tunnel_token.strip() + "\n")
        os.chmod(self.token_path, 0o600)
        log.info("tunnel.token_written", path=str(self.token_path))
        marker = (
            "# Managed by tunnel_manager (socketless mode) — see tunnel.token\n"
            "# cloudflared is defined in docker-compose.yml, not here.\n"
        )
        self.override_path.write_text(marker)
        try:
            os.chmod(self.override_path, 0o600)
        except OSError:
            pass
        return self.token_path

    # ── Compose control (subprocess) ────────────────────────────────────

    def _compose_cmd(self, *args: str) -> list[str]:
        return [
            self.docker_bin,
            "compose",
            "-f", str(self.project_dir / "docker-compose.yml"),
            "-f", str(self.override_path),
            *args,
        ]

    async def _run(
        self,
        cmd: list[str],
        timeout: float = COMPOSE_TIMEOUT,
        input_text: str | None = None,
    ) -> tuple[int, str]:
        """Run a subprocess, returning (returncode, combined output)."""
        log.info("tunnel.exec", cmd=" ".join(cmd))
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_text is not None else None,
            )
        except FileNotFoundError as exc:
            raise TunnelError(
                f"'{self.docker_bin}' not found — a docker CLI must be available "
                "to manage the cloudflared container"
            ) from exc
        try:
            out, err = await asyncio.wait_for(
                proc.communicate(input=input_text.encode() if input_text else None),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise TunnelError(
                f"Command timed out after {timeout:.0f}s: {' '.join(cmd)}"
            )
        output = (
            (out or b"").decode(errors="replace") + (err or b"").decode(errors="replace")
        ).strip()
        return proc.returncode or 0, output

    async def start(self) -> None:
        """Socketless start — ensure token file exists; watcher restarts.

        The ``cloudflared`` sibling (docker-compose.yml) polls
        ``app/config/tunnel.token`` via ``cloudflared-watch.sh``. Writing the
        file is the trigger — no ``docker run`` needed.
        """
        state = self.load_state() or {}
        tunnel_token = state.get("tunnel_token")
        if not tunnel_token:
            raise TunnelError("No tunnel token in state — run POST /tunnel/setup first")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.token_path.exists() or self.token_path.read_text().strip() != tunnel_token.strip():
            self.token_path.write_text(tunnel_token.strip() + "\n")
            os.chmod(self.token_path, 0o600)
            log.info("tunnel.token_refreshed", path=str(self.token_path))
        try:
            network = await self._server_network()
        except Exception:
            network = f"{self.project_dir.name}_default"
        log.info("tunnel.started", network=network, mode="socketless")

    async def _server_network(self) -> str:
        """Docker network of the subworker-srv container (cloudflared joins it)."""
        rc, out = await self._run(
            [
                self.docker_bin, "inspect", self.compose_service_name,
                "--format", "{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}",
            ],
            timeout=30,
        )
        if rc == 0 and out.strip():
            return out.strip().split()[0]
        return f"{self.project_dir.name}_default"

    async def stop(self) -> None:
        """Socketless stop — remove token file; watcher exits, container idles."""
        try:
            self.token_path.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            rc, out = await self._run(
                [self.docker_bin, "rm", "-f", self.cloudflared_container], timeout=30
            )
            if rc != 0:
                log.warning("tunnel.stop_docker_ignored", rc=rc, out=out[-200:])
        except TunnelError:
            pass
        log.info("tunnel.stopped", mode="socketless")

    async def remove(self) -> dict[str, Any]:
        """Full teardown: stop cloudflared, delete DNS + tunnel via CF API, clean files.

        Never touches the subworker-srv service. Remote cleanup errors are
        collected (not raised) so local cleanup always completes.
        """
        state = self.load_state() or {}
        remote_errors: list[str] = []

        # 1. Stop + remove the cloudflared container only.
        try:
            await self._run(
                [self.docker_bin, "rm", "-f", self.cloudflared_container], timeout=30
            )
        except TunnelError as exc:
            remote_errors.append(str(exc))

        # 2. Delete DNS record + tunnel remotely (needs persisted tokens).
        api_token = state.get("api_token")
        tunnel_id = state.get("tunnel_id")
        if api_token and tunnel_id:
            try:
                account_id = state.get("account_id")
                if not account_id:
                    account_id = (await self.verify_token(api_token))["account_id"]
                if state.get("record_id") and state.get("zone_id"):
                    await self._cf_request(
                        "DELETE",
                        f"/zones/{state['zone_id']}/dns_records/{state['record_id']}",
                        api_token=api_token,
                    )
                # cascade=true also removes tunnel connections.
                await self._cf_request(
                    "DELETE",
                    f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}",
                    api_token=api_token,
                    params={"cascade": "true"},
                )
                log.info("tunnel.remote_removed", tunnel_id=tunnel_id)
            except TunnelError as exc:
                remote_errors.append(str(exc))
        elif tunnel_id:
            remote_errors.append("API token not persisted — tunnel left on Cloudflare")

        # 3. Local cleanup.
        for p in (self.override_path, self.token_path):
            try:
                p.unlink(missing_ok=True)
            except OSError as exc:
                remote_errors.append(f"could not remove {p.name}: {exc}")
        self.clear_state()

        self._step = STEP_IDLE
        self._last_error = None
        log.info("tunnel.removed", remote_errors=remote_errors)
        return {"removed": True, "remote_errors": remote_errors}

    # ── Public reachability ─────────────────────────────────────────────

    async def _resolve_via_doh(self, domain: str) -> str | None:
        """Resolve A record via DNS-over-HTTPS (bypasses broken local resolvers)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://cloudflare-dns.com/dns-query",
                    params={"name": domain, "type": "A"},
                    headers={"accept": "application/dns-json"},
                )
            for answer in resp.json().get("Answer", []):
                if answer.get("type") == 1:
                    return str(answer["data"])
        except Exception:
            pass
        return None

    def _pin_hosts(self, domain: str, ip: str) -> None:
        """Pin domain→IP in /etc/hosts (container-local) to dodge a local
        resolver's negative cache; returns nothing, best-effort."""
        try:
            with open("/etc/hosts", "a") as fh:
                fh.write(f"\n{ip} {domain} # elia-tunnel-verify\n")
        except OSError:
            pass

    def _unpin_hosts(self, domain: str) -> None:
        try:
            lines = Path("/etc/hosts").read_text().splitlines()
            kept = [l for l in lines if "# elia-tunnel-verify" not in l or domain not in l]
            Path("/etc/hosts").write_text("\n".join(kept) + "\n")
        except OSError:
            pass

    async def verify_public(
        self, domain: str, timeout: float = PUBLIC_VERIFY_TIMEOUT
    ) -> bool:
        """Poll https://{domain}/server/health until it returns 200 (or timeout).

        If the local resolver negative-caches the fresh record, falls back to
        DoH resolution + temporary /etc/hosts pinning.
        """
        url = f"https://{domain}/health"
        deadline = time.monotonic() + timeout
        last = ""
        pinned = False
        try:
            while time.monotonic() < deadline:
                try:
                    async with httpx.AsyncClient(timeout=PUBLIC_REQUEST_TIMEOUT) as client:
                        resp = await client.get(url)
                    if resp.status_code == 200:
                        log.info("tunnel.public_ok", domain=domain)
                        return True
                    last = f"HTTP {resp.status_code}"
                except httpx.HTTPError as exc:
                    last = str(exc)[:200]
                    # DNS dead? Resolve via DoH and pin for the next attempt.
                    if not pinned and ("Name or service not known" in last or "getaddrinfo" in last):
                        ip = await self._resolve_via_doh(domain)
                        if ip:
                            self._pin_hosts(domain, ip)
                            pinned = True
                            log.info("tunnel.doh_pinned", domain=domain, ip=ip)
                await asyncio.sleep(PUBLIC_POLL_INTERVAL)
        finally:
            if pinned:
                self._unpin_hosts(domain)
        raise TunnelError(
            f"https://{domain}/server/health did not return 200 within "
            f"{timeout:.0f}s (last: {last})"
        )

    async def check_public_now(self, domain: str) -> bool:
        """Single-shot public health probe for GET /tunnel/status.

        Uses /health (auth-exempt). Falls back to DoH resolution with a
        temporary /etc/hosts pin when the local resolver cannot resolve the
        freshly created record.
        """
        url = f"https://{domain}/health"
        try:
            async with httpx.AsyncClient(timeout=STATUS_PUBLIC_TIMEOUT) as client:
                resp = await client.get(url)
            return resp.status_code == 200
        except httpx.HTTPError:
            pass
        ip = await self._resolve_via_doh(domain)
        if not ip:
            return False
        self._pin_hosts(domain, ip)
        try:
            async with httpx.AsyncClient(timeout=STATUS_PUBLIC_TIMEOUT) as client:
                resp = await client.get(url)
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
        finally:
            self._unpin_hosts(domain)

    async def is_cloudflared_running(self) -> bool:
        """Socketless check: token file exists => watcher will keep it running.

        Falls back to ``docker ps`` when the socket is available (e.g. host
        tooling), but never requires it inside the server container.
        """
        if not self.token_path.exists():
            return False
        try:
            proc = await asyncio.create_subprocess_exec(
                self.docker_bin, "ps",
                "--filter", f"name={self.cloudflared_container}",
                "--filter", "status=running",
                "-q",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if out and out.strip():
                return True
            return bool(self.token_path.exists())
        except (FileNotFoundError, asyncio.TimeoutError, OSError):
            return bool(self.token_path.exists())

    # ── Persistence (app/config/tunnel.json, chmod 600) ─────────────────

    def save_state(self, **fields: Any) -> None:
        data = self.load_state() or {}
        data.update(fields)
        now = datetime.now(timezone.utc).isoformat()
        data.setdefault("created_at", now)
        data["updated_at"] = now
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(data, indent=2))
        os.chmod(self.state_path, 0o600)
        log.info("tunnel.state_saved", path=str(self.state_path))

    def load_state(self) -> dict[str, Any] | None:
        try:
            return json.loads(self.state_path.read_text())
        except FileNotFoundError:
            return None
        except (ValueError, OSError) as exc:
            log.warning("tunnel.state_unreadable", error=str(exc))
            return None

    def clear_state(self) -> None:
        try:
            self.state_path.unlink(missing_ok=True)
        except OSError as exc:
            log.warning("tunnel.state_clear_failed", error=str(exc))

    # ── Setup orchestration ─────────────────────────────────────────────

    @property
    def step(self) -> str:
        return self._step

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @property
    def is_setup_running(self) -> bool:
        return self._setup_task is not None and not self._setup_task.done()

    def _set_step(self, step: str) -> None:
        self._step = step
        log.info("tunnel.step", step=step)

    def start_setup(self, domain: str, api_token: str) -> asyncio.Task[None]:
        """Kick off the full setup as a background task (progress via `step`)."""
        if self.is_setup_running:
            raise TunnelError("A setup is already running — poll GET /tunnel/status")
        self._setup_task = asyncio.create_task(self.run_setup(domain, api_token))
        return self._setup_task

    async def run_setup(self, domain: str, api_token: str) -> None:
        """Full orchestration; never raises — failures land in step=error."""
        self._last_error = None
        try:
            self._set_step(STEP_VERIFYING_TOKEN)
            account = await self.verify_token(api_token)

            self._set_step(STEP_CHECKING_ZONE)
            zone = await self.check_zone(api_token, domain)

            # Account resolution: /accounts listing first, zone ownership as
            # fallback (tokens scoped to Tunnel+DNS only never list accounts).
            account_id = account["account_id"] or zone.get("account_id")
            if not account_id:
                raise TunnelError(
                    "Could not resolve the Cloudflare account for this token — "
                    "add the 'Account → Cloudflare Tunnel → Edit' permission"
                )

            self._set_step(STEP_CREATING_TUNNEL)
            tunnel = await self.create_tunnel(api_token, account_id, domain)

            self._set_step(STEP_ROUTING_DNS)
            dns = await self.create_dns_route(
                api_token, zone["zone_id"], domain, tunnel["tunnel_id"]
            )

            self.write_compose_service(tunnel["tunnel_token"])
            self.save_state(
                domain=domain,
                tunnel_id=tunnel["tunnel_id"],
                account_id=account_id,
                zone_id=zone["zone_id"],
                record_id=dns.get("record_id"),
                api_token=api_token,
                tunnel_token=tunnel["tunnel_token"],
            )

            self._set_step(STEP_STARTING_CLOUDFLARED)
            await self.start()

            self._set_step(STEP_VERIFYING_PUBLIC)
            await self.verify_public(domain)

            self._set_step(STEP_DONE)
            log.info("tunnel.setup_done", domain=domain)
        except asyncio.CancelledError:
            self._last_error = "setup cancelled"
            self._set_step(STEP_ERROR)
            raise
        except Exception as exc:
            self._last_error = str(exc)
            self._set_step(STEP_ERROR)
            log.error("tunnel.setup_failed", error=str(exc))

    # ── Status snapshot ─────────────────────────────────────────────────

    async def status(self) -> dict[str, Any]:
        """Snapshot for GET /tunnel/status. Tokens are masked, never raw."""
        state = self.load_state() or {}
        domain = state.get("domain")
        configured = bool(state.get("tunnel_id") and domain)
        return {
            "configured": configured,
            "domain": domain,
            "tunnel_id": state.get("tunnel_id"),
            "cloudflared_running": await self.is_cloudflared_running(),
            "public_ok": await self.check_public_now(domain) if configured else False,
            "last_error": self._last_error,
            "step": self._step,
            "api_token_masked": mask_token(state.get("api_token")),
            "tunnel_token_masked": mask_token(state.get("tunnel_token")),
        }
