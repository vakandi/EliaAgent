#!/usr/bin/env bash
# reset.sh — reset the omp-server Docker stack WITHOUT losing the Cloudflare domain.
#
# Usage:
#   ./reset.sh [--up] [--no-build]
#
#   (no flag)   compose down (incl. tunnel profile) + remove omp-server images
#               + clear runtime data, then rebuild the image.
#   --up        after reset, restart the stack WITH tunnel
#               (equiv. ./start.sh --docker --with-tunnel).
#   --no-build  skip the rebuild (down + clean only).
#
# Preserved (domain keeps working after re-up):
#   omp-server/.env, omp-server/config/subworkers.json, omp-server/config/server.json,
#   omp-server/config/tunnel.token (chmod 600) — the token IS the domain binding.
#   The cloudflared container is removed but re-created from the same token.
# Cleaned:
#   omp-server containers (both profiles), omp-server* images,
#   omp-server/data/{runs.json,frames/*,prompts/*,server.pid,server.log}.
#   Live :5656 stack is never touched (own compose file, own project).
set -euo pipefail
IFS=$'\n\t'

ROOT="$(cd "$(dirname "$0")" && pwd)"
ELIA_DIR="$ROOT/omp-server"
COMPOSE="docker compose -f $ELIA_DIR/docker-compose.yml"

log() { printf '[reset] %s\n' "$*"; }
die() { printf '[reset] ERROR: %s\n' "$*" >&2; exit 1; }

UP=0
BUILD=1
for arg in "$@"; do
  case "$arg" in
    --up) UP=1 ;;
    --no-build) BUILD=0 ;;
    -h|--help)
      sed -n '1,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown flag: $arg (see --help)" ;;
  esac
done

command -v docker >/dev/null 2>&1 || die "docker CLI not found."

# ── 0. Preflight: token must exist or the domain can't come back ──
if [ ! -s "$ELIA_DIR/config/tunnel.token" ]; then
  log "WARN: omp-server/config/tunnel.token missing/empty — domain will NOT survive."
  log "Restore it (POST /tunnel/setup) before --up, or continue for a clean slate."
fi

# ── 1. Down everything incl. tunnel-profile sidecar ──
log "compose down (incl. tunnel profile)…"
(cd "$ROOT" && { docker compose -f omp-server/docker-compose.yml --profile tunnel down --remove-orphans 2>/dev/null || docker-compose -f omp-server/docker-compose.yml --profile tunnel down --remove-orphans 2>/dev/null; }) || true

# ── 2. Remove our images only (live images untouched) ──
MAP=$(docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep -E '^omp-server(:| )' || true)
if [ -n "$MAP" ]; then
  echo "$MAP" | while read -r _ id; do
    [ -n "$id" ] && docker rmi -f "$id" 2>/dev/null || true
  done
  log "removed omp-server images."
else
  log "no omp-server images to remove."
fi

# ── 3. Clear runtime data, keep configs + tokens ──
rm -f "$ELIA_DIR/data/runs.json" "$ELIA_DIR/data/server.pid" "$ELIA_DIR/data/server.log"
rm -f "$ELIA_DIR/data/frames/"*.jsonl 2>/dev/null || true
rm -f "$ELIA_DIR/data/prompts/"*.txt 2>/dev/null || true
log "cleared runs/frames/prompts/pid/log (configs + tunnel.token kept)."

# ── 4. Rebuild (unless skipped) ──
if [ "$BUILD" = "1" ]; then
  log "rebuilding image…"
  (cd "$ROOT" && docker build -f omp-server/Dockerfile -t omp-server .)
  log "rebuilt omp-server."
fi

if [ "$UP" = "1" ]; then
  log "restarting stack with tunnel…"
  exec "$ROOT/start.sh" --docker --with-tunnel
fi

log "reset done. Token + configs preserved; domain rebinds on next up."
echo "  Start: ./start.sh --docker --with-tunnel"
