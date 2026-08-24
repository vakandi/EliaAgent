# EliaAI Subworker Server

Python FastAPI server for managing EliaAI subworkers. Replaces the launchd-based scheduling system with a centralized JSON-configured, Docker-deployed server.

## Quick Start

```bash
# Local development
cd subworkers/server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# Docker
docker compose up --build
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health check |

More endpoints added in subsequent tasks (status, trigger, enable/disable, logs, server management, WebSocket).

## Configuration

Copy `.env.example` to `.env` and adjust values. JSON configs live in `app/config/`:

- `server.json` — server settings
- `subworkers.json` — all subworker definitions + schedules

## Architecture

```
app/
  main.py           # FastAPI application
  routes/           # HTTP endpoint handlers
  services/         # Business logic (scheduler, runner, health, etc.)
  utils/            # Shared utilities (OpenCode client, etc.)
  config/           # JSON config files + Pydantic models
tests/              # Test suite
```

## Development

```bash
# Run tests
pytest -v

# Lint
ruff check .
ruff format .
```
