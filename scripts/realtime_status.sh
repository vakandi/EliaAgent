#!/bin/zsh
# Mycroft Agent Simple Log Monitor - Just like tail but better

# Get the directory where this script is located, then get parent (EliaAI root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${AGENT_DIR}/logs/output.log"
MULTI_AGENT_LOG="${AGENT_DIR}/logs/multi_agent.log"

# Simple colors (optional, not aggressive)
GREEN='\033[32m'
YELLOW='\033[33m' 
RED='\033[31m'
BLUE='\033[34m'
RESET='\033[0m'

# Get the active log file (multi-agent or single)
get_active_log() {
    # Check if LaunchAgent is running and has multi-agent logs
    if launchctl list | grep -q com.elia.mycroft-agent && [[ -f "$MULTI_AGENT_LOG" ]]; then
        echo "$MULTI_AGENT_LOG"
    elif [[ -f "$LOG_FILE" ]]; then
        echo "$LOG_FILE"
    else
        echo ""
    fi
}

# Show simple status header
show_header() {
    local active_log=$(get_active_log)
    local status="IDLE"
    local next="Unknown"
    
    # Check if agent is running
    if [[ -f "${AGENT_DIR}/.agent.lock" ]]; then
        local pid=$(cat "${AGENT_DIR}/.agent.lock" 2>/dev/null)
        if kill -0 "$pid" 2>/dev/null; then
            status="${GREEN}● RUNNING${RESET}"
        else
            status="${YELLOW}○ STALE${RESET}"
        fi
    else
        status="${BLUE}○ IDLE${RESET}"
    fi
    
    # Calculate next run time for LaunchAgent
    local current_hour=$(date +%H)
    local next_run=""
    for h in 10 12 14 16 18 20; do
        if [[ $current_hour -lt $h ]]; then
            next_run="$h:00"
            break
        fi
    done
    [[ -n "$next_run" ]] && next="Today at $next_run" || next="Tomorrow at 10:00"
    
    # Simple header
    echo -e "${BLUE}🤖 Mycroft Agent${RESET} | Status: $status | Next: $next | Log: $(basename "$active_log" 2>/dev/null || echo "None")"
    echo "$(printf '─%.0s' {1..80})"
}

# Main monitor function
main() {
    case "${1:-}" in
        -h|--help)
            echo "Usage: $0 [options]"
            echo "  (no args)  - Show header and tail logs"
            echo "  -f, --follow - Follow logs like tail -f"
            echo "  -h, --help  - Show this help"
            exit 0
            ;;
        -f|--follow)
            local active_log=$(get_active_log)
            if [[ -z "$active_log" ]]; then
                echo -e "${RED}No log files found${RESET}"
                exit 1
            fi
            
            # Show header once, then tail
            show_header
            echo ""
            tail -f "$active_log" 2>/dev/null
            ;;
        *)
            local active_log=$(get_active_log)
            if [[ -z "$active_log" ]]; then
                echo -e "${RED}No log files found${RESET}"
                exit 1
            fi
            
            # Show header and last 50 lines
            show_header
            echo ""
            tail -50 "$active_log" 2>/dev/null
            ;;
    esac
}

main "$@"
