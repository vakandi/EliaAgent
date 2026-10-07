#!/usr/bin/env bash
# stop.sh — stop the omp-server Bun wrapper (omp-server/) without touching data.
#
# Usage:
#   ./stop.sh [--with-colima]
#
#   (no flag)       Kill the pid in omp-server/data/server.pid (only if the process
#                   command matches `bun.*server.ts`, else warn + keep it) and
#                   remove the pidfile; then
#                   `docker compose -f omp-server/docker-compose.yml down --remove-orphans`
#                   (tolerated when compose/docker is missing).
set -euo pipefail
IFS=$'\n\t'

ROOT="$(cd "$(dirname "$0")" && pwd)"
ELIA_DIR="$ROOT/omp-server"
PID_FILE="$ELIA_DIR/data/server.pid"
WITH_COLIMA=0

log() { printf '[stop] %s\n' "$*"; }
die() { printf '[stop] ERROR: %s\n' "$*" >&2; exit 1; }

for arg in "$@"; do
  case "$arg" in
    --with-colima) WITH_COLIMA=1 ;;
    -h|--help)
      sed -n '1,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown flag: $arg (see --help)" ;;
  esac
done

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null | tr -d '[:space:]' || true)"
  if [ -z "${PID:-}" ]; then
    log "WARNING: pidfile $PID_FILE is empty — removing it."
    rm -f "$PID_FILE"
  elif kill -0 "$PID" 2>/dev/null; then
    if ps -p "$PID" -o command= 2>/dev/null | grep -q 'bun.*server\.ts'; then
      log "stopping host server (pid $PID)…"
      kill "$PID" 2>/dev/null || true
      for _ in $(seq 1 10); do
        kill -0 "$PID" 2>/dev/null || break
        sleep 1
      done
      if kill -0 "$PID" 2>/dev/null; then
        log "pid $PID still alive — sending SIGKILL."
        kill -9 "$PID" 2>/dev/null || true
      fi
      rm -f "$PID_FILE"
      log "host server stopped; pidfile removed."
    else
      log "WARNING: pid $PID does not match \`bun.*server.ts\` ($(ps -p "$PID" -o command= 2>/dev/null || echo '<unknown>')) — not killing; remove $PID_FILE manually if stale."
    fi
  else
    log "stale pidfile (pid $PID not running) — removing it."
    rm -f "$PID_FILE"
  fi
else
  log "no pidfile ($PID_FILE) — no host server to stop."
fi

if command -v docker >/dev/null 2>&1; then
  log "docker compose down --remove-orphans (tolerated if compose file/stack missing)…"
  (cd "$ROOT" && { docker compose -f omp-server/docker-compose.yml down --remove-orphans 2>/dev/null || docker-compose -f omp-server/docker-compose.yml down --remove-orphans; }) || \
    log "WARNING: compose down failed or stack absent — continuing."
else
  log "docker CLI not found — skipping compose down."
fi

if [ "$WITH_COLIMA" -eq 1 ]; then
  command -v colima >/dev/null 2>&1 || die "colima not found."
  log "stopping colima…"
  colima stop
fi

log "omp-server/data preserved (runs/frames/state untouched). Restart with ./start.sh."
