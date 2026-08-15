#!/bin/zsh
# OpenCode Server launcher with auto-restart

set -euo pipefail

AGENT_DIR="$HOME/EliaAI"

# ============================================================
# SCHEDULER DISABLE GUARD
# ============================================================
if [[ -f "${AGENT_DIR}/.scheduler_disabled" ]]; then
    echo "[GUARD] .scheduler_disabled found — serve-fixed disabled. Exiting."
    exit 0
fi
PROXY_CONF="$HOME/.proxychains.conf"
LOG_FILE="/tmp/opencode_server_restart.log"

PORT="${1:-4096}"

MAX_RESTARTS=10
RESTART_DELAY=5
MAX_DELAY=60

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

is_port_free() {
    ! nc -z 127.0.0.1 "$PORT" 2>/dev/null
}

is_already_opencode_server() {
    local pid
    pid=$(lsof -ti :"$PORT" 2>/dev/null | head -1)
    [[ -z "$pid" ]] && return 1
    local process_name
    process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    # NOTE: macOS `ps -o comm=` returns the FULL PATH for node, so match substring.
    [[ "$process_name" == *"opencode"* ]] || [[ "$process_name" == *"node"* ]] || return 1
    return 0
}

kill_existing() {
    if nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
        if is_already_opencode_server; then
            log "Port $PORT holds an opencode server - preserving it (no kill)."
            return 1
        fi
        log "Port $PORT in use by non-opencode process - killing it..."
        local existing_pid
        existing_pid=$(lsof -ti :"$PORT" 2>/dev/null | head -1)
        if [[ -n "$existing_pid" ]]; then
            kill -9 "$existing_pid" 2>/dev/null || true
            sleep 2
        fi
    fi
    return 0
}

start_server() {
    local PROXY_HTTP=""
    local PROXY_HTTPS=""
    
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

    log "[SERVER] Starting on port $PORT..."
    if [[ -n "$PROXY_HTTP" ]]; then
        exec env HTTP_PROXY="$PROXY_HTTP" HTTPS_PROXY="$PROXY_HTTPS" http_proxy="$PROXY_HTTP" https_proxy="$PROXY_HTTPS" opencode serve --port "$PORT"
    else
        exec opencode serve --port "$PORT"
    fi
}

main() {
    local restart_count=0
    local current_delay=$RESTART_DELAY

    log "=== OpenCode Server Started ==="
    log "Port: $PORT"
    log "Max restarts: $MAX_RESTARTS"

    if nc -z 127.0.0.1 "$PORT" 2>/dev/null && is_already_opencode_server; then
        log "Existing opencode server on port $PORT — exiting cleanly (no kill)"
        exit 0
    fi

    while [[ $restart_count -lt $MAX_RESTARTS ]]; do
        if ! kill_existing; then
            log "Existing opencode server detected on port $PORT — adopting it"
            exit 0
        fi

        start_server &
        SERVER_PID=$!

        log "Server started (PID: $SERVER_PID)"

        sleep 3

        if kill -0 "$SERVER_PID" 2>/dev/null; then
            log "Server running successfully"
            restart_count=0
            current_delay=$RESTART_DELAY
            
            wait "$SERVER_PID" || true
            log "Server exited with code: $?"
        else
            log "Server failed to start or died immediately"
        fi

        restart_count=$((restart_count + 1))

        if [[ $restart_count -ge $MAX_RESTARTS ]]; then
            log "MAX RESTARTS REACHED - giving up"
            exit 1
        fi

        log "Restarting in ${current_delay}s (attempt $restart_count/$MAX_RESTARTS)..."
        sleep "$current_delay"
        current_delay=$((current_delay * 2))
        [[ $current_delay -gt $MAX_DELAY ]] && current_delay=$MAX_DELAY
    done
}

main "$@"