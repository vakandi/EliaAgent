# Repository Guidelines

Fork of `oh-my-pi` at ref `78b7531`, no upstream remote — never fetch/pull. `packages/coding-agent/` is the primary focus. When the user says "agent", they mean the coding-agent CLI implementation, not the assistant session.

## Project Overview

oh-my-pi (`omp`) is a Bun-native multi-package monorepo: an agentic coding CLI with session/SDK runtime, terminal UI library, multi-provider LLM client, model catalog with KDL-compiled policy, Rust N-API natives, and supporting services. This fork adds an `omp-server/` wrapper entrypoint: a Bun (TypeScript, zero Python) server re-implementing the live FastAPI subworker spec (`~/EliaAI/subworkers/server/`, port 5656) on omp primitives (`createAgentSession`), listening on HTTP `5677`. Live `app/` is read-only reference — never imported. Done means EliaTopBar on `:5677` shows counts, triggers stream text+reasoning+tools live, stalls surface within 5 min.

## Architecture & Data Flow

- **Agent runtime**: `createAgentSession({cwd, agentDir, eventBus})` (`packages/coding-agent/src/sdk.ts:1330`) builds an `AgentSession` (`src/session/agent-session.ts:566`) with `prompt(text, opts)` (`:6298`), `subscribe(listener)` (`:4446`, returns unsub), `waitForIdle()` (`:5321`), `dispose()` (`:4705`). Session events (`src/session/agent-session-events.ts`) extend core `AgentEvent`.
- **omp-server/ request flow**: HTTP/WS → Bearer gate (`omp-server/auth.ts`) → `admitRun()` (`omp-server/admit.ts`, fsyncs run record to `omp-server/data/runs.json` BEFORE responding; over cap → HTTP 202 `queued_429`) → `startEngine()` (`omp-server/engine.ts`, lazy dynamic import so boot never needs the native addon) → `session.subscribe` maps SDK events to `text|reasoning|tool` frames → broadcast to `/ws` AND append to `omp-server/data/frames/<sessionId>.jsonl`.
- **SDK creation is serialized**: `creationGate` mutex in `omp-server/engine.ts` — concurrent `createAgentSession` calls abort each other ("Agent Main was replaced during session initialization"). Prompts/turns stay parallel post-creation.
- **Bun ≤1.3.x quirk**: `require()` of modules using `with { type: "text" }` drops the attribute → pre-warm via static side-effect imports (`omp-server/engine.ts`). Prefer Bun ≥1.4.
- **Scheduler**: interval / clock-aligned every / cron (`omp-server/scheduler.ts`), persists `next_run` in `omp-server/data/state.json`. **Watchdog** (`omp-server/watchdog.ts`): `STALL_TIMEOUT_S` (300) / `MAX_RUN_S` (3600) → mark failed + error banner + Discord; no RSS-cap gate anywhere (container `mem_limit` is the only guard). **Proxy**: oldest-used LRU per session + forced 4-min rotation, no quarantine (`omp-server/proxy.ts`). **Tunnel**: socketless, token file only (`omp-server/config/tunnel.token`, chmod 600) + `omp-server/tunnelWatch.sh` sidecar; never mount `docker.sock`.
- **TopBar is the client of record**: on shape ambiguity, `SubworkerManager.swift` wins. WS events: `initial_status`, `status_update`, `subworker_started/completed/success/cancelled/error`, `run_log` (+`field`), `run_banner`, `pong`. `running` comes from the run registry, never the schedule. `health_status` must be the literal `"healthy"`.

## Models & Auth (read before debugging agent runs)

- **Agents run on `zen-free/*`, never `opencode-zen/*`.** `zen-free` is a custom provider defined in `~/.omp/agent/models.yml` (baseUrl = local proxy-local on `127.0.0.1:18898` → residential egress to `https://opencode.ai`, keyless). `opencode-zen/*` instead needs `OPENCODE_API_KEY`, which exists nowhere in this setup — any run configured with it fails instantly. `omp-server/config/subworkers.json` must only reference `zen-free/*` ids present in `models.yml` (muse-spark-1.3/1.2, deepseek-v4-flash-free, mimo-v2.5-free, ling-3.0-flash-fin-free, nemotron-3-ultra/3.5-lightning, jev-1.13, big-pickle).
- **Model string goes via `modelPattern`, never prompt opts.** `worker.ts` passes the entry model as `modelPattern` in `createAgentSession` — the CLI-blessed deferred path, because extension-provided models (models.yml) register after extensions load. `AgentPromptOptions` has NO `model` field; anything passed there is silently ignored and the turn falls back to the default provider model (`openai/gpt-5.5` via OpenRouter, whose key is dead → instant empty turn). If you see `provider=openrouter model=openai/gpt-5.5` in SDK logs, the requested model never resolved — start here.
- **EliaTopBar changes models via the wrapper API.** `SubworkerManager.setModel` → `PUT {baseURL}/status/{name}` on `:5677` (`routes/status.ts`, allowlist: `agent_id, model, variant, timeout_minutes, max_retries, schedule`). Model/version snapshot also flows over `/ws` (`models_version`).
- **MCP sources, in priority order:** project `.omp/mcp.json` (subworkers running from this checkout) → user `~/.omp/agent/mcp.json` (personal OMP AND docker OMP via the `:rw` compose mount — one file, both systems). Verify inside with `omp-server/scripts/check-*-docker.sh` before claiming a server is missing — see **MCPs & Skills** below for what that does and does not prove.
- **Skills, in priority order:** repo `.omp/skills/` (project level — every subworker sees all of them, wins on name collision). Host globals (`~/.omp/agent/skills`) apply to local runs only — shadowed in Docker via tmpfs so agents stay lean. Docker: repo skills arrive through the `../.omp/skills:/srv/omp-server/subworkers/.omp/skills:ro` mount (SDK ancestor scan from `subworkers/<name>/workspace`). Add one: `<name>/SKILL.md` with `name` + `description` frontmatter — live on the next run, no rebuild/restart.- **Empty turn triage (run `completed` in seconds, zero frames):** 1) `data/frames/<session>.jsonl` — prompts only? 2) fresh `/root/.omp/logs/omp.*.log` inside the container — which `provider/model` did the turn actually use? 3) if `openrouter/openai/gpt-5.5` → model resolution failed (check entry model id + `modelPattern` wiring). Never blame provider keys without this chain.

## MCPs & Skills — verifying and adding them

**Every MCP that an agent uses must have a readiness script at `omp-server/scripts/check-<short>-docker.sh`.** Run it from the omp-server checkout (`omp-server/scripts/...`) — each script self-locates `../docker-compose.yml` and hard-exits 2 if copied elsewhere, because a check run against the wrong compose file proves nothing. Naming drops the `mcp-server-` prefix and may shorten: `mcp-server-linkedin` → `check-linkedin-docker.sh`, `hasdata-indeed` → `check-indeed-docker.sh`. Existing: `check-linkedin-docker.sh`, `check-indeed-docker.sh`.

What a check script asserts, in order: container up → server key present in `/root/.omp/agent/mcp.json` → runtime present (`uvx`, node, python) → auth material present (session/cookies/API key, with placeholders like `REPLACE_WITH` treated as NOT READY) → live probe where the transport allows one. Exit 0 = READY, 1 = NOT READY.

- **`READY` is necessary, NOT sufficient.** A green script only proves the server *starts*; it does not prove a tool *works*. Real failure on 2026-09-26: `check-linkedin-docker.sh` printed `READY` while **every** tool returned `Patchright Chromium browser is missing` (container inherited the host's macOS `chrome-mac-arm64`), and later `No valid LinkedIn session is available in Docker` while the profile dir was non-empty. **A check script MUST end with a live read-only tool call** and exit non-zero when it fails — `check-linkedin-docker.sh` now does this (embedded stdio probe on `get_my_profile`, read-only, safe against a real account); copy that pattern. Two traps when writing one: MCP stdio is **newline-delimited JSON, NOT LSP `Content-Length` framing**, and you must **sequence** `initialize` → wait for its result → `notifications/initialized` → `tools/call`. Fire them all at once and the server answers only the handshake, which reads as a hang.
- **Native vs `mcp-cli` are different registries.** Servers in `~/.omp/agent/mcp.json` load as integrated tools `mcp__<server>_<tool>` for the agent; `mcp-cli` reads `~/.config/mcp/mcp_servers.json` and will legitimately NOT list them. Absence from `mcp-cli list` is not a missing server. Never call a native tool through `mcp-cli`.

**Adding an MCP:** (1) register it in `~/.omp/agent/mcp.json` — user-level, mounted `:rw`, so one file serves local and docker; (2) add its interpreter/runtime deps to `omp-server/Dockerfile`, never a runtime install (`/root/.local` and `/opt` are not volumes, so recreates wipe them — this is how `fastmcp` and the Linux Chromium died); (3) add any bind-mount, and choose the mode deliberately — code/secrets `:ro`, but state the tool refreshes **in place** (OAuth tokens) must be `:rw` or it breaks at first expiry with no way to re-auth headlessly; (4) give it a browser/runtime its own platform build when the host mount is a different OS; (5) add `check-<short>-docker.sh`; (6) verify with the script **and** a real read-only call.

**Adding a skill:** `.omp/skills/<name>/SKILL.md` with `name` + `description` frontmatter (multi-line `description: |` is fine) — live on the next run, no rebuild or restart. Docker sees it at `/srv/omp-server/subworkers/.omp/skills/<name>/` via the `../.omp/skills:...:ro` mount; the SDK ancestor-scans from `subworkers/<name>/workspace`. Agents read it as `read skill://<name>`. Exclude `.git` when vendoring an upstream skill (a nested repo breaks the parent repo's git). Reference the skill by `skill://` name in `PROMPT.md`/persona so the model actually loads it.

## Key Directories

| Path | Purpose |
|---|---|
| `packages/coding-agent/` | Main CLI + SDK (`@oh-my-pi/pi-coding-agent`); primary focus |
| `packages/ai/` | Multi-provider LLM client, streaming (`@oh-my-pi/pi-ai`) |
| `packages/catalog/` | Model catalog, descriptors, KDL policy tree (`@oh-my-pi/pi-catalog`) |
| `packages/agent/` | Agent runtime, tool calling, state (`@oh-my-pi/pi-agent-core`) |
| `packages/tui/` | Terminal UI, differential rendering (`@oh-my-pi/pi-tui`) |
| `packages/natives/` | Rust N-API bindings: grep/PTY/shell/clipboard/image (`@oh-my-pi/pi-natives`) |
| `packages/utils/` | Shared logger/streams/temp/vcs helpers (`@oh-my-pi/pi-utils`) |
| `packages/stats/` | Local observability dashboard (`omp stats`) |
| `packages/omptype/` | ArkType-compatible schema validation, lazy JIT |
| `packages/wire/` | Shared wire-protocol types |
| `packages/mnemopi/` | Local SQLite memory engine |
| `packages/snapcompact/` | Bitmap-frame context compression for vision LLMs |
| `packages/collab-web/`, `browser-relay/`, `metaharness/` | Private: collab web client, Chrome relay ext, benchmark harness |
| `crates/pi-natives/` | Rust crate for performance-critical text/grep ops |
| `omp-server/` (wrapper files) | Wrapper server: `server.ts` entry, `routes/`, `engine.ts`, `store.ts`, `scheduler.ts`, `watchdog.ts`, `notifier.ts`, `proxy.ts`, `tunnel.ts`, `admit.ts`, `statusView.ts`, `auth.ts`, `ws.ts`, `testFrames.ts`, `Dockerfile`, `docker-compose.yml`, `config/` (upstream `packages/` etc. live alongside) |
| `omp-server/data/` | Runtime state (gitignored): `runs.json`, `frames/*.jsonl`, `state.json`, `main-agent.json`, `proxy-map.json` |
| `.omp/skills/` | Repo skills, visible to every subworker (local + docker) — add `<name>/SKILL.md`, live next run |
| `scripts/` | Release, merge, CI chunking, version sync, cleanup-scan |
| `docs/` (~85 files) | `providers.md`, `auth-broker-gateway.md`, `sdk.md`, `rpc.md`, `tui.md`, `cli-reference.md` |
| `python/robomp/`, `python/omp-rpc/` | Python workspaces (tests via pytest, not bun) |

## Development Commands

Cwd is repo root unless noted. Never run project-wide suites mid-edit; run focused checks for the changed area.

```bash
bun install                    # workspace deps (root)
bun check                      # TS gate: oxlint + oxfmt + per-package check:types (NEVER tsc/npx tsc)
bun run test:rs                # Rust: cargo nextest + doctest pass (NEVER bare cargo test)
bun test <path>                # focused TS tests, e.g. bun test packages/ai/test/tokens.test.ts
bun run gen:compat              # recompile KDL rules → packages/catalog/src/compat/rules.json (commit both)
bun run gen:models              # regen packages/catalog/src/models.json (commit both)
bun run release                 # version bump + changelog finalize + tag + publish
omp --smoke-test               # worker smoke probe (wired into ci:test:smoke)
ELIA_AUTH_TOKEN=... bun omp-server/server.ts            # boot wrapper on 127.0.0.1:5677
curl -s http://127.0.0.1:5677/health              # open healthcheck
curl -s -H "Authorization: Bearer $T" http://127.0.0.1:5677/status | jq .
ELIA_AUTH_TOKEN=... bun omp-server/testFrames.ts [name] # synthetic text/reasoning/tool gate (no engine)
docker build -f omp-server/Dockerfile -t omp-server .   # image (linux .node packs via bazel-natives host step)
```

- **Git**: NEVER commit/push unless asked. Merge commits: `Merge PR #<number>: <conventional subject> (@<author>)`.
- **GitHub**: posting a comment/issue or creating one needs explicit user confirmation (an instruction to post supplied text counts). Read-only checks need none. Never resolve review threads without an approved factual reply posted first. Keep PR template sections (`What/Why/Testing`); every PR needs one human-written what+why sentence — never generate a substitute.
- **omp-server/ wrapper has no test framework** (zero `*.test.ts`): verify via boot → curl gates → synthetic frames → TopBar on `:5677`.

## Code Conventions & Common Patterns

- **Types**: no `any` unless necessary; NEVER `ReturnType<>` (name the type); NEVER inline imports (`await import()`, `import("pkg").Type`) — top-level only. Exception: elia lazy-loads `engine.ts` via `import()` so boot survives without the native addon (commented at each site).
- **Style**: ES `#private` fields (no `private` keyword except constructor param properties); `Promise.withResolvers()` over `new Promise`; barrels are `export * from "./module"` even for single/type-only specifiers; `node:*` always namespaced (`import * as fs from "node:fs/promises"`; async-only file → `node:fs/promises`).
- **Bun over Node**: `Bun.file()/Bun.write()`, `` $`cmd` `` with `.quiet().nothrow().cwd()`, `Bun.sleep/sleep`, `Bun.stringWidth/wrapAnsi`, `bun:sqlite`, `Bun.JSON5/JSONL`, `$which()` from `@oh-my-pi/pi-utils`, `import.meta.dir/path`. Never shell out for what an API covers. Check central utils first (`packages/coding-agent/src/utils/`, `@oh-my-pi/pi-utils`, `@oh-my-pi/pi-tui`); duplicate helpers are bugs. Git/jj only via `@oh-my-pi/pi-natives/vcs`.
- **Prompts**: never built in code — static `.md` + Handlebars, `import content from "./prompt.md" with { type: "text" }`.
- **Logging**: `import { logger } from "@oh-my-pi/pi-utils"` → `~/.omp/logs/omp.YYYY-MM-DD.log` (rotated). Anything that may run under TUI/RPC/SDK/workers MUST NOT `console.*`; only standalone exiting CLI commands may print user-facing output.
- **TUI text**: sanitize every render path via `replaceTabs()`, `truncateToWidth()`/`TRUNCATE_LENGTHS`, `shortenPath()`, `PREVIEW_LIMITS` — including error strings and diffs.
- **Model/provider policy lives in KDL** (`packages/catalog/src/compat/rules/`: `taxonomy/` identity, `classes/` lineage, `providers/` host contracts, `runtime/behavior.kdl` heuristics). NEVER branch on model names in TS — only on `classifyModel()` facts. Fix overlap with KDL `priority=`, then `bun run gen:compat` + commit `rules.json`.
- **Layering** (FastAPI-style services if added): routers → services → repositories; services raise domain errors, routers map to HTTP; no `print()`, typed signatures, `async def` routes.
- **elia deltas**: `field ∈ text|reasoning|tool` fixed; remap inside `omp-server/engine.ts` if SDK names drift. Tool frames carry name+status only, never payloads.

## Important Files

- `packages/coding-agent/src/cli.ts` — CLI entry, command registry, `--smoke-test` (`runSmokeTest`, :134-174)
- `packages/coding-agent/src/sdk.ts` — `createAgentSession` (:1330), options (:377-433), `CreateAgentSessionResult` (:679)
- `packages/coding-agent/src/session/agent-session.ts` — `AgentSession` (:566); `prompt` (:6298), `subscribe` (:4446), `waitForIdle` (:5321), `dispose` (:4705)
- `packages/coding-agent/src/session/agent-session-events.ts` — `AgentSessionEvent` union
- `packages/coding-agent/src/utils/event-bus.ts` — `EventBus` (isolated instance per engine run)
- `packages/catalog/src/compat/rules/` + `rules.json` — model policy (see above)
- `packages/catalog/src/models.json` + `src/provider-models/descriptors.ts` — generated bundle + its source
- `omp-server/server.ts` — serve entry, auth gate, router, `/ws` (HOST env bind, default 127.0.0.1)
- `omp-server/config/subworkers.json` — 25-entry registry (verbatim live copy); `omp-server/config/server.json` — `{port:5677, concurrency:8}`
- `omp-server/engine.ts` — sole omp dependency + frame mapping + creation mutex + pre-warm
- `bunfig.toml` — telemetry off, hoisted/exact installs, `[test]` ignore list, `.md/.py/.lark=text` loader
- `rust-toolchain.toml` (nightly-2026-08-12) + root `Cargo.toml` profiles (dev/release/local/profiling/ci)
- `packages/*/CHANGELOG.md` — `## [Unreleased]` sections (Breaking/Added/Changed/Fixed/Removed); released sections immutable
- `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `packages/coding-agent/DEVELOPMENT.md`

## Runtime/Tooling Preferences

- **Runtime**: Bun (`packageManager bun@>=1.4`, engines `>=1.3.14`; lockfile `bun.lock`, exact installs). Prefer Bun APIs; `node:*` only for gaps. Use `bun check`, never `tsc`.
- **Rust**: nightly toolchain per `rust-toolchain.toml`; test via `bun run test:rs` (nextest config `.config/nextest.toml`).
- **Python**: pytest only under `python/` (`test:py`); zero Python in the elia hot path.
- **Docker**: `omp-server/Dockerfile` (Bun slim, `HEALTHCHECK` on `:5677/health`), `omp-server/docker-compose.yml` (`mem_limit: 2g`, `5677:5677`, bind-mounts for data/config/workspaces/auth/proxies, NO `docker.sock`; `HOST: 0.0.0.0` in-container).
- **elia env**: `ELIA_AUTH_TOKEN` (empty = auth off), `MAX_CONCURRENT_RUNS` (8, cap 100 → HTTP 202 `queued_429`), `STALL_TIMEOUT_S` (300), `MAX_RUN_S` (3600), `DISCORD_WEBHOOK_URL` (300s debounce, never logged), `HOST`, `OMP_AGENT_DIR`.
- **Native addon**: `packages/natives/native/*.node` is gitignored; darwin prebuilt resolvable from bun cache for local runs; linux packs via `bun scripts/bazel-natives.ts host --dest packages/natives/native` (host path needs no bazel).
- **Generated, never hand-edit**: `packages/catalog/src/models.json`, `packages/catalog/src/compat/rules.json` (+`provider-ids.ts`/`auth-ids.ts`), `packages/coding-agent/src/export/html/tool-views.generated.js`.

## Testing & QA

- **Philosophy** (repo rule): every test defends one externally observable contract — name the failure mode or don't add it. Good: transformations, branches/boundaries, exact wire bytes downstream parses, precedence/negative contracts, true regression repros (`issue-<N>-repro.test.ts`). Bad: static echo, `fn(x)===x` passthrough, prompt wording/defaults, duplicate param rows, source-grep tests (asserting on `.ts` text is banned — use runtime probes/type tests/oxlint rules). No placeholder/tautology/bare-`not.toThrow` tests. Tests must be full-suite safe (per-test `vi.spyOn` + `afterEach restoreAllMocks`; `mock.module()` banned — registry leak). One invariant per stateful test; trigger real failure paths for errors.
- **Layout**: `packages/*/test/*.test.ts` (+`test/core/`, `test/tools/`), fixtures in `packages/*/test/fixtures/`. Async: plain `async` describe/it; e2e gated by `skipIf(!token)`. No global setup files.
- **Commands**: `bun test <path>` (focused); `bun run test:rs`; `test:py` for `python/`; `omp --smoke-test` for worker wiring (also `scripts/install-tests/run-ci.sh` across binary/source/tarball installs).
- **elia verification** (no framework): boot → `curl /health` → authed `/status` → `POST /trigger/{name}` (<100ms + `session_id`) → `POST /test/frames/{name}` → TopBar run popup shows text/reasoning/tool → `GET /sessions/{name}?limit=` + SSE `/sessions/{name}/{id}/events` (clean EOF on disconnect). Soak: 15-burst expects ~8×200 + ~7×202 `queued_429`, RSS flat.
- **Before "done"**: run the focused check covering the change; exact-bytes assertions only when a consumer parses them; exact strings never for prompts/UI boilerplate.
