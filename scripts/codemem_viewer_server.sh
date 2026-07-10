#!/bin/zsh
# Codemem Viewer Server - Standalone launcher
# Similar to playwright/mcp launchers - keeps viewer running

set -euo pipefail

# Configuration
AGENT_DIR="~/EliaAI"
LOG_DIR="${AGENT_DIR}/logs"
PID_DIR="/tmp/elia_codemem_pids"
PID_FILE="${PID_DIR}/viewer.pid"
LOG_FILE="${LOG_DIR}/codemem_viewer_standalone.log"
PORT=38888
DB_PATH="~/.codemem/mem.sqlite"
MAX_RESTARTS=10
INITIAL_RESTART_DELAY=2
MAX_RESTART_DELAY=30
HEALTH_CHECK_INTERVAL=5

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [viewer] $*" | tee -a "$LOG_FILE" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "$LOG_FILE" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$LOG_FILE" >&2
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE" >&2
}

# Setup
mkdir -p "$LOG_DIR" 2>/dev/null || true
mkdir -p "$PID_DIR" 2>/dev/null || true

# Setup proxy if needed
setup_proxy() {
    if [[ -f "$AGENT_DIR/.proxy_enabled" ]] && [[ -f "$HOME/.proxychains.conf" ]]; then
        local PROXY_LINE=$(grep -v "^#" "$HOME/.proxychains.conf" | grep "http " | head -1)
        
        if [[ -n "$PROXY_LINE" ]]; then
            local ip=$(echo "$PROXY_LINE" | awk '{print $2}')
            local port_proxy=$(echo "$PROXY_LINE" | awk '{print $3}')
            local user=$(echo "$PROXY_LINE" | awk '{print $4}')
            local pass=$(echo "$PROXY_LINE" | awk '{print $5}')
            
            log "[PROXY] Proxy is handled by proxychains4 at library level (no env vars needed)"
        else
            log "[PROXY] No valid proxy line found in $PROXY_CONF"
        fi
    else
        log "[PROXY] Using proxychains4 (no env vars needed)"
    fi
}

# Check if port is in use
get_port_pid() {
    lsof -ti :"$PORT" 2>/dev/null | head -1
}

is_port_in_use() {
    [[ -n "$(get_port_pid)" ]]
}

# Kill process on port
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
        error "Failed to free port $PORT after $max_attempts attempts"
        return 1
    fi
    
    log "Port $PORT is now free"
    return 0
}

# Start viewer process
start_viewer() {
    setup_proxy
    
    log "Starting codemem viewer on port $PORT..."
    
    cd "$AGENT_DIR/integrations/codemem"
    npx codemem serve start --foreground --host 127.0.0.1 --port "$PORT" --db-path "$DB_PATH" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    log "Started with PID $pid"
    return 0
}

# Health check
health_check() {
    local pid=$(cat "$PID_FILE" 2>/dev/null)
    
    if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi
    
    if ! nc -z 127.0.0.1 "$PORT" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

# Cleanup handler
cleanup() {
    log "[SIGNAL] Received shutdown signal - cleaning up..."
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "Stopping viewer (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
    log "Viewer stopped gracefully"
    exit 0
}

trap cleanup SIGTERM SIGINT SIGHUP

# Main loop
main() {
    log "=== Codemem Viewer Standalone Server ==="
    log "Port: $PORT"
    log "Log file: $LOG_FILE"
    log "PID file: $PID_FILE"
    log "DB path: $DB_PATH"
    log "Max restarts: $MAX_RESTARTS"
    
    # Kill any existing process on our port
    kill_port_process || {
        error "Could not free port $PORT"
        exit 1
    }
    
    local restart_count=0
    local current_delay=$INITIAL_RESTART_DELAY
    
    while [[ $restart_count -lt $MAX_RESTARTS ]]; do
        start_viewer
        
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
            warning "Viewer did not become healthy in time"
        fi
        
        restart_count=0
        current_delay=$INITIAL_RESTART_DELAY
        
        log "Viewer running (PID: $(cat "$PID_FILE" 2>/dev/null)) - monitoring..."
        
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        while kill -0 "$pid" 2>/dev/null; do
            sleep "$HEALTH_CHECK_INTERVAL"
            
            if ! health_check; then
                warning "Health check failed - viewer may be unresponsive"
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
            error "Max restarts ($MAX_RESTARTS) reached - giving up"
            break
        fi
        
        log "Restarting in ${current_delay}s (attempt $restart_count/$MAX_RESTARTS)..."
        sleep "$current_delay"
        
        current_delay=$((current_delay * 2))
        [[ $current_delay -gt $MAX_RESTART_DELAY ]] && current_delay=$MAX_RESTART_DELAY
    done
    
    log "=== Codemem Viewer Shutdown ==="
    cleanup
}

main "$@"
