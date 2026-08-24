#!/bin/zsh
set -euo pipefail
IFS=$'\n\t'

AGENT_DIR="$HOME/EliaAI"
PROXY_CONF="$HOME/.proxychains.conf"
LOG_DIR="$AGENT_DIR/scripts/logs"
LOG_FILE="$LOG_DIR/opencode-serve.log"
PID_FILE="/tmp/opencode-serve.pid"

PORT="${1:-4096}"
MAX_RESTARTS=10
INITIAL_RESTART_DELAY=2
MAX_RESTART_DELAY=30
HEALTH_CHECK_INTERVAL=5

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [serve] $*" | tee -a "$LOG_FILE" >&2
}

preflight_check() {
    mkdir -p "$LOG_DIR" 2>/dev/null || true
    
    if ! command -v opencode &>/dev/null; then
        log "ERROR: 'opencode' command not found in PATH"
        log "PATH: $PATH"
        exit 1
    fi
    
    if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [[ "$PORT" -lt 1024 ]] || [[ "$PORT" -gt 65535 ]]; then
        log "ERROR: Invalid port: $PORT (must be 1024-65535)"
        exit 1
    fi
    
    log "Pre-flight check passed"
}

get_port_pid() {
    lsof -ti :"$PORT" 2>/dev/null | head -1
}

is_port_in_use() {
    [[ -n "$(get_port_pid)" ]]
}

kill_port_process() {
    local max_attempts=5
    local attempt=0
    
    while is_port_in_use && [[ $attempt -lt $max_attempts ]]; do
        local pid=$(get_port_pid)
        log "Port $PORT in use by PID $pid - attempting to kill (attempt $((attempt+1))/$max_attempts)..."
        
        kill -TERM "$pid" 2>/dev/null || true
        sleep 1
        
        if is_port_in_use; then
            kill -KILL "$pid" 2>/dev/null || true
            sleep 1
        fi
        
        attempt=$((attempt + 1))
    done
    
    if is_port_in_use; then
        log "ERROR: Failed to free port $PORT after $max_attempts attempts"
        return 1
    fi
    
    log "Port $PORT is now free"
    return 0
}

setup_proxy() {
    if [[ -f "$AGENT_DIR/.proxy_enabled" ]] && [[ -f "$PROXY_CONF" ]]; then
        local PROXY_LINE=$(grep -v "^#" "$PROXY_CONF" | grep "http " | head -1)
        
        if [[ -n "$PROXY_LINE" ]]; then
            local ip=$(echo "$PROXY_LINE" | awk '{print $2}')
            local port_proxy=$(echo "$PROXY_LINE" | awk '{print $3}')
            local user=$(echo "$PROXY_LINE" | awk '{print $4}')
            local pass=$(echo "$PROXY_LINE" | awk '{print $5}')
            
            PROXY_HTTP="http://${user}:${pass}@${ip}:${port_proxy}"
            PROXY_HTTPS="http://${user}:${pass}@${ip}:${port_proxy}"
            log "[PROXY] Loaded proxy: $ip:$port_proxy (HTTP_PROXY env vars ready)"
        else
            log "[PROXY] No valid proxy line found in $PROXY_CONF"
        fi
    else
        log "[PROXY] No proxy enabled"
    fi
}

start_server_process() {
    setup_proxy
    
    log "[SERVER] Starting opencode serve on port $PORT..."
    
    if [[ -n "${PROXY_HTTP:-}" ]]; then
        env HTTP_PROXY="$PROXY_HTTP" HTTPS_PROXY="$PROXY_HTTPS" http_proxy="$PROXY_HTTP" https_proxy="$PROXY_HTTPS" opencode serve --port "$PORT" >> "$LOG_FILE" 2>&1 &
    else
        opencode serve --port "$PORT" >> "$LOG_FILE" 2>&1 &
    fi
    echo $! > "$PID_FILE"
    
    log "[SERVER] Started with PID $(cat $PID_FILE)"
}

stop_server_process() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "[SERVER] Stopping server (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

get_server_pid() {
    [[ -f "$PID_FILE" ]] && cat "$PID_FILE"
}

is_server_running() {
    local pid=$(get_server_pid)
    [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

health_check() {
    local pid=$(get_server_pid)
    
    if ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi
    
    if ! nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

is_already_opencode_server() {
    local pid=$(get_port_pid)
    [[ -z "$pid" ]] && return 1
    
    local process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    [[ "$process_name" == *"opencode"* ]] || return 1
    
    if nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
        log "[SERVER] Found existing opencode server on port $PORT (PID: $pid)"
        echo "$pid" > "$PID_FILE"
        return 0
    fi
    
    return 1
}

cleanup() {
    log "[SIGNAL] Received shutdown signal - cleaning up..."
    stop_server_process
    log "[SERVER] Server stopped gracefully"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGHUP

main() {
    preflight_check
    
    log "=== OpenCode Server Robust Launcher ==="
    log "Port: $PORT"
    log "Log file: $LOG_FILE"
    log "Max restarts: $MAX_RESTARTS"
    log "PID file: $PID_FILE"
    
    # Check if a healthy opencode server is ALREADY running — don't touch it
    if is_already_opencode_server; then
        log "[SERVER] Existing opencode server is healthy — exiting cleanly (no kill)"
        exit 0
    fi
    
    kill_port_process || {
        log "ERROR: Could not free port $PORT"
        exit 1
    }
    
    local restart_count=0
    local current_delay=$INITIAL_RESTART_DELAY
    
    while [[ $restart_count -lt $MAX_RESTARTS ]]; do
        start_server_process
        
        log "Waiting for server to become healthy..."
        local health_attempts=10
        local health_attempt=0
        
        while [[ $health_attempt -lt $health_attempts ]]; do
            if health_check; then
                log "Server is healthy and responding"
                break
            fi
            sleep 1
            health_attempt=$((health_attempt + 1))
        done
        
        if [[ $health_attempt -eq $health_attempts ]]; then
            log "WARNING: Server did not become healthy in time"
        fi
        
        restart_count=0
        current_delay=$INITIAL_RESTART_DELAY
        
        log "Server running (PID: $(get_server_pid)) - monitoring..."
        
        local pid=$(get_server_pid)
        while kill -0 "$pid" 2>/dev/null; do
            sleep "$HEALTH_CHECK_INTERVAL"
            
            if ! health_check; then
                log "WARNING: Health check failed - server may be unresponsive"
            fi
        done
        
        local exit_code=0
        wait "$pid" 2>/dev/null || exit_code=$?
        
        log "Server exited with code: $exit_code"
        
        if [[ $exit_code -eq 0 ]] || [[ $exit_code -eq 130 ]] || [[ $exit_code -eq 143 ]]; then
            log "Server exited normally - not restarting"
            break
        fi
        
        restart_count=$((restart_count + 1))
        
        if [[ $restart_count -ge $MAX_RESTARTS ]]; then
            log "ERROR: Max restarts ($MAX_RESTARTS) reached - giving up"
            break
        fi
        
        log "Restarting in ${current_delay}s (attempt $restart_count/$MAX_RESTARTS)..."
        sleep "$current_delay"
        
        current_delay=$((current_delay * 2))
        [[ $current_delay -gt $MAX_RESTART_DELAY ]] && current_delay=$MAX_RESTART_DELAY
    done
    
    log "=== OpenCode Server Shutdown ==="
    stop_server_process
}

main "$@"