#!/bin/zsh
# ============================================================
# TRIGGER TEMPLATE — Universal subworker trigger for OpenCode
# ============================================================
# Usage:
#   1. Copy this file → scripts/trigger_<name>.sh
#   2. Change AGENT_NAME (underscore convention, e.g. my_agent)
#   3. Create subworkers/<agent-id>/PROMPT.md
#   4. Create subworkers/<agent-id>/.enabled to activate
#   5. (Optional) Create .loop_mode for server-attach loop mode
#   6. chmod +x scripts/trigger_<name>.sh
# ============================================================
set -euo pipefail

# ═══════════════════════════════════════════════════════════
# CONFIG — Change only this line per agent
# ═══════════════════════════════════════════════════════════
: "${AGENT_NAME:=CHANGE_ME}"
# ═══════════════════════════════════════════════════════════

# Derive hyphenated ID from underscored name
AGENT_ID="${AGENT_NAME//_/-}"

# ── Paths ─────────────────────────────────────────────────
AGENT_DIR="/path/to/EliaAI"
SUBWORKER_DIR="$AGENT_DIR/subworkers/$AGENT_ID"
WORKSPACE_DIR="$SUBWORKER_DIR/workspace"
LOG_DIR="$AGENT_DIR/subworkers/logs"
AGGREGATE_LOG="$LOG_DIR/${AGENT_NAME}.log"
RUNS_DIR="$LOG_DIR/runs/${AGENT_NAME}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
RUN_LOG="$RUNS_DIR/${TIMESTAMP}.log"
mkdir -p "$RUNS_DIR" "$WORKSPACE_DIR"

# ── Daily workspace docs folder ──────────────────────────
DAILY_DIR="$WORKSPACE_DIR/docs/$(date '+%Y-%m-%d')"
mkdir -p "$DAILY_DIR"

# ── Logger ────────────────────────────────────────────────
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$AGGREGATE_LOG" >> "$RUN_LOG"
}

# ── PATH Resolution (launchd lacks ~/.bun/bin) ────────────
if ! command -v oh-my-opencode &>/dev/null; then
  for dir in "$HOME/.bun/bin" "$HOME/.opencode/bin" /opt/homebrew/bin /usr/local/bin; do
    if [[ -x "$dir/oh-my-opencode" ]]; then
      export PATH="$dir:$PATH"
      break
    fi
  done
fi
if ! command -v oh-my-opencode &>/dev/null; then
  log "FATAL: oh-my-opencode not found"
  exit 1
fi

log "Starting $AGENT_ID trigger..."

# ── .enabled gate ─────────────────────────────────────────
ENABLED_FLAG="$SUBWORKER_DIR/.enabled"
if [[ ! -f "$ENABLED_FLAG" ]]; then
    log "$AGENT_ID skipped (.enabled not found). Create $ENABLED_FLAG to activate."
    exit 0
fi

# ── Load PROMPT.md ────────────────────────────────────────
PROMPT_FILE="$SUBWORKER_DIR/PROMPT.md"
if [[ ! -f "$PROMPT_FILE" ]]; then
    log "ERROR: PROMPT.md not found at $PROMPT_FILE"
    exit 1
fi
PROMPT=$(cat "$PROMPT_FILE")

# ── Load personality (optional) ───────────────────────────
PERSONALITY_FILE="$HOME/.config/opencode/agents/${AGENT_ID}.md"
PERSONALITY=$(cat "$PERSONALITY_FILE" 2>/dev/null || echo "")

# ── Detect mode: task vs loop ─────────────────────────────
LOOP_FLAG="$SUBWORKER_DIR/.loop_mode"
if [[ -f "$LOOP_FLAG" ]]; then
    MODE="loop"
else
    MODE="task"
fi
log "Mode: $MODE"

# ── Detect proxy ──────────────────────────────────────────
USE_PROXY=0
if [[ "${USE_PROXY_ENV:-0}" == "1" ]]; then
    USE_PROXY=1
elif [[ -f "$AGENT_DIR/.proxy_enabled" ]]; then
    USE_PROXY=1
fi
if [[ "$USE_PROXY" == "1" ]]; then
    log "[PROXY] Proxy mode enabled"
fi

# ═══════════════════════════════════════════════════════════
# EXECUTE
# ═══════════════════════════════════════════════════════════
cd "$AGENT_DIR"

if [[ "$MODE" == "loop" ]]; then
    # ── Loop mode: server-attach (promoters, persistent agents) ──
    OPENCODE_PORT=4096

    if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
        if [[ "$USE_PROXY" == "1" ]]; then
            SERVER_PID=$(lsof -ti :$OPENCODE_PORT 2>/dev/null | head -1)
            if [[ -n "$SERVER_PID" ]] && ps -p "$SERVER_PID" -o args= 2>/dev/null | grep -q proxychains4; then
                log "[SERVER] Already running with proxychains4 (PID: $SERVER_PID) — attaching"
            else
                if [[ -n "$SERVER_PID" ]]; then
                    log "[SERVER] Restarting server with proxychains4..."
                    kill -9 "$SERVER_PID" 2>/dev/null || true
                    sleep 2
                fi
                nohup proxychains4 -f ~/.proxychains.conf opencode serve --port $OPENCODE_PORT \
                    > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
                sleep 3
            fi
        else
            log "[SERVER] OpenCode server running on port $OPENCODE_PORT — attaching"
        fi
    else
        log "[SERVER] Starting new server on port $OPENCODE_PORT"
        if [[ "$USE_PROXY" == "1" ]]; then
            nohup proxychains4 -f ~/.proxychains.conf opencode serve --port $OPENCODE_PORT \
                > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
        else
            nohup opencode serve --port $OPENCODE_PORT \
                > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
        fi
        sleep 3
    fi

    # Determine loop command
    if [[ -f "$AGENT_DIR/.ralph_mode" ]]; then
        LOOP_CMD="/ralph-loop"
    else
        LOOP_CMD="/ulw-loop"
    fi
    log "Loop: $LOOP_CMD"

    oh-my-opencode run --attach "http://127.0.0.1:$OPENCODE_PORT" \
        -d "$WORKSPACE_DIR" -a "$AGENT_ID" "$LOOP_CMD" >> "$RUN_LOG" 2>&1
else
    # ── Task mode: single-shot (SEO, blog, one-off tasks) ──
    PERSONALITY_BLOCK=""
    if [[ -n "$PERSONALITY" ]]; then
        PERSONALITY_BLOCK="PERSONALITY:
$PERSONALITY"
    fi

    oh-my-opencode run -d "$WORKSPACE_DIR" -a "$AGENT_ID" "Execute ONE task now:

$PERSONALITY_BLOCK

PROMPT:
$PROMPT" >> "$RUN_LOG" 2>&1
fi

log "$AGENT_ID completed"
