# subworkers-omp — Elia subworker server on the **omp** harness

A drop-in alternative harness for the Elia subworker fleet. Same 25-agent
registry shape, same TopBar HTTP/WebSocket contract as the reference server —
different engine underneath: **Bun + TypeScript on the
[omp](https://github.com/can1357/oh-my-pi) SDK**, zero Python.

Point EliaTopBar at `http://127.0.0.1:5677` and the fleet runs there. The
reference server keeps running on `:5655`/`:5656` — the two never collide.

---

## What is and is not in this repo

This directory ships the **Elia wrapper layer only**. The agent runtime is
upstream omp, MIT licensed, ~180MB, and is **not committed here**:

- `omp-server/packages/`, `omp-server/crates/`, `omp-server/assets/` — upstream omp
- `omp-server/server.ts`, `engine.ts`, `worker.ts`, `scheduler.ts`, `watchdog.ts`,
  `admit.ts`, `store.ts`, `auth.ts`, `ws.ts`, `tunnel.ts`, `notifier.ts`,
  `statusView.ts`, `models.ts`, `testFrames.ts`, `contractCheck.ts` — **Elia wrapper**
- `omp-server/routes/`, `omp-server/extensions/proxy-local.ts`,
  `omp-server/config/`, `omp-server/Dockerfile`, `omp-server/docker-compose.yml` — **Elia wrapper**

`./install.sh` fetches upstream omp at the pinned ref on first run. Pass
`--skip-upstream` if you already have the checkout. **Never edit
`omp-server/packages` or `omp-server/crates`** — only the wrapper files.

## Quickstart

```bash
./install.sh                # fetch omp + bun install + mint token + build image
# edit omp-server/config/subworkers.json
# create ~/.omp/agent/models.yml  (provider `zen-free`)
# create ~/.omp/agent/agents/<name>.md personas
./start.sh --docker         # or ./start.sh for host mode
curl -s http://127.0.0.1:5677/health
./stop.sh                   # ./reset.sh wipes data/ and config/
```

## Layout

```
subworkers-omp/
├── install.sh / start.sh / stop.sh / reset.sh   lifecycle, health-gated
├── AGENTS.md        repo guidelines + the model/pitfall rules
├── OMP_CHANGES.md   every local delta vs the reference server
├── omp-server/
│   ├── server.ts        HTTP + /ws entry, Bearer gate, router
│   ├── auth.ts          Bearer / X-Elia-Token / ?token=; /health exempt
│   ├── admit.ts         run registry, fsync BEFORE responding, cap -> 202 queued_429
│   ├── engine.ts        sole omp dependency, frame mapping, creation mutex, pre-warm
│   ├── worker.ts        one run: persona + prompt -> frames -> completion
│   ├── scheduler.ts     interval / every / clock-aligned / cron
│   ├── watchdog.ts      STALL_TIMEOUT_S + MAX_RUN_S -> failed + error banner
│   ├── store.ts         data/runs.json + data/frames/<session>.jsonl
│   ├── tunnel.ts        Cloudflare tunnel setup + token file (socketless)
│   ├── routes/          status, sessions, serverRoutes, misc
│   ├── extensions/proxy-local.ts   in-process residential forward, LRU rotation
│   └── config/          subworkers.json, server.json, tunnel.json(.example)
├── examples/agents/   persona template
└── .env.example       every env var the server reads
```

## Port map (no overlap with the reference server)

- `5677` — this server (loopback-published)
- `:3128` / `:3129` — unused here; the `proxy-local` extension runs **in-process**,
  no forwarding daemon and no extra container
- reference server: `5655` + `5656` — untouched

## TopBar contract

Mirrored path-for-path from the reference server:

`/health`, `/server/health` (`health_status` is the literal `"healthy"`),
`/status` (+ `/{name}`; each item carries a boolean `running`), `/trigger`,
`/enable`, `/disable`, `PUT /status/{name}`, `/config/reload`, `/logs`,
`/sessions` (+ `/list`, `/{id}/continue`, `/{id}/events`), `/models`, `/restart`,
`/cleanup`, `/tunnel/*`, `/main-agent` ×2, `/ws`, `POST /test/frames/{name}`.

WebSocket events: `initial_status`, `status_update`,
`subworker_started/completed/success/cancelled/error`, `run_log` (+ `field`),
`run_banner`, `pong`, `models_version`. `running` comes from the **run registry**,
never from the schedule. An abrupt SSE close is a clean EOF, never a 500.

`EliaTopBar`'s `SubworkerManager.swift` is the client of record — when a route
shape is ambiguous, that file wins.

## Run lifecycle

`POST /trigger` → `admitRun()` fsyncs the run record, then `startEngine()` creates
an `AgentSession` → `session.subscribe` maps SDK events to `text|reasoning|tool`
frames → broadcast on `/ws` **and** appended to `data/frames/<id>.jsonl` →
`completed`. Over the concurrency cap: HTTP `202` with `{"status":"queued_429"}`.

## Models and auth

- Agents run on **`zen-free/*`** — the custom provider you define in
  `~/.omp/agent/models.yml`. `opencode-zen/*` needs an `OPENCODE_API_KEY` that
  this setup does not have, so any entry using it fails instantly.
- `subworkers.json` may only reference `zen-free/*` ids that exist in your
  `models.yml`. An unknown id silently falls back to the default provider model —
  check `data/frames/<session>.jsonl` first when a turn completes in seconds with
  zero frames.
- `entry.model` reaches the engine as `modelPattern`, never as a prompt option.
- Personas: `~/.omp/agent/agents/<name>.md`, frontmatter stripped, 12k cap, fed
  via `appendSystemPrompt`. Mounted `:rw`, so a persona edit is live on the next
  run with no rebuild.
- Skills: `../.omp/skills/` at the repo root, visible to every subworker. Host
  globals are shadowed in Docker by a tmpfs so agents stay lean.

## Proxy

`omp-server/extensions/proxy-local.ts` is the **only** proxy path — vendored
locally, loaded exclusively per worker. In-process residential forward with
native upstream rotation: no shell scripts, no forwarding daemon, no extra
container. Pool lives in `omp-server/extensions/proxies.txt`
(`host:port:user:pass |last:<ts>`; oldest-unused wins, forced 4-minute swap).
Model traffic is proxied; agent tool shells stay direct. Log:
`omp-server/data/proxy-local.log`. An empty pool is not fatal — it fails open.

## Secrets

`omp-server/.env` (token, chmod 600), `config/tunnel.json`, `config/tunnel.token`,
`extensions/proxies.txt`, `data/` are all gitignored. Copy the `.example` files
and fill them locally. Never commit a filled one.

## Verify

```bash
curl -s http://127.0.0.1:5677/health
curl -s -H "Authorization: Bearer $ELIA_AUTH_TOKEN" http://127.0.0.1:5677/status | jq .
curl -s -X POST -H "Authorization: Bearer $ELIA_AUTH_TOKEN" \
  http://127.0.0.1:5677/trigger/<name>          # <100ms, returns session_id
ELIA_AUTH_TOKEN=... bun omp-server/testFrames.ts <name>   # synthetic text/reasoning/tool
curl -s "http://127.0.0.1:5677/sessions/<name>?limit=5"
curl -sN "http://127.0.0.1:5677/sessions/<name>/<id>/events"   # clean EOF on disconnect
```

Docs: [`omp-server/SERVER.md`](omp-server/SERVER.md) ·
[`AGENTS.md`](AGENTS.md) ·
[`omp-server/docs/SUBWORKERS_SYSTEM.md`](omp-server/docs/SUBWORKERS_SYSTEM.md) ·
[`omp-server/docs/HOWTOADDAGENTS.md`](omp-server/docs/HOWTOADDAGENTS.md)

## License

Wrapper layer: MIT (see [LICENSE](LICENSE)). Vendored omp: MIT,
© 2025 Mario Zechner, © 2025-2026 Can Bölük, © 2026 Stencil Labs, Inc.