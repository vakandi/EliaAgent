# EliaAgent Release Notes

## Version: v6.5.0 (October 7, 2026)

### 🔀 Harness Parity — the same fleet on two more engines

The reference server runs OpenCode inside FastAPI. That was the only engine.
This release adds **two more harnesses that speak the identical TopBar
contract**, so the same agent registry, schedules, personas and clients run
unchanged on a different runtime:

- **`subworkers-qwen/`** — a lighter side-by-side stack. A FastAPI **shim** on
  `:5676` that drives `opencode run --format json` as a subprocess, with a Qwen
  daemon kept as a dormant sidecar on internal `:4170`. Same 25-agent shape,
  same routes, smaller footprint.
- **`subworkers-omp/`** — a **Bun/TypeScript** re-implementation of the server
  on the [omp](https://github.com/can1357/oh-my-pi) SDK (`createAgentSession`).
  **Zero Python.** Listens on `:5677`.

Both are side-by-side. The reference server keeps running on `:5655`/`:5656`,
and neither new harness touches it.

```bash
cd subworkers-qwen && docker-compose up -d --force-recreate shim qwen
cd subworkers-omp && ./install.sh && ./start.sh --docker
# then: EliaTopBar -> Change Server URL -> http://127.0.0.1:5677  (or :5676)
```

**What is *not* committed here.** `subworkers-omp` ships the Elia wrapper layer
only — upstream omp (`omp-server/packages`, `crates`, `assets`, ~180 MB, MIT) is
fetched by `install.sh` at the pinned ref `78b7531` via sparse checkout, so the
public repo stays at 408 KB instead of 184 MB. Pass `--skip-upstream` if you
already have the checkout. Agent workspaces, prompts, personas, memories, the
auth store and the session DB are excluded from both harnesses; both ship a
randomized 5-agent registry and one worked example so the schema is obvious.

---

### Compatibility matrix

Verified by reading the shipped routers, not by assumption.

**Transport**

- Reference: FastAPI + uvicorn on `:5656`, `opencode serve` on `:5655`
- `subworkers-qwen`: FastAPI + uvicorn on `:5676`, engine = `opencode run`
  subprocess, `qwen` daemon internal `:4170` (expose-only), forward proxy
  internal `:3128`, attest shim internal `:3129`
- `subworkers-omp`: `Bun.serve` on `:5677`, engine = omp SDK in-process

**Auth** — identical on all three

- HTTP: `Authorization: Bearer <token>` or `X-Elia-Token: <token>`
- WebSocket: `?token=` or the two headers above (omp also accepts
  `Sec-WebSocket-Protocol`)
- Exempt: `/health` only. Empty `ELIA_AUTH_TOKEN` disables the check — loopback only.

**REST routes** — reference, qwen and omp all implement

`GET /health` · `GET /server/health` · `GET /status` · `GET /status/{name}` ·
`PUT /status/{name}` · `POST /trigger/{name}` · `POST /enable/{name}` ·
`POST /disable/{name}` · `POST /config/reload` · `GET /logs/{name}` ·
`GET /sessions/{name}` · `GET /sessions/{name}/list` ·
`POST /sessions/{name}/{id}/continue` · `GET /sessions/{name}/{id}/events` ·
`GET /models` · `GET/POST /main-agent` · `POST /server/restart` ·
`POST /server/cleanup` · `GET /tunnel/status` · `POST /tunnel/check` ·
`POST /tunnel/setup` · `POST /tunnel/stop` · `POST /tunnel/remove` · `WS /ws`

Harness-specific extras (not required by the client):

- omp only: `POST /sessions/{name}/{id}/stop`, `POST /test/frames/{name}`
  (synthetic `text|reasoning|tool` frames, no engine, no credentials)
- qwen only: `GET /daemon/status`, `POST /check`, `POST /setup`, `POST /stop`,
  `POST /remove`

**WebSocket events** — where the two harnesses actually differ

| Event | reference | qwen | omp |
|---|---|---|---|
| `initial_status` | ✅ | ✅ | ✅ |
| `run_log` (+ `field`) | ✅ | ✅ | ✅ |
| `run_banner` | ✅ | ✅ | ✅ |
| `subworker_completed` | ✅ | ✅ | ✅ |
| `status_update` | ✅ | ❌ | ✅ |
| `subworker_started` | ✅ | ❌ | ✅ |
| `subworker_success` | ✅ | ❌ | ✅ |
| `subworker_cancelled` | ✅ | ❌ | ✅ |
| `subworker_error` | ✅ | ⚠️ `subworker_failed` | ✅ |
| `models_version` | ✅ | ❌ | ✅ |
| `pong` | ✅ | ❌ | ✅ |

**Read that table before pointing TopBar at `:5676`.** The qwen shim's routes are
a path-for-path mirror, but its event vocabulary is not: it emits five event
names, not eleven. Clients that render *live agent state* from `status_update`
or *run outcome colour* from `subworker_success` will fall back to polling
`GET /status` and will paint a failed run with the completed-run styling.
`subworkers-omp` is the parity-complete one. This is a documented gap in the
harness, not in the contract — `SubworkerManager.swift` remains the client of
record.

**Registry schema** — identical in all three `subworkers.json`

`name` · `enabled` · `schedule{type: interval|every|cron, hours, minute, days,
every, expression}` · `prompt_file` · `workspace` · `agent_id` · `model` ·
`variant` · `max_retries` · `timeout_minutes` · `proxy_enabled` · `mcp_servers[]`
· `notify_discord`. `days` is cron convention, `0 = Sunday`.

**Models** — the provider id differs by harness, and getting it wrong fails silently

- Reference + qwen: `opencode/<model>` through the baked `opencode.json`
  (`provider: zen-free`)
- omp: `zen-free/<model>` from your own `~/.omp/agent/models.yml`
- **An unknown model id is not an error.** The run starts, completes in seconds
  and emits zero frames, because the turn falls back to the default provider
  model. Triage in this order: `data/frames/<session>.jsonl` (prompts only?) →
  `/root/.omp/logs/omp.*.log` (which `provider/model` actually ran?) → the
  registry entry. Never blame a provider key before that chain.
- omp: an entry on `opencode/*` rather than `zen-free/*` is a known live-config
  bug fixed in the shipped template.

**Scheduler** — omp adds cron; all three support `interval`, `every`, and
clock-aligned hours. `next_run` persists in `data/state.json`.

**Concurrency and admission**

- reference: `MAX_CONCURRENT_RUNS=100`; over-cap runs previously queued invisibly
- qwen: `MAX_CONCURRENT_RUNS=8` (default)
- omp: `MAX_CONCURRENT_RUNS=8`, hard cap 100 → over cap answers HTTP **202**
  `{"status":"queued_429"}`. `admitRun()` fsyncs the run record **before**
  responding, so a 202 is durable, not advisory.

**Stall and run ceilings** — same two knobs, same names

`STALL_TIMEOUT_S` (300) with no frames → mark failed + error banner + notify.
`MAX_RUN_S` (3600) absolute → mark failed. Neither harness uses an RSS-cap gate;
the container `mem_limit` is the only memory guard (a cap gate fought the OOM
killer and lost).

**Proxy rotation**

- reference: Node forward proxy on `127.0.0.1:3128`, round-robin per request
- qwen: same shape, plus a 4-minute forced LRU swap and `POST /__rotate`; a 429
  rotates egress and retries once, then reports `queued_429`
- omp: **in-process** `extensions/proxy-local.ts`, vendored and loaded per
  worker — no forwarding daemon, no extra container. Oldest-unused entry wins,
  forced 4-minute swap, and after a rate-limit error it swaps proxy *and* sends
  a continuation message so the run carries on. Model traffic is proxied; agent
  tool shells stay direct. Pool: `omp-server/extensions/proxies.txt`
  (`host:port:user:pass |last:<ts>`). Empty pool fails open to direct.
- All three fail open when the pool is empty or the proxy is down.

**Tunnel** — socketless everywhere

No `docker.sock` mount in any of the three. Cloudflared is a sidecar polling
`config/tunnel.token` (mode 600) on an md5/5s file watcher. A missing token never
crash-loops the default stack: the sidecar is opt-in (`--profile tunnel`, or
`start.sh --with-tunnel`). Docker socket access would let any agent
`docker run -v /:/host alpine` and read host SSH keys and cookies.

**Frame model** — one shape across harnesses

`field ∈ text | reasoning | tool`. Tool frames carry **name + status only, never
payloads**. An abrupt SSE close is a clean EOF, never a 500.

**Secrets layout**

- reference / qwen: `.env` (mode 600), gitignored
- omp: `omp-server/.env`, `config/tunnel.json`, `config/tunnel.token`,
  `extensions/proxies.txt`, `data/` — all gitignored; `.example` files shipped
  for each

---

### Upgrade notes

- **Nothing to migrate.** Both harnesses are additive. Existing
  `subworkers/server/` deployments, configs, workspaces and sessions are
  untouched by this release.
- `install.sh` gained `--skip-upstream`. Without it, `install.sh` fetches
  upstream omp on first run; with an existing checkout it detects the source and
  skips the clone. Existing installs are unaffected.
- The shipped `subworkers.json` in both new harnesses is a **randomized
  5-agent template**. Replace it with your own registry — it is not the
  production roster.
- **Model ids in the templates are examples.** Validate each one against your
  `opencode.json` / `models.yml` before enabling an agent, per the silent-fallback
  behaviour above.

---

## Version: v6.4.0 (September 15, 2026)

### 🚀 Host MCP Parity + Full-Parallel Fleet + Headless Browser

**No more tool excuses:**
- Host `~/Documents` mounted read-only at the identical path — every `npx`,
  plain-`python3`, and node MCP server resolves in-container with zero copies
  and zero config edits; `uv` runtime added to the image
- Verified live inside the container: parallel-browser sessions, dashboard
  sprints, multi-account social stats — read-only calls tested green
- `agent-browser` CLI (headless) + Playwright ARM64 Chromium baked into the
  image — agents browse without any host browser wrapper or profile
- Tier list documented (`SUBWORKERS_SYSTEM.md` §8.10): `uv`-based and
  macOS-binary servers stay host-only by design

**Full parallelism (the "same process" bug):**
- `MAX_CONCURRENT_RUNS` raised to 100 — scheduled agents no longer queue
  invisibly behind a cap of 2 (`running:true` with no session); each run gets
  its own opencode session + isolated workspace + rotated egress IP, so the
  whole fleet fires at the same slot without stepping on each other

**Fresh-start recovery:**
- Full Docker nuke path verified (VM disk 98% → 0% free): scheduler state,
  session DB, and run logs all survive via bind-mounts; stack rebuilds clean
  with `docker-compose up -d --build`

**Idle cleaner (new `app/services/idle_cleanup.py`):**
- When all enabled subworkers sit idle past `IDLE_TIMEOUT` (300s), the server
  kills stale `parallel-browser-mcp` + headless Chrome processes that eat
  container RAM — no more OOM-kills from leftover browser instances; opencode
  restarts automatically if cleanups pile up (`IDLE_CHECK_INTERVAL=30`)

---

## Version: v6.3.0 (August 30, 2026)

### 🔧 Socketless Hardening + Global API Key + Warmup Fix

**Security:**
- `elia-subworker-srv` no longer mounts `/var/run/docker.sock` (agents can't escape via `docker run -v /:/host`)
- `cloudflared` now sidecar `alpine` with file-watcher `cloudflared-watch.sh` polling `tunnel.token` md5/5s (no Docker socket)
- `docs`/`openapi.json` now `404` (was 200 public), all `…/status` require `Bearer` (401 without, 200 with)

**Cloudflare Tunnel Global API Key:**
- `POST /tunnel/setup` now accepts `global_key` (cfk_...) + `email` and auto-mints restricted Bearer (`Zone DNS Write` + `Tunnel Write`) via `X-Auth-Email/Key`
- TopBar + Android wizards now have `Global API Key` + `Email` fields, auto-detect `cfk_` prefix

**Stability:**
- `forward-proxy.js` now bypasses `127.0.0.1/localhost` for both HTTP and CONNECT (fixes opencode `GET /session?limit=...` 15s timeout via proxy)
- `app/main.py` startup warmup for sessions DB (fixes 1-session-0-msg cold start after reboot)
- `subworkers.py` `/list` timeout 10→20s and limit 200→50 with fallback to 20 (4.4s vs 15s)
- Handles duplicate tunnel name (1013) by reusing or unique suffix

---

---

## Version: v6.2.0 (August 30, 2026)

### 🌐 Per-Session Proxy Rotation — Unlimited Tokens on Free Models

The fleet now rotates **residential egress IPs per request**, so free OpenCode Zen models
rate-limited per IP scale linearly across concurrent sessions. 14 agents firing at once
each get a different upstream IP — no more instant 429s.

**What changed:**
- **Node forward proxy on `127.0.0.1:3128`** (`app/forward-proxy.js`, `http` + `net` `CONNECT` handling). Pool loaded at startup, round-robin per request. `entrypoint.sh` sets `HTTP_PROXY=http://127.0.0.1:3128` + `NO_PROXY=localhost,127.0.0.1,::1` before starting `opencode serve --port 5655`. Every `fetch`/`CONNECT` from opencode goes through the local proxy → next residential proxy.
- **Why a forward proxy** (not a `fetch({proxy})` patch or plugin): the `BUN_PRELOAD` patch produced `<defunct>` zombies (uvicorn as PID1 never reaped), and the plugin approach runs after the provider `fetch` is cached — too late. The forward proxy is the only stable per-request isolation that works with the **release binary** + Effect fibers at 14 concurrent.
- **Zombie fix**: `tini -g` is now PID1 + an entrypoint supervisor loop auto-restarts opencode in 2s on OOM/crash. Verified `ps aux` shows no defunct after `pkill -9 opencode`.
- **Warmup**: `docker_subworker.sh` warms the sessions DB before the first run (prevents the 1-session-0-msg cold start).
- **Continue fix**: `subworkers.py` `/list` timeout `5s→10s` + warning log; `/sessions` catches `OpenCodeConnectionError` → 200 empty instead of 500. Fixes "1 session 0 msg" when opencode is slow.
- **Infinite restart loop**: `opencode-serve.sh` now restarts forever (100% uptime as long as the host is up) instead of giving up after `MAX_RESTARTS`.
- **Routes resilience**: graceful degrade + continue broadcast so a slow opencode never takes the whole fleet down.

**Failure mode:** falls back to a direct IP (fail-open) if the pool is empty or the forward proxy is down.

**Verify:**
```bash
docker exec elia-subworker-srv curl -x http://127.0.0.1:3128 -s https://api.ipify.org  # proxied IP
docker exec elia-subworker-srv curl -s https://api.ipify.org                            # direct IP
docker exec elia-subworker-srv cat /data/logs/forward-proxy.log | tail -20              # CONNECT opencode.ai via <proxy>
curl http://localhost:5656/health
```

---

## Version: v6.1.0 (August 24, 2026)

### 📱 Official Clients: macOS TopBar + Mobile App · 🌍 Remote Access via Cloudflare Tunnel

The ecosystem now ships two first-class clients for managing your subworkers in realtime,
plus secure remote access from anywhere.

**macOS — EliaTopBar (native Swift menu-bar app):**
- Full realtime subworker dashboard over WebSocket: live agent states (running/idle/error/done), running counts, server health
- Chat & session viewer with streaming output, reasoning blocks and tool-call details
- Trigger / enable / disable, model + reasoning-variant switching, main-agent control
- One-click Cloudflare Tunnel setup and a live tunnel status indicator

**Mobile — EliaSubworkers (Android today, iOS-ready · Expo / React Native):**
- Same realtime dashboard optimized for touch, with automatic LAN discovery
- Chat & sessions browser per agent: markdown rendering, collapsible reasoning, tool-call details
- Schedule calendar projecting interval & cron runs across the week, with collision picker
- Run notifications (finish / fail), profile photos, shared-token auth

**🌍 Cloudflare Tunnel remote access (both clients):**
- In-app wizard: domain + Cloudflare API token → automatic tunnel creation, DNS routing,
  connector startup and public verification — step by step
- Permanent by design: the `cloudflared` connector restarts with Docker; set it up once
- Shared-token auth (`ELIA_AUTH_TOKEN`) protects every HTTP call and WebSocket handshake
- Deployable anywhere: run the stack on your Mac or a VPS and reach it from any network

**Links:** [EliaTopBar](https://github.com/vakandi/Elia-Topbar) · [EliaAndroidApp](https://github.com/vakandi/EliaAndroidApp)

---

## Version: v6.0.2 (August 25, 2026)

### 🐛 Critical Fix: Subworkers Were Running With a Placeholder Prompt

**Every scheduled subworker run sent a generic placeholder instead of the agent's real `PROMPT.md`.** The runner had a shortcut: when an `agent_id` was configured (the case for all subworkers), it skipped reading `PROMPT.md` and sent a one-line "Execute the <name> subworker task" instruction. Agents were effectively running on their personality file alone — no workspace constraints, no handoff protocol, no task-specific business logic.

**Fix**
- `PROMPT.md` is now **always loaded and sent as the user message**, regardless of `agent_id`
- Robust path resolution: `workspace/prompt_file` → subworker root (`PROMPT.md` next to `workspace/`) → `/data/subworkers/<name>/` container layout
- Placeholder only remains as last-resort fallback when no prompt file exists anywhere (logged loudly)
- Tests updated to lock the correct behavior + new test for the root-level layout

**Also in this sync**
- Cloudflare Tunnel management routes (`/tunnel/*`) + tunnel manager service — setup wizard backend for the EliaTopBar/EliaAndroidApp remote-access feature
- Reasoning-variant support end-to-end: config → runner → OpenCode `send_message(variant=...)`
- Progress streamer now starts before the blocking `send_message` call (realtime logs during long runs)
- `GET /models` catalog endpoint for UI model pickers

---

## Version: v6.0.1 (August 25, 2026)

### 🖥️ UI Electron Sync & WebSocket Fix

**Bug Fixes**
- Fixed `WebSocket is not defined` crash: the Electron main process now uses the `ws` package for the realtime subworker connection (`ws://127.0.0.1:5656/ws`) with exponential-backoff reconnect

**New Features**
- Subworker popup: full model catalog fetched from `GET /models`, two-step selection (model → thinking variant), persisted per agent via `PUT /status/{name}`
- Scheduler-disable guard in desktop shortcuts (`touch ~/EliaAI/.scheduler_disabled` kills all scheduled runs)

**Cleanup**
- Removed hardcoded personal paths → relative paths via `EliaAIRoot`
- Removed stale `EliaUI.app` binary bundle from desktop shortcuts
- New UI assets (icons, tray images)

---

## Version: v6.0.0 (August 24, 2026)

### 🐳 Subworkers System v4 — Dockerized, Deployable Anywhere

**The subworker system was completely rebuilt.** The old launchd + bash/Node.js trigger stack (v3) is replaced by a **Python FastAPI server running in Docker** — deployable on any Mac or VPS.

| | Old (v3) | New (v4) |
|--|----------|----------|
| Scheduling | 14 launchd plists | `subworkers.json` + APScheduler (hot-reloaded) |
| Runtime | Shell + Node.js triggers | Python FastAPI in Docker (port 5656) |
| Completion detection | Log-file EOF marker parsing | Multi-layer API + process polling |
| Error handling | None | ErrorParser (10 error types) + exponential backoff retries |
| Alerts | None | macOS beep + Electron + ntfy.sh |
| Status view | 14 separate log files | REST API + WebSocket realtime |

**Why it matters:** OpenCode has known memory leaks that previously caused real CPU/RAM blowups when many agents ran concurrently. The Docker server isolates and contains that — **thousands of sessions on only 4 GB of RAM**, with Colima handling Docker resource management on macOS and HealthManager auto-recovering crashed OpenCode server processes.

**Highlights**
- Runs drive the host OpenCode server over its HTTP API (`POST /session` + `/message`) — no CLI spawned inside the container
- Session persistence survives full Docker nukes (`scheduler_state.json` bind-mounted to host)
- Main-agent-as-subworker: Elia is managed like any other agent via `GET/POST /main-agent`
- Full control from EliaTopBar / EliaUI over REST + WebSocket (`/ws`)
- Team Mode cleanup: all upstream/team-specific references scrubbed for public release
- Docs: companion clients ([EliaTopBar](https://github.com/vakandi/Elia-Topbar), [EliaAndroidApp](https://github.com/vakandi/EliaAndroidApp)) & Cloudflare Tunnel remote access

**Docs:** See `subworkers/SUBWORKERS_SYSTEM.md` (v4.0) for the full architecture; `subworkers/SUBWORKERS_SYSTEM_OLD.md` keeps the legacy v3 reference.

---

## Version: v5.0.1 (July 12, 2026)

### 🛡️ Subworker Premature Completion Fix — 10 Critical Bugfixes

**Subworkers no longer die mid-task.** All 10 root causes of the "All tasks completed" false-positive and silent SSE stream death have been fixed in the oh-my-opencode CLI runner. Subworkers now survive long-running tasks with proper timeout handling, session-scoped event filtering, and continuous progress reporting.

**What changed:**
- **Fix #1** — `EVENT_PROCESSOR_SHUTDOWN_TIMEOUT_MS` raised from 2s → 10s to survive heavy event bursts
- **Fix #2** — Telemetry `capture()` failures caught and logged instead of crashing the runner
- **Fix #3** — Completion diagnostics (verbose mode) wrapped in try/catch — never crashes runner
- **Fix #4** — Unknown completion status no longer treated as idle — requires explicit `completed` or `failed`
- **Fix #5** — Null todo list guard — avoids crash when todo list hasn't been populated yet
- **Fix #6** — `requiredConsecutive` raised from 1 → 3 before declaring idle — prevents false positives during stalls
- **Fix #7** — `eventProcessorDied` flag — detects when the event processor crashes and stops poll loop
- **Fix #8** — Watchdog timer scoped to session — multi-session CLI no longer triggers false idle
- **Fix #9** — Toast notifications filtered by session ID — cross-session toasts no longer corrupt state
- **Fix #10** — `eventProcessorDied` field added to event state — wired through completion detection

**Impact:** Subworkers that previously died after 5-10 minutes of heavy tool use now survive indefinitely. The trigger template, launchd plists, and personality injection are unchanged — only the CLI runner internals were fixed.

**Files modified:** `runner.ts`, `completion.ts`, `poll-for-completion.ts`, `event-stream-processor.ts`, `event-toast-handlers.ts`, `event-state.ts`

**Docs:** See `setup/OH-MY-OPENCODE-CHANGES.md` for the full technical breakdown.

---

## Version: v4.1.0 (July 10, 2026)

### 🚀 Unified Subworker Lifecycle Manager + Security Hardening

**One script to rule all subworkers.** The new `manage_subworkers.sh` replaces the ad-hoc cron-based management with a single command for the full launchd lifecycle on macOS.

**What changed:**
- **Unified Lifecycle Manager** (`scripts/manage_subworkers.sh`) — 6 commands: `default` (status table), `enable`, `disable`, `status`, `install`, `uninstall`. Handles bootstrap for loading agents, bootout for unloading, and plist management across both the project `subworkers/plists/` directory and `~/Library/LaunchAgents/`.
- **`.enabled` File Convention** — Master switch per subworker. Remove a single file = emergency stop without launchctl interaction. The `disable` command additionally marks `Disabled=true` in the plist and unloads from launchd.
- **Color-Coded Status Table** — Default view shows a formatted table with ENABLED/PLIST/LAUNCHD/SCRIPT columns for all subworkers at a glance.

**Security hardening:**
- **Removed 6 files with hardcoded secrets** — `yourapp_run.py` (Discord bot token, Telegram keys), `cloudconvert_md_to_docx.py` (JWT API key), `discord_send.py`, `google_workspace.py`, `captcha_solver.py` (OpenRouter key), `trigger_opencode_interactive.sh` (Jira/Atlassian tokens).
- **Sanitized all public-facing files** — Business names, server IPs, Discord channel IDs, and real paths replaced with placeholders. All 9 security checks from `SYNC_PROMPT.md` pass clean.
- **Created `context/` directory** with sanitized `TOOLS.md` and `business.md` for the public repo.

**New skills synced:**
- `hyperframes` / `hyperframes-cli` / `hyperframes-registry` — Video composition framework
- `gsap` — GSAP animation reference
- `directus-flows-skill` — Directus workflow automation
- `pdf-form-filler` — IRS/government XFA PDF form filling
- `best-heygen-image` — Blog hero image generation
- `vakandi-rapid-api-builder` — RapidAPI marketplace scaffolding
- `website-to-hyperframes` — Website-to-video conversion
- `ui-ux-pro-max-skill` — UI/UX design system
- `yourapp-ga-marketing-review` — GA4 analytics review

### Bug Fixes
- **Subworker plist conflict** — `yourapp-telegram` had both a managed plist and a stale manual plist in `~/Library/LaunchAgents/`. Cleaned up during lifecycle manager integration.
- **Missing tiktok-content plist** — Identified as blocker for enabling the tiktok-content subworker.

### Technical Details
- Script location: `scripts/manage_subworkers.sh` (403 lines, zsh)
- Subworker state tracked across 4 dimensions: `.enabled` file, plist presence, launchctl status, trigger script existence
- 6 subworkers: yourapp-telegram, YourBrand-promoter, youragency-promoter, YourBrand-suppliers, tempack-dev, tiktok-content
- All subworkers currently disabled — enable with `./manage_subworkers.sh enable <name>`

---

## Version: v4.0.0 (July 9, 2026)

### 🚀 Subworker Management System — Built for Organic Marketing at Scale

I built a complete subworker orchestration system with an Electron UI dashboard to run and monitor autonomous AI agents. This isn't just a task runner — it's a full marketing operations center.

**What I built:**
- **Subworker Engine** — Each agent gets its own identity (personality file), workspace (isolated directory), PROMPT.md, and per-run logging. The trigger template (`trigger_template.sh`) handles everything: PATH resolution for launchd, .enabled gating, personality injection, proxy support, and task/loop mode switching.
- **Electron UI Dashboard** — Real-time subworker management in a floating window. See every agent's status (● RUNNING / ○ STOPPED), enable/disable with toggle switches, browse per-run log history with time-ago badges, duration badges, and crash detection. The UI uses a unique `EOF_SUBWORKER_EXIT:<code>` marker — impossible for AI output to fake — to reliably detect completion vs crash.
- **Unique Exit Marker Protocol** — Every run log ends with `[timestamp] EOF_SUBWORKER_EXIT:<code>`. The UI parses this with absolute precision: exit 0 → green duration badge, exit non-zero → orange "(crashed)" badge, no marker → gray "???" badge for old logs. No false positives from AI output text.
- **Reliable Crash Recovery** — The shell script uses `set +e` / `set -e` wrapping to capture the exit code even on crashes, always writing the marker before propagating the real exit status. Failed runs show their partial duration instead of being indistinguishable from running agents.

**This powers a full organic marketing system:**
- Multi-platform content creation and scheduling agents
- Automated community engagement
- SEO content generation
- Social media promotion
- All running on cron schedules with the LaunchAgent integration

**Custom MCP Servers** — I built custom MCP servers to make this work seamlessly. The system integrates with the right tools for each platform. If you need specialized MCPs for your own automation stack, contact me — I build custom MCP servers tailored to your use case.

**Contact for custom MCP development**: Reach out to discuss your automation needs. I build production-ready MCP servers for any platform or workflow.

### New Features
- **Subworker Management UI** (`subworker-popup.html`) — Electron-based floating dashboard with per-agent status badges, enable/disable toggles, per-run log dropdown with time-ago + duration badges, crash detection via unique EOF marker.
- **Unique Exit Marker Protocol** — `EOF_SUBWORKER_EXIT:<code>` written at end of every run. Zero ambiguity between success, crash, and still-running. Backward compatible with old logs (shows gray "???" badge).
- **Robust Shell Exit Handling** — `set +e` wrapping around `oh-my-opencode run` captures exit code even on crash. The marker is always written before propagating the real exit status.
- **Status-Based Badge System** — Three-state rendering: green (success), orange (crashed with duration), gray (unknown — old log or unparseable), yellow (● RUNNING — agent still executing).
- **Fallback Duration Parsing** — Even without the unique marker, the UI scans for the last `[timestamp]` line to show partial duration for old or pre-marker logs.

### Bug Fixes
- **False "RUNNING" for old logs** — Previously, any log without a completion marker showed "RUNNING." Now shows gray "???" with partial duration if available.
- **Fuzzy "completed" regex parsing** — Removed unreliable `.*completed` matching that could false-trigger on AI output text. Replaced with exact unique marker match.
- **set -e crash masking** — `set -euo pipefail` was killing the trigger script before it could write the completion line on non-zero exits. Fixed with `set +e` wrapper.

### Technical Details
- Marker format: `[YYYY-MM-DD HH:MM:SS] EOF_SUBWORKER_EXIT:<exit_code>`
- Log parsing: reads first 300 bytes (head) for start timestamp, last 300 bytes (tail) for marker
- UI renders up to 100 most recent runs per subworker, newest first
- All trigger scripts share the template via `source trigger_template.sh` — one change propagates everywhere
- Node.js `--check` verified, no runtime dependencies added

---

## Version: v3.3.0 (July 8, 2026)

### New Features
- **Symlink integrity check in trigger_template.sh** — Automatically detects when `oh-my-opencode` bun global package is a symlink to a local source checkout (causes EPERM on macOS). Fails early with a clear fix message instead of a cryptic Node.js stack trace.

### Bug Fixes
- **Subworker EPERM crash resolved** — `oh-my-opencode` global package was a symlink to a clone in `nayo-app-fastapi` project. Reinstalled properly via `bun install -g oh-my-opencode`. All subworker triggers now work without macOS permission errors.

### Documentation
- **SUBWORKERS_SYSTEM.md** — Rewritten with Table of Contents, workspace isolation architecture, per-agent permissions, agent registration guide (opencode.json + oh-my-openagent.json + personality file + categories), and expanded troubleshooting section including the bun global symlink pitfall.
- **trigger_template.sh** — Added binary integrity check, updated example paths, cleaner structure.

### Technical Details
- `oh-my-opencode` upgraded from 3.17.2 → 4.16.0 (major version jump).
- Version 4.16.0 uses JS-based platform binaries instead of Mach-O executables.
- Trigger template now checks `~/.bun/install/global/node_modules/oh-my-opencode` for symlink status before running.