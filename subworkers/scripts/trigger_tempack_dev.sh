#!/bin/zsh
set -euo pipefail

AGENT_DIR="/path/to/EliaAI"
LOG_FILE="$AGENT_DIR/subworkers/logs/tempack_dev.log"
OPENCODE_PORT=4096
ENABLED_FLAG="$AGENT_DIR/subworkers/tempack-dev/.enabled"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Tempack Dev trigger..." >> "$LOG_FILE"

# Disabled by default: create .enabled file to allow scheduled runs.
if [[ ! -f "$ENABLED_FLAG" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tempack Dev skipped (.enabled not found)." >> "$LOG_FILE"
    exit 0
fi

if [[ "${USE_PROXY:-0}" == "1" ]]; then
    echo "[PROXY] Proxy mode enabled (proxychains4)" >> "$LOG_FILE"
elif [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    USE_PROXY=1
    echo "[PROXY] Proxy mode enabled (via .proxy_enabled file, proxychains4)" >> "$LOG_FILE"
fi

if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
    if [[ "${USE_PROXY:-0}" == "1" ]]; then
        SERVER_PID=$(lsof -ti :$OPENCODE_PORT 2>/dev/null | head -1)
        if [[ -n "$SERVER_PID" ]] && ps -p "$SERVER_PID" -o args= 2>/dev/null | rg -q proxychains4; then
            echo "[SERVER] Server already running with proxychains4 (PID: $SERVER_PID) - will attach" >> "$LOG_FILE"
        else
            if [[ -n "$SERVER_PID" ]]; then
                echo "[SERVER] USE_PROXY=1 - restarting server with proxychains4..." >> "$LOG_FILE"
                kill -9 $SERVER_PID 2>/dev/null || true
                sleep 2
            fi
            echo "[SERVER] Starting new server with proxychains4..." >> "$LOG_FILE"
            nohup proxychains4 -f ~/.proxychains.conf opencode serve --port $OPENCODE_PORT \
                > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
            sleep 3
        fi
    else
        echo "[SERVER] OpenCode server running on port $OPENCODE_PORT - will auto-attach" >> "$LOG_FILE"
    fi
else
    echo "[SERVER] No existing server - starting new one on port $OPENCODE_PORT" >> "$LOG_FILE"
    if [[ "${USE_PROXY:-0}" == "1" ]]; then
        nohup proxychains4 -f ~/.proxychains.conf opencode serve --port $OPENCODE_PORT \
            > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
    else
        nohup opencode serve --port $OPENCODE_PORT \
            > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
    fi
    sleep 3
fi

RALPH_MODE_FILE="$AGENT_DIR/.ralph_mode"
if [[ -f "$RALPH_MODE_FILE" ]]; then
    LOOP_CMD="/ralph-loop"
else
    LOOP_CMD="/ulw-loop"
fi

TASK_PROMPT="Read /path/to/EliaAI/subworkers/tempack-dev/PROMPT.md and execute the next highest-value coding increment for the Tempack SaaS.
Focus on implementation (not docs), keep changes small and production-ready, then report concise progress."

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Using: $LOOP_CMD" >> "$LOG_FILE"

cd "$AGENT_DIR"
oh-my-opencode run --attach "http://127.0.0.1:$OPENCODE_PORT" -a tempack-dev "$LOOP_CMD

$TASK_PROMPT"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tempack Dev completed" >> "$LOG_FILE"
