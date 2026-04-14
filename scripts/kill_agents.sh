#!/bin/zsh
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

SPINNER_DELAY=0.1

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

spinner() {
    local pid=$1
    local message=$2
    local i=0
    while kill -0 "$pid" 2>/dev/null; do
        printf "\r${CYAN}[ spinner ]${NC} $message"
        sleep $SPINNER_DELAY
        ((i++))
    done
    printf "\r${GREEN}[OK]${NC} $message complete\n"
}

progress_bar() {
    local current=$1
    local total=$2
    local width=30
    local percent=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    
    printf "\r${PURPLE}["
    printf "%${filled}s" | tr ' ' '='
    printf "%${empty}s" | tr ' ' '-'
    printf "] ${percent}%%${NC}"
}

get_ram_usage() {
    local total=0
    for pid in $(pgrep -f "opencode" 2>/dev/null || true); do
        local mem=$(ps -o rss= -p "$pid" 2>/dev/null || echo 0)
        total=$((total + mem))
    done
    echo $((total / 1024))
}

kill_with_animation() {
    local pid=$1
    local name=$2
    
    if kill -0 "$pid" 2>/dev/null; then
        spinner $pid "Killing $name (PID: $pid)" &
        local spinner_pid=$!
        
        kill "$pid" 2>/dev/null || true
        sleep 1
        
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        kill $spinner_pid 2>/dev/null || true
        wait $spinner_pid 2>/dev/null || true
    fi
}

kill_all_opencode() {
    echo ""
    log "=== AGGRESSIVE OPENCODE CLEANUP ==="
    echo ""
    
    local before_ram=$(get_ram_usage)
    log "RAM used by opencode: ${before_ram}MB"
    
    echo ""
    echo -e "${CYAN}===================================================${NC}"
    echo -e "${PURPLE}CLEANING ALL OPENCODE PROCESSES...${NC}"
    echo -e "${CYAN}===================================================${NC}"
    echo ""
    
    local total_pids=$(pgrep -f "opencode" 2>/dev/null | wc -l | tr -d ' ')
    log "Found $total_pids opencode processes"
    
    killed=0
    
    local opencode_pids=$(pgrep -f "opencode-darwin-arm64/bin/opencode" 2>/dev/null || true)
    for pid in $opencode_pids; do
        if kill -0 "$pid" 2>/dev/null; then
            log "Killing opencode main process PID: $pid"
            kill -9 "$pid" 2>/dev/null || true
            killed=$((killed + 1))
        fi
    done
    
    local node_pids=$(pgrep -f "node.*opencode" 2>/dev/null || true)
    for pid in $node_pids; do
        if kill -0 "$pid" 2>/dev/null; then
            log "Killing opencode node subprocess PID: $pid"
            kill -9 "$pid" 2>/dev/null || true
            killed=$((killed + 1))
        fi
    done
    
    sleep 1
    local remaining=$(pgrep -f "opencode" 2>/dev/null || true)
    if [[ -n "$remaining" ]]; then
        warning "Force killing remaining: $remaining"
        echo "$remaining" | while read pid; do
            kill -9 "$pid" 2>/dev/null || true
            killed=$((killed + 1))
        done
    fi
    
    echo ""
    progress_bar 1 1
    echo ""
    
    local after_ram=$(get_ram_usage)
    local freed=$((before_ram - after_ram))
    
    if [[ $freed -lt 0 ]]; then
        freed=0
    fi
    
    success "Killed $killed processes"
    success "Freed ~${freed}MB RAM"
    echo ""
}

kill_agents() {
    echo ""
    log "=== KILLING AGENT PROCESSES ==="
    echo ""
    
    local gemini_pids=$(pgrep -f "gemini" 2>/dev/null || true)
    if [[ -n "$gemini_pids" ]]; then
        log "Killing Gemini processes: $gemini_pids"
        for pid in $gemini_pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
        success "Killed Gemini processes"
    fi
    
    local kiro_pids=$(pgrep -f "kiro" 2>/dev/null || true)
    if [[ -n "$kiro_pids" ]]; then
        log "Killing Kiro processes: $kiro_pids"
        for pid in $kiro_pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
        success "Killed Kiro processes"
    fi
    
    local ohmy_pids=$(pgrep -f "oh-my-opencode" 2>/dev/null || true)
    if [[ -n "$ohmy_pids" ]]; then
        log "Killing oh-my-opencode: $ohmy_pids"
        for pid in $ohmy_pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
    fi
    
    local fcm_pids=$(pgrep -f "free-coding-models" 2>/dev/null || true)
    if [[ -n "$fcm_pids" ]]; then
        log "Killing free-coding-models: $fcm_pids"
        for pid in $fcm_pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
    fi
}

cleanup_state() {
    echo ""
    log "=== CLEANING STATE FILES ==="
    echo ""
    
    rm -f ~/EliaAI/.agent_payloads/*.lock 2>/dev/null || true
    rm -f ~/EliaAI/ralph-loop.local.md 2>/dev/null || true
    rm -f ~/.config/opencode/ralph-loop.local.md 2>/dev/null || true
    rm -f ~/EliaAI/.ralph-state.json 2>/dev/null || true
    rm -rf ~/.openclaw/sessions/* 2>/dev/null || true
    
    success "State files cleaned"
}

show_status() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}*** AGENT CLEANUP COMPLETE ***${NC}"
    echo "=========================================="
    echo ""
    
    local remaining=$(pgrep -f "opencode" 2>/dev/null || true)
    if [[ -n "$remaining" ]]; then
        warning "Remaining opencode processes:"
        ps aux | grep opencode | grep -v grep | awk '{print "  PID:", $2, "MEM:", $6/1024 "MB", "CMD:", $11, $12, $13}'
    else
        success "No opencode processes remaining"
    fi
    
    echo ""
    local after_ram=$(get_ram_usage)
    log "Opencode RAM usage now: ${after_ram}MB"
    echo ""
}

main() {
    echo ""
    echo "================================================"
    echo "     EliaAI Agent Process Killer v2.0          "
    echo "     MEMORY CLEANUP UTILITY                    "
    echo "================================================"
    echo ""
    
    kill_all_opencode
    kill_agents
    cleanup_state
    show_status
}

main "$@"
