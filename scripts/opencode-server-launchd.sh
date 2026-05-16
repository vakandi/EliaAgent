#!/bin/zsh
# OpenCode server launcher for launchd - auto-restart on crash

set -euo pipefail

AGENT_DIR="$HOME/EliaAI"
PROXY_CONF="$HOME/.proxychains.conf"
LOG_DIR="$AGENT_DIR/logs"
NTFY_TOPIC="OpenCode"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/server.log"
}

start_server() {
    local PROXY_HTTP=""
    local PROXY_HTTPS=""
    
    # Proxy
    if [[ -f "$AGENT_DIR/.proxy_enabled" ]] && [[ -f "$PROXY_CONF" ]]; then
        PROXY_LINE=$(grep -v "^#" "$PROXY_CONF" | grep "http " | head -1)
        if [[ -n "$PROXY_LINE" ]]; then
            ip=$(echo "$PROXY_LINE" | awk '{print $2}')
            port_proxy=$(echo "$PROXY_LINE" | awk '{print $3}')
            user=$(echo "$PROXY_LINE" | awk '{print $4}')
            pass=$(echo "$PROXY_LINE" | awk '{print $5}')
            PROXY_HTTP="http://${user}:${pass}@${ip}:${port_proxy}"
            PROXY_HTTPS="http://${user}:${pass}@${ip}:${port_proxy}"
            log "[PROXY] Loaded proxy: $ip:$port_proxy (HTTP_PROXY env vars ready)"
        fi
    fi

    log "[SERVER] Starting on port 4096..."
    if [[ -n "$PROXY_HTTP" ]]; then
        exec env HTTP_PROXY="$PROXY_HTTP" HTTPS_PROXY="$PROXY_HTTPS" http_proxy="$PROXY_HTTP" https_proxy="$PROXY_HTTPS" opencode serve --port 4096
    else
        exec opencode serve --port 4096
    fi
}

send_ntfy() {
    local title="$1"
    local message="$2"
    curl -s -H "Title: ${title}" "https://ntfy.sh/${NTFY_TOPIC}" -d "${message}" >/dev/null 2>&1 || true
}

# Max restarts
MAX_RESTARTS=10
PORT=4096
restart_count=0
current_delay=5

log "=== OpenCode Server Starting ==="

while [[ $restart_count -lt $MAX_RESTARTS ]]; do
    # Kill existing on port
    if nc -z 127.0.0.1 $PORT 2>/dev/null; then
        existing=$(lsof -ti :$PORT 2>/dev/null | head -1)
        if [[ -n "$existing" ]]; then
            log "Killing existing server (PID: $existing)"
            kill -9 $existing 2>/dev/null || true
            sleep 2
        fi
    fi

    start_server &
    SERVER_PID=$!

    log "Server started (PID: $SERVER_PID)"

    # Wait to see if it stays up
    sleep 5

    if kill -0 $SERVER_PID 2>/dev/null; then
        log "Server running successfully"
        restart_count=0
        current_delay=5
        wait $SERVER_PID
        exit_code=$?
        log "Server exited with code: $exit_code"
    else
        log "Server died or failed to start"
    fi

    restart_count=$((restart_count + 1))

    if [[ $restart_count -ge $MAX_RESTARTS ]]; then
        log "MAX RESTARTS - giving up"
        send_ntfy "SERVER DOWN PROBLEM" "OpenCode server failed after $MAX_RESTARTS restarts"
        exit 1
    fi

    log "Restarting in ${current_delay}s (attempt $restart_count/$MAX_RESTARTS)"
    sleep $current_delay
    current_delay=$((current_delay * 2))
    [[ $current_delay -gt 60 ]] && current_delay=60
done