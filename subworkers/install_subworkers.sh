#!/usr/bin/env bash
# install_subworkers.sh — one-time installer for the EliaAI subworker system.
# Verifies prerequisites, prepares config, builds the Docker image.
# After this script succeeds, start everything with: ./start_subworkers.sh

set -euo pipefail
IFS=$'\n\t'

ELIA_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_DIR="$ELIA_ROOT/subworkers/server"

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
die()  { echo "[ERROR] $*" >&2; exit 1; }

# ── 1. macOS + Homebrew ──────────────────────────────────────────────────
[[ "$(uname)" == "Darwin" ]] || log "WARN: non-macOS system — Colima steps will be skipped"
command -v brew >/dev/null 2>&1 || log "WARN: Homebrew not found — install from https://brew.sh if you need Colima/Docker"

# ── 2. OpenCode CLI ──────────────────────────────────────────────────────
command -v opencode >/dev/null 2>&1 \
    || die "opencode not found in PATH — install it first (https://opencode.ai)"

# ── 3. Colima + docker CLI ───────────────────────────────────────────────
if [[ "$(uname)" == "Darwin" ]]; then
    command -v colima >/dev/null 2>&1 || { log "Installing colima..."; brew install colima; }
    command -v docker >/dev/null 2>&1 || { log "Installing docker CLI..."; brew install docker; }
    if ! docker info >/dev/null 2>&1; then
        log "Starting Colima (4 GB RAM is enough for thousands of sessions)..."
        colima start --runtime docker --cpu 2 --memory 4 || die "Colima failed to start"
    fi
fi
docker info >/dev/null 2>&1 || die "Docker daemon not reachable"

# ── 4. Server .env with auth token ───────────────────────────────────────
ENV_FILE="$SERVER_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    TOKEN="$(openssl rand -hex 32)"
    printf 'ELIA_AUTH_TOKEN=%s\n' "$TOKEN" > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    log "Created $ENV_FILE with a fresh auth token."
    log "Put the same token in your clients (EliaTopBar → UserDefaults eliaAuthToken)."
else
    log ".env already exists — keeping it."
fi

# ── 5. Build the container image ─────────────────────────────────────────
log "Building subworker server image..."
(cd "$SERVER_DIR" && docker-compose build)

# ── 6. Done ──────────────────────────────────────────────────────────────
log "Install complete."
echo ""
echo "Next steps:"
echo "  1. Edit $ELIA_ROOT/subworkers/server/app/config/subworkers.json"
echo "     (one entry per agent: name, schedule hours/minute/days, agent_id)"
echo "  2. Start the stack:  $ELIA_ROOT/subworkers/start_subworkers.sh"
echo "  3. Health check:     curl http://localhost:5656/health"
