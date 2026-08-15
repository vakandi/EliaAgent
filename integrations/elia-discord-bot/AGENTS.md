# AGENTS.md — elia-discord-bot

**Generated:** 2026-07-11
**Commit:** 721c5a0
**Branch:** main

## OVERVIEW

Python 3.11+ Discord bot bridging Discord servers to EliaAI's OpenCode backend. Uses discord.py + httpx async. Small codebase: 8 modules, ~460 LOC.

## STRUCTURE

```
elia-discord-bot/
├── main.py                  # Entry point — asyncio.run(main())
├── pyproject.toml           # Deps, ruff, pytest config
├── Dockerfile               # Multi-stage python:3.11-slim
├── docker-compose.yml       # Service + healthcheck
├── .env.example             # Required env vars
├── src/
│   ├── bot.py               # Discord client, slash cmds, on_message
│   ├── config.py            # Pydantic Settings (env vars)
│   ├── opencode_client.py   # Async httpx wrapper for OpenCode API
│   ├── session_manager.py   # Guild→session mapping, create/reset
│   ├── message_handler.py   # Prompt formatting + mcp-cli injection
│   ├── context_tracker.py   # Per-channel TTL message history
│   └── logging_config.py    # structlog + rotating file handler
└── logs/                    # Runtime logs (bot.log)
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Add Discord command | `src/bot.py` → `_register_commands()` | Slash cmds defined via `@self.tree.command` |
| Change OpenCode API call | `src/opencode_client.py` | All HTTP via httpx.AsyncClient |
| Modify message format | `src/message_handler.py` | Includes mcp-cli tool hints |
| Change session logic | `src/session_manager.py` | In-memory dict, guild-scoped |
| Add env var | `src/config.py` → `Settings` | Pydantic Field with description |
| Change context behavior | `src/context_tracker.py` | deque-based, TTL eviction |
| Deployment config | `Dockerfile`, `docker-compose.yml` | Multi-stage build |

## ARCHITECTURE

```
main.py → EliaDiscordBot(settings)
  ├── OpenCodeClient(base_url, api_key)     # HTTP layer
  ├── SessionManager(client)                # Guild→session mapping
  ├── ContextTracker(max_history)           # Channel TTL history
  └── asyncio.Semaphore(3)                  # Concurrency control
```

**Data flow:** Discord message → format with context + metadata → OpenCode API → response → Discord reply (chunked at 1900 chars)

## CONVENTIONS

- **Async-first**: ALL I/O is async. httpx.AsyncClient, discord.py async, no synchronous HTTP ever.
- **structlog**: `log = structlog.get_logger()` at module top. Keys: `dot.separated` (`bot.starting`, `message.received`).
- **Semaphore wraps OpenCode calls**: Every `session_manager.send_message()` call acquires `self.semaphore` first.
- **Pydantic Settings**: Single `Settings` class, `.env` file, `Field(...)` with descriptions.
- **Ruff only**: line-length 100, target py311, rules: E/F/I/N/W/UP.
- **pytest asyncio_mode = "auto"**: No `@pytest.mark.asyncio` needed.

## ANTI-PATTERNS

- **NEVER** use `requests` or synchronous HTTP — always `httpx.AsyncClient`
- **NEVER** make OpenCode API calls outside the semaphore
- **NEVER** store secrets in code — use `.env` + `Settings`
- **NEVER** suppress exceptions with bare `except:` — use specific types
- **NEVER** modify `src/bot.py` without testing Discord interaction/message flows end-to-end

## COMMANDS

```bash
# Run locally
python main.py

# Lint
ruff check src/ main.py

# Format
ruff format src/ main.py

# Test (no tests exist yet — add tests/ directory)
pytest

# Docker
docker compose up --build
```

## GOTCHAS

- **Missing `__init__.py`** in `src/` — relies on implicit namespace packages. Some tools may break.
- **No tests** — pytest configured but zero test files. `tests/` directory needs creation.
- **Health check gap** — Dockerfile exposes :8080, docker-compose checks `/health`, but no HTTP server exists. Healthcheck always fails.
- **ContextTracker TTL bug** — TTL check runs AFTER timestamp is updated, so it never triggers. See `context_tracker.py:20`.
- **In-memory sessions** — `SessionManager.active_sessions` dict lost on restart.
- **`DISCORD_ERROR_CHANNEL_ID`** configured but never wired to error handler in bot.
- **Dual response path** — bot replies via `interaction.followup.send` AND instructs OpenCode agent to use `mcp-cli discord_send_message`. Can cause duplicate messages.
