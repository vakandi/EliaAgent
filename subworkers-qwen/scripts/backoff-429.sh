#!/usr/bin/env bash
# 429 drill: backoff + model fallback across the 9 zen-free models (gap 9).
# Usage: ./scripts/backoff-429.sh [prompt]
# Talks to the SHIM on 5676 only (never the daemon or live ports directly).
set -euo pipefail
IFS=$'\n\t'

SHIM_URL="${SHIM_URL:-http://127.0.0.1:5676}"
TOKEN="${ELIA_AUTH_TOKEN:-}"
PROMPT_TEXT="${1:-429 drill probe: reply with the single word PONG.}"
MODELS_CSV="${ZEN_FREE_MODELS:-muse-spark-1.3-contributor-free,muse-spark-1.2-contributor-free,big-pickle,jev-1.13-free,deepseek-v4-flash-free,mimo-v2.5-free,ling-3.0-flash-fin-free,nemotron-3-ultra-free,nemotron-3.5-lightning-free}"

command -v curl >/dev/null 2>&1 || { echo "curl required" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq required" >&2; exit 1; }

auth_args=()
if [[ -n "$TOKEN" ]]; then
  auth_args=(-H "Authorization: Bearer $TOKEN")
fi

log() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] $*" >&2; }

log "shim=$SHIM_URL"
if ! curl -sf -m 5 "$SHIM_URL/health" | jq -e '.status == "ok"' >/dev/null; then
  log "ERROR shim /health not ok — is the stack up? (docker compose up -d)"
  exit 1
fi
log "daemon: $(curl -s -m 10 "${auth_args[@]}" "$SHIM_URL/daemon/status" | jq -c '{ok, daemon: .daemon}')"
log "models: $MODELS_CSV"

# Trigger the cheapest pilot; the shim walks the fallback chain with backoff.
# A 202-admission with queued_429 status = drill working as designed.
resp=$(curl -s -m 30 "${auth_args[@]}" -X POST "$SHIM_URL/trigger/workspace-digest" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg m "$PROMPT_TEXT" '{message: $m}')")
echo "$resp" | jq .
status=$(echo "$resp" | jq -r '.status // "unknown"')
session=$(echo "$resp" | jq -r '.session_id // empty')

if [[ "$status" == "queued_429" ]]; then
  log "DRILL PASS: all models 429'd, run queued + Discord alert fired."
  exit 0
fi

if [[ -n "$session" ]]; then
  log "admitted session=$session — polling SSE events for turn-completion (gap 10)..."
  for i in 1 2 3 4 5 6; do
    sleep 20
    events=$(curl -s -m 30 "${auth_args[@]}" \
      "$SHIM_URL/sessions/workspace-digest/$session/events")
    count=$(echo "$events" | jq '.events | length')
    log "poll $i: $count events"
    if [[ "$count" -gt 0 ]]; then
      echo "$events" | jq '.events[0]'
      log "DRILL PASS: turn events observed."
      exit 0
    fi
  done
  log "DRILL OPEN: admitted but zero SSE events (provider-throttled?) — see docs/NOTES.md gap 10."
  exit 2
fi

log "ERROR unexpected trigger response (status=$status)"
exit 1
