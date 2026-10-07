# subworkers-qwen — Lighter Elia Subworker Stack (Qwen + opencode engine)

Side-by-side replacement for `~/EliaAI/subworkers/` (live :5656/:5655).
Same 25 agents, same TopBar contract — smaller footprint, same auth token.
Live system is NEVER touched: different folder, ports, volumes, containers.

> **Public template.** This copy ships the harness only: `shim/`, `qwen/`,
> `scripts/`, `docs/`, the compose file. The live `workspaces/` (agent prompts,
> memory, run data) and `opencode-share/` (auth + session DB) are **not**
> included — create your own. `workspaces/claims-monitor/` is a worked example,
> and `shim/app/config/subworkers.json` ships with five fictional agent entries so
> the schema is obvious. `proxies.txt.example` documents the egress pool format.
> Everything else below is exactly how the live stack runs.

## Layout

```
subworkers-qwen/
├── README.md               # this file
├── docker-compose.yml      # shim :5676 + qwen :4170 (internal) + cloudflared (tunnel profile)
├── shim/                   # FastAPI, Elia-native routes (port 5676, loopback-only)
│   ├── Dockerfile          # python:3.12-slim + node 20 + opencode binary + procps
│   ├── opencode.json       # baked provider + portable MCPs (context7, duckduckgo, parallel-browser)
│   ├── .env / .env.example # PORT, tokens (placeholders only — never commit secrets)
│   └── app/
│       ├── main.py             # routes incl. tunnel router, /health open
│       ├── config.py           # env settings (STALL_TIMEOUT_S=300, MAX_RUN_S=3600, MAX_CONCURRENT_RUNS=8)
│       ├── auth.py             # Bearer/X-Elia-Token/?token=, /health exempt
│       ├── qwen_client.py      # Qwen daemon REST+SSE client (DORMANT path)
│       ├── opencode_engine.py  # ACTIVE engine: `opencode run --format json` subprocess
│       ├── stream_bridge.py    # SSE → WS run_log translator + counters
│       ├── notifier.py         # Discord webhook
│       └── routers/            # subworkers, server, tunnel, main_agent, websocket
├── qwen/                   # Qwen daemon image (DORMANT engine, kept as sidecar)
│   ├── Dockerfile / .env / entrypoint.sh / forward-proxy.js
│   └── chunk-patches/      # daemon provider-retry patch source
├── workspaces/<agent>/     # PROMPT.md + memory (HANDOFF, daily dirs, GDOC files)
├── scripts/                # backoff-429.sh, cloudflared-watch.sh
├── logs/                   # per-run logs (same shape as live)
└── docs/                   # NOTES.md, SUBWORKERS_SYSTEM.md
```

## Port map (no conflicts with live)

| Service | Address | Notes |
|---|---|---|
| shim HTTP | `127.0.0.1:5676` | TopBar → Change Server URL to this |
| qwen daemon | internal `:4170` | `expose` only — never published (avoids clash with `qwen-case` test container) |
| qwen forward proxy | internal `:3128` | LRU pool + 4-min rotation + `POST /__rotate` ops endpoint |
| qwen attest shim | internal `:3129` | stamps `User-Agent` + `x-opencode-session`, chains into `:3128` |
| host zen gateway | `host.docker.internal:18898` | omp proxy-local extension (residential pool) |
| live (untouched) | `:5655` + `:5656` | zero overlap — verified by grep on every change |

## TopBar contract (base URL is the ONLY client change)

Mirrored path-for-path from live: `/health`, `/server/health`
(`health_status=="healthy"` when ok — TopBar checks that exact string),
`/status` (+`/{name}`, items carry boolean `running` — TopBar parses it as
Bool, missing = permanent "0 agents"), `/trigger`, `/enable`, `/disable`,
`PUT /status/{name}`, `/config/reload`, `/logs`, `/sessions` (+`/list`,
`/{id}/continue`, `/{id}/events`), `/models`, `/restart`, `/cleanup`,
`/tunnel/*`, `/main-agent` ×2, `/ws` (`initial_status` on connect, then
`subworker_started`, `status_update`, `run_log{name,text,field}`,
`run_banner`). Abrupt SSE close = clean EOF, never 500.

## Run lifecycle

Trigger → session minted → engine subprocess (`opencode -m opencode/<agent-model>
--variant <agent-variant>`) → JSON frames → translated → WS `run_log` +
stored for events replay → `completed`. No frames for `STALL_TIMEOUT_S` (300s)
or past `MAX_RUN_S` (3600s) → `failed` + error banner (never eternal running).
429 → rotate egress (`POST qwen:3128/__rotate`) + one retry, then `queued_429`.

## Per-agent models (from live config — engine was defaulting everything to spark)

`entry.model`/`entry.variant` flow trigger → engine → `opencode run -m/-variant`.
E.g. hunters run ling/medium, workspace-digest spark-1.2/xhigh.

## Hard-won rules (do not regress)

1. **No RSS-cap gate.** Deleted `OPENCODE_MAX_RSS_MB`/`QWEN_MAX_RSS_MB`
   everywhere — container `mem_limit` guards (shim 2g after OOM kills).
2. **Never mount host `~/.config/opencode`.** Its plugins poison in-container
   runs (72s Bad Gateway deaths); clean-HOME keyless answers in ~4s.
   Auth copy pattern only (`opencode-share/`), never the live DB.
3. **PROMPT paths are rewritten.** Copies reference `/data/subworkers-qwen/…`,
   never `/Users/…/EliaAI/subworkers/…` (else every read errors and runs go thin).
4. **No `__pycache__` in images.** `.dockerignore` present — stale bytecode
   once haunted a whole evening with phantom tracebacks.
5. **`qwen:`/`shim` hostnames stay in NO_PROXY.** Loopback + compose peers
   never go through a proxy (the hairpin bug: pool egress cannot route back).
6. **Rebuild with `--force-recreate`.** Plain `up -d` silently keeps stale
   containers; verify with md5 host-vs-container after every rebuild.
7. **Secrets never in repo.** `.env` files, `tunnel.token`, state files are
   gitignored; lengths/masked only in reports.

## Ops

```bash
cd ~/EliaAI/subworkers-qwen
docker-compose up -d --force-recreate shim qwen   # apply code/config changes
docker-compose config > /dev/null                 # validate before up
docker logs elia-subworker-qwen-shim | tail -40   # shim trail
docker logs elia-qwen-srv | tail -40              # daemon trail
# TopBar-equivalent trigger (token never printed):
docker exec elia-subworker-qwen-shim sh -c \
 'curl -s -X POST http://localhost:5676/trigger/<agent> -H "Authorization: Bearer $ELIA_AUTH_TOKEN"'
```

## Known upstream wall (2026-09-19/20)

Zen free tier gates non-opencode clients (`FreeTierError` 403) and spark-class
models 500 model-side in waves; rotation spreads per-IP quota but cannot lift
identity/model outages. Mitigations live: 4-min LRU rotation + rotate-on-429 +
5-attempt daemon retry + engine fallback chain. When everything 403/500s at
once, wait for the window — the stack now waits instead of dying.
