#!/usr/bin/env bash
# start.sh — start the omp-server Bun wrapper (omp-server/) on :5677.
#
# Usage:
#   ./start.sh [--docker] [--with-tunnel]
#
#   (no flag)   Host mode: `bun omp-server/server.ts` via nohup from the repo root,
#               pid in omp-server/data/server.pid, log in omp-server/data/server.log.
#   --docker    `docker compose -f omp-server/docker-compose.yml up -d --build`.
#   --with-tunnel  with --docker: also start the cloudflared sidecar
#               (`--profile tunnel`; needs omp-server/config/tunnel.token).
# Safety: if a healthy server already answers on :5677 (open /health OK and
# authed /server/health reports health_status == "healthy"), prints
# already-running and exits 0 without disturbing it (hub-managed
# `bun server.ts` owns the port — never pkill unrelated processes).
set -euo pipefail
IFS=$'\n\t'

ROOT="$(cd "$(dirname "$0")" && pwd)"
ELIA_DIR="$ROOT/omp-server"
ENV_FILE="$ELIA_DIR/.env"
PID_FILE="$ELIA_DIR/data/server.pid"
LOG_FILE="$ELIA_DIR/data/server.log"
BASE="http://127.0.0.1:5677"
WITH_DOCKER=0
WITH_TUNNEL=0

log() { printf '[start] %s\n' "$*"; }
die() { printf '[start] ERROR: %s\n' "$*" >&2; exit 1; }
# docker compose v2 plugin vs standalone binary (this host has only the latter).
dcompose() {
  if docker compose version >/dev/null 2>&1; then docker compose "$@";
  else docker-compose "$@"; fi
}

for arg in "$@"; do
  case "$arg" in
    --docker) WITH_DOCKER=1 ;;
    --with-tunnel) WITH_TUNNEL=1 ;;
    -h|--help)
      sed -n '1,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown flag: $arg (see --help)" ;;
  esac
done

[ -f "$ENV_FILE" ] || die "omp-server/.env not found — run ./install.sh first."
set -a; . "$ENV_FILE"; set +a
[ -n "${ELIA_AUTH_TOKEN:-}" ] || die "ELIA_AUTH_TOKEN is empty in omp-server/.env — re-run ./install.sh."
server_healthy() {
  curl -sf "$BASE/health" >/dev/null 2>&1 || return 1
  curl -sf -H "Authorization: Bearer $ELIA_AUTH_TOKEN" "$BASE/server/health" 2>/dev/null \
    | tr -d '[:space:]' | grep -q '"health_status":"healthy"'
}

if server_healthy; then
  log "already running and healthy on :5677 — leaving it alone."
  exit 0
fi

health_gate() {
  # $1 = attempts, $2 = label
  local i out
  for i in $(seq 1 "$1"); do
    if server_healthy; then
      log "$2 healthy."
      return 0
    fi
    sleep 1
  done
  out="$(curl -sf -H "Authorization: Bearer $ELIA_AUTH_TOKEN" "$BASE/server/health" 2>&1 || true)"
  log "health gate failed; /server/health last said: ${out:-<unreachable>}"
  return 1
}
if [ "$WITH_DOCKER" = "1" ]; then
  log "starting via docker compose (up -d --build)…"
  if [ "$WITH_TUNNEL" = "1" ]; then
    (cd "$ROOT" && dcompose -f omp-server/docker-compose.yml --profile tunnel up -d --build)
  else
    (cd "$ROOT" && dcompose -f omp-server/docker-compose.yml up -d --build)
  fi
  health_gate 30 "docker" || die "docker server did not become healthy within 30s."
  exit 0
fi

# Host mode — refuse to double-start our own pidfile owner.
if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "${PID:-}" ] && kill -0 "$PID" 2>/dev/null; then
    if ps -p "$PID" -o command= 2>/dev/null | grep -q 'bun.*server\.ts'; then
      die "pidfile $PID_FILE points at live bun server.ts (pid $PID) but :5677 is unhealthy — inspect $LOG_FILE, then ./stop.sh."
    fi
    log "WARNING: stale pidfile (pid $PID not a bun server.ts process) — replacing."
  fi
fi

command -v bun >/dev/null 2>&1 || die "bun not found — run ./install.sh first."
mkdir -p "$(dirname "$PID_FILE")"
log "starting host server: nohup bun omp-server/server.ts >> omp-server/data/server.log 2>&1 &"
(cd "$ROOT" && nohup bun omp-server/server.ts >> "$LOG_FILE" 2>&1 & echo $! > "$PID_FILE")
for i in $(seq 1 30); do
  curl -sf "$BASE/health" >/dev/null 2>&1 && break
  [ "$i" -eq 30 ] || sleep 1
done
curl -sf "$BASE/health" >/dev/null 2>&1 || {
  log "server did not answer /health within 30s — tail of $LOG_FILE:"
  tail -n 30 "$LOG_FILE" 2>/dev/null || true
  exit 1
}
health_gate 30 "host" || {
  log "tail of $LOG_FILE:"
  tail -n 30 "$LOG_FILE" 2>/dev/null || true
  exit 1
}
