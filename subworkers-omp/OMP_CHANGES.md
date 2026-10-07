# OMP_CHANGES.md — what changed from stock omp to make this server

Checkout: fork of `oh-my-pi` @ `78b7531`, no remote, never fetch/pull.
Rule kept throughout: **zero edits to upstream source** (`omp-server/packages/`,
`omp-server/crates/`, `omp-server/scripts/`, …). Everything below is additive
or build-time only. Verify any time with:
`git status --short | grep -v '^??'` — only `AGENTS.md`, `README.md`,
`.gitignore`, `install/start/stop/reset.sh` and this file should ever show as
modified; `packages/` and `crates/` must stay clean.

## 1. Added: the wrapper server (`omp-server/*.ts`, `routes/`, `config/`)

Stock omp ships four entry points (interactive TUI, one-shot `-p`, RPC, ACP)
— all single-session, terminal-attached. This repo adds a fifth: a headless
multi-tenant HTTP+WS server (`Bun.serve` on `127.0.0.1:5677`) exposing the
EliaTopBar contract (`GET /status`, `POST /trigger/{name}`, session reads +
SSE, `/tunnel/*`, `/models`, `/main-agent`, `/ws`). New files only:

- `server.ts` — serve entry, Bearer gate, router, `/ws`, `HOST` env bind.
- `routes/` — `status.ts` (status/trigger/enable/disable/update/reload/logs),
  `sessions.ts` (get/list/continue/stop + SSE events), `serverRoutes.ts`
  (health/restart/cleanup), `misc.ts` (tunnel/models/main-agent/test-frames).
- `admit.ts` — synchronous admission: run record fsynced to
  `data/runs.json` BEFORE responding (<100 ms); over cap → HTTP 202
  `queued_429`. Fixes the "in-memory runs wiped on restart" class of bugs.
- `engine.ts` — the ONLY file that imports the omp SDK
  (`createAgentSession`). Lazy dynamic import so the listener boots without
  the native addon. Holds the `creationGate` mutex, the live-children kill
  registry, per-run rotation timers, and the worker-spawn path (below).
- `worker.ts` — one isolated Bun process per run (`Bun.spawn`), own
  `HTTPS_PROXY`, own `EventBus`/session. Speaks NDJSON frames over stdout,
  accepts `ROTATE <url>` over stdin. A dead worker fails exactly one run.
- `store.ts` — JSONL persistence (`data/runs.json`, `data/frames/*.jsonl`,
  `data/state.json`). Frame shape extends omp events with
  `{field: text|reasoning|tool, tool?, input?, output?}` for panel parsers.
- `scheduler.ts` — interval / clock-aligned `every` / cron, `next_run`
  persisted across restarts.
- `watchdog.ts` — stall (`STALL_TIMEOUT_S`, default 300) and max-runtime
  (`MAX_RUN_S`, default 3600) expiry: SIGKILLs the worker child, writes an
  error banner, fires Discord. No RSS-cap gates anywhere (container
  `mem_limit` is the only guard).
- `proxy.ts` — oldest-used (LRU) proxy pool from `config/proxies.txt`,
  distinct pick per concurrent session, forced 4-min rotation, no quarantine.
- `notifier.ts` — Discord webhook, 300 s debounce per (name, kind), never logs secrets.
- `tunnel.ts` + `tunnelWatch.sh` — socketless Cloudflare contract (token file
  only, chmod 600, sidecar restarts the sibling service, no `docker.sock`).
- `statusView.ts`, `auth.ts`, `ws.ts`, `testFrames.ts`, `contractCheck.ts`.
- `config/` — `subworkers.json` (25 agents, verbatim live registry, all
  disabled by default), `server.json` (`{port: 5677, concurrency: 8}`),
  `tunnel.token` + `proxies.txt` (both chmod 600, both gitignored).
- `extensions/proxy-local.ts` — vendored copy of the harness
  residential-forward extension, plus a `PROXY_LOCAL_NO_SPAWN=1` mode that
  rotates upstreams natively in-process (no shell script), and `ELIA_PROXY_LOG`
  log redirection. Workers load ONLY this copy
  (`disableExtensionDiscovery` + `additionalExtensionPaths`).

## 2. Behavior deltas vs stock omp (same SDK, different posture)

| Stock omp | This server |
|---|---|
| One interactive session per process | N isolated worker processes per listener |
| Proxy from process env, memoized per provider | Per-worker `HTTPS_PROXY` (distinct LRU proxy each) + in-worker forward extension (`PI_PROXY` → `127.0.0.1:18898`) with 4-min + on-error rotation |
| Extensions auto-discovered from agent dir | Explicit-only: vendored `extensions/` dir, nothing else loads |
| Bash children inherit a curated static env (no proxy vars) | Same (upstream design, kept): agent *tool* traffic stays direct; only *model* traffic is proxied — verified live (fetch → proxy IP, bash → host IP) |
| Session CWD = project dir | Session CWD = `subworkers/<agent>/workspace/` (created on demand); `PROMPT.md` read from the agent home (parent), mirroring the opencode layout |
| TUI renders tool cards from live events | We normalize events to `{text,reasoning,tool}` frames + bare tool names with `input`/`output`, which is what EliaTopBar's livestream, subagents panel (`task`/`subtask`/`hub` + synthetic `ses_*` ids), and todo parser consume |
| `bun check`, `tsc` via tsgo, oxlint/oxfmt | Unchanged — still the gates. Never `tsc` directly |

## 3. Build- and pack-time additions (no source impact)

- `omp-server/packages/natives/native/pi_natives.linux-arm64.node` — fetched
  from the published `@oh-my-pi/pi-natives-linux-arm64@18.2.6` tarball
  (gitignored via `**/*.node`, with a `.dockerignore` exception so it reaches
  image builds; Darwin `.node` resolves from the Bun cache for local runs).
- `omp-server/packages/coding-agent/src/export/html/tool-views.generated.js` —
  one-line stub (HTML-export asset only; real file is generated at pack time
  by `gen:tool-views`). Unblocks source-mode boot; never executed here.
- `omp-server/Dockerfile` (+ `.dockerignore` shadow) — Bun-slim multi-stage
  image: SDK workspace closure only (docs/crates/bench/test dirs excluded),
  ffmpeg + Node 22 for agent MCPs, `HEALTHCHECK :5677/health`.
- `omp-server/docker-compose.yml` — `5677:5677`, `mem_limit: 4g`,
  `HOST: 0.0.0.0` in-container, bind-mounts (data, config, agent workspaces,
  `~/.omp/agent`, MCP config + `mcp-cli`, proxy pool inputs), `cloudflared`
  on the opt-in `tunnel` profile, no `docker.sock` ever.
- Root lifecycle scripts — `install.sh`, `start.sh` (`--docker`,
  `--with-tunnel`, never disturbs a healthy server), `stop.sh`
  (`--with-colima`), `reset.sh` (`--up`, `--no-build`, preserves token +
  configs + domain binding).

## 4. Deliberately NOT changed

- No model/provider policy (still KDL in `packages/catalog`, `gen:compat` flow).
- No prompt wording, no TUI code, no Rust crates, no CLI flags.
- No `team_*` opencode-isms: omp-native `task`/`subtask`/`hub`/`todo` are the
  coordination surface; agent prompts were rewritten from opencode (`team_*`)
  to omp tools.
- Live FastAPI `:5656` system is read-only reference; TopBar remains the
  client of record on any shape ambiguity.

## 5. Docs map

- `omp-server/SERVER.md` — usage, scripts, route table, TopBar contract.
- `omp-server/docs/SUBWORKERS_SYSTEM.md` — the subworker system on this stack.
- `omp-server/docs/elia-optimization-plan.md` — 10-way plan: caches, CPU/RAM,
  crash-proofing, TopBar parity gaps.
- `AGENTS.md` — repo guidelines (root).
