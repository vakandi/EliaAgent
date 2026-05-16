#!/bin/zsh
set -euo pipefail
IFS=$'\n\t'

AGENT_DIR="$HOME/EliaAI"
LOG_DIR="$AGENT_DIR/logs"
LOG_FILE="$LOG_DIR/codemem_viewer.log"
PID_FILE="/tmp/elia_codemem_pids/viewer.pid"
PORT="${CODEMEM_VIEWER_PORT:-38888}"
MAX_RESTARTS=10
INITIAL_RESTART_DELAY=2
MAX_RESTART_DELAY=30
HEALTH_CHECK_INTERVAL=5

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [viewer] $*" | tee -a "$LOG_FILE" >&2
}

preflight_check() {
    mkdir -p "$LOG_DIR" 2>/dev/null || true
    mkdir -p "$(dirname $PID_FILE)" 2>/dev/null || true
    
    if [[ -x "$AGENT_DIR/integrations/codemem/packages/cli/dist/index.js" ]]; then
        CODEMEM_CLI="node"
        CODEMEM_ARGS="$AGENT_DIR/integrations/codemem/packages/cli/dist/index.js"
    elif command -v codemem &>/dev/null; then
        CODEMEM_CLI="codemem"
        CODEMEM_ARGS=""
    else
        log "ERROR: codemem CLI not found"
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

start_viewer_process() {
    log "[VIEWER] Starting codemem viewer on port $PORT..."
    
    if [[ "$CODEMEM_CLI" == "node" ]]; then
        "$CODEMEM_CLI" "$CODEMEM_ARGS" serve start --host 127.0.0.1 --port "$PORT" >> "$LOG_FILE" 2>&1 &
    else
        "$CODEMEM_CLI" serve start --host 127.0.0.1 --port "$PORT" >> "$LOG_FILE" 2>&1 &
    fi
    
    echo $! > "$PID_FILE"
    
    log "[VIEWER] Started with PID $(cat $PID_FILE)"
}

get_viewer_pid() {
    [[ -f "$PID_FILE" ]] && cat "$PID_FILE"
}

is_viewer_running() {
    local pid=$(get_viewer_pid)
    [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

health_check() {
    local pid=$(get_viewer_pid)
    
    if ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi
    
    if ! (echo > /dev/tcp/127.0.0.1/$PORT) 2>/dev/null; then
        return 1
    fi
    
    return 0
}

cleanup() {
    log "[SIGNAL] Received shutdown signal - cleaning up..."
    stop_viewer_process
    log "[VIEWER] Viewer stopped gracefully"
    exit 0
}

stop_viewer_process() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "[VIEWER] Stopping viewer (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

trap cleanup SIGTERM SIGINT SIGHUP

main() {
    preflight_check
    
    if is_port_in_use; then
        log "WARNING: Port $PORT already in use - attempting to kill existing process..."
        kill_port_process || {
            log "ERROR: Could not free port $PORT"
            exit 1
        }
    fi
    
    log "=== Codemem Viewer Robust Launcher ==="
    log "Port: $PORT"
    log "Log file: $LOG_FILE"
    log "Max restarts: $MAX_RESTARTS"
    log "PID file: $PID_FILE"
    
    local restart_count=0
    local current_delay=$INITIAL_RESTART_DELAY
    
    while [[ $restart_count -lt $MAX_RESTARTS ]]; do
        start_viewer_process
        
        log "Waiting for viewer to become healthy..."
        local health_attempts=10
        local health_attempt=0
        
        while [[ $health_attempt -lt $health_attempts ]]; do
            if health_check; then
                log "Viewer is healthy and responding"
                break
            fi
            sleep 1
            health_attempt=$((health_attempt + 1))
        done
        
        if [[ $health_attempt -eq $health_attempts ]]; then
            log "WARNING: Viewer did not become healthy in time"
        fi
        
        restart_count=0
        current_delay=$INITIAL_RESTART_DELAY
        
        log "Viewer running (PID: $(get_viewer_pid)) - monitoring..."
        
        local pid=$(get_viewer_pid)
        while kill -0 "$pid" 2>/dev/null; do
            sleep "$HEALTH_CHECK_INTERVAL"
            
            if ! health_check; then
                log "WARNING: Health check failed - viewer may be unresponsive"
            fi
        done
        
        local exit_code=0
        wait "$pid" 2>/dev/null || exit_code=$?
        
        log "Viewer exited with code: $exit_code"
        
        if [[ $exit_code -eq 0 ]] || [[ $exit_code -eq 130 ]] || [[ $exit_code -eq 143 ]]; then
            log "Viewer exited normally - not restarting"
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
    
    log "=== Codemem Viewer Shutdown ==="
    stop_viewer_process
}

main "$@"
