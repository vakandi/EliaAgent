#!/bin/zsh
set -euo pipefail

AGENT_DIR="/path/to/EliaAI"
LOG_FILE="$AGENT_DIR/subworkers/logs/promoter_yourbrand.log"
OPENCODE_PORT=4096

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting YourBrand Promoter..." >> "$LOG_FILE"

if [[ "${USE_PROXY:-0}" == "1" ]]; then
    echo "[PROXY] Proxy mode enabled (proxychains4)" >> "$LOG_FILE"
elif [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    USE_PROXY=1
    echo "[PROXY] Proxy mode enabled (via .proxy_enabled file, proxychains4)" >> "$LOG_FILE"
fi

if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
    if [[ "${USE_PROXY:-0}" == "1" ]]; then
        SERVER_PID=$(lsof -ti :$OPENCODE_PORT 2>/dev/null | head -1)
        if [[ -n "$SERVER_PID" ]] && ps -p "$SERVER_PID" -o args= 2>/dev/null | grep -q proxychains4; then
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

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Using: $LOOP_CMD" >> "$LOG_FILE"

cd "$AGENT_DIR"
oh-my-opencode run --attach "http://127.0.0.1:$OPENCODE_PORT" -a promoter-template-1 "$LOOP_CMD"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] YourBrand Promoter completed" >> "$LOG_FILE"