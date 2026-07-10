#!/bin/zsh
# EliaAI Scheduler Manager (launchd-based)
# Install, uninstall, or modify scheduler with various interval options
# REPLACES cron with macOS launchd to avoid permission popups

set -euo pipefail

# Configuration
AGENT_DIR="/Users/$(whoami)/EliaAI"
TRIGGER_SCRIPT="${AGENT_DIR}/scripts/trigger_opencode_interactive.sh"
USE_SUDO=false
USE_PROXY=false

# LaunchAgent plist location
LAUNCHD_DIR="${HOME}/Library/LaunchAgents"
LAUNCHD_PLIST="${LAUNCHD_DIR}/com.elia.elia-agent.plist"
LAUNCHD_MORNING_PLIST="${LAUNCHD_DIR}/com.elia.elia-agent-morning.plist"

# Local backup plist locations (in EliaAI folder for backup/version control)
LOCAL_PLIST="${AGENT_DIR}/com.elia.elia-agent.plist"
LOCAL_MORNING_PLIST="${AGENT_DIR}/com.elia.elia-agent-morning.plist"

# State file for UI to read settings
STATE_FILE="${AGENT_DIR}/.scheduler_state"

# Disabled flag — when present, launchd plist will NOT be loaded
# This is the actual enable/disable control (unlike .scheduler_state which is display-only)
DISABLED_FLAG="${AGENT_DIR}/.scheduler_disabled"

# Default settings
DEFAULT_START_HOUR=11
DEFAULT_END_HOUR=21
DEFAULT_INTERVAL="1h"  # 1 hour
DEFAULT_MORNING_HOUR=10  # 10am default for morning cron

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Save state for UI to read
save_state() {
    local interval="$1"
    local start_hour="$2"
    local end_hour="$3"
    local morning_hour="$4"
    local enabled="$5"
    local morning_enabled="$6"
    
    cat > "$STATE_FILE" << EOF
interval=${interval}
startHour=${start_hour}
endHour=${end_hour}
morningHour=${morning_hour}
enabled=${enabled}
morningEnabled=${morning_enabled}
EOF
    log "State saved to ${STATE_FILE}"
}

# Read state
load_state() {
    if [[ -f "$STATE_FILE" ]]; then
        source "$STATE_FILE"
    fi
}

show_usage() {
    cat << 'EOF'
Usage: ./manage_cron.sh [command] [options]

Commands:
  install         Install or update standard scheduler (interval-based)
  install-morning Install or update morning scheduler (MORNING_PROMPT.md)
  uninstall       Remove all EliaAI schedulers (DESTRUCTIVE — removes state)
  uninstall-morning Remove only morning scheduler
  disable         Stop scheduler, unload plist, preserve settings
  enable          Re-enable scheduler, reload plist from saved settings
  show            Show current schedulers
  status          Show scheduler status and settings

Install Options (standard):
  --interval      Set interval: 20min, 30min, 1h, 2h, 3h, 4h (default: 1h)
  --start         Start hour (0-23, default: 11)
  --end           End hour (0-23, default: 21)
  --sudo          Install to system-wide LaunchAgent (requires sudo for plist)
  --proxy         Enable proxy mode (calls 'sp' to refresh proxy before each run)

Install-Morning Options:
  --morning-hour  Hour to run morning scheduler (0-23, default: 10)
  --sudo          Install to system-wide LaunchAgent
  --proxy         Enable proxy mode for morning scheduler

Examples:
  # Install with defaults (every hour)
  ./manage_cron.sh install

  # Every 30 minutes
  ./manage_cron.sh install --interval 30min

  # Every 2 hours
  ./manage_cron.sh install --interval 2h --start 10 --end 22

  # Install morning scheduler at 10am (default)
  ./manage_cron.sh install-morning

  # Install morning scheduler at 8am with proxy
  ./manage_cron.sh install-morning --morning-hour 8 --proxy

  # Remove all schedulers
  ./manage_cron.sh uninstall

  # Show current schedulers
  ./manage_cron.sh show

EOF
}

# Convert interval to seconds
interval_to_seconds() {
    local interval="$1"
    case "$interval" in
        20min) echo "1200" ;;
        30min) echo "1800" ;;
        1h|1hour|hourly) echo "3600" ;;
        1h30|1h30min|90min) echo "5400" ;;
        2h|2hour) echo "7200" ;;
        3h|3hour) echo "10800" ;;
        4h|4hour) echo "14400" ;;
        *) echo "3600" ;;  # default 1h
    esac
}
# Generate calendar entries dynamically based on start/end hours
# FIX: Now respects start_hour and end_hour from arguments
generate_calendar_entries() {
    local interval="$1"
    local start_hour="$2"
    local end_hour="$3"
    
    local entries=""
    
    # Generate entries based on interval
    case "$interval" in
        20min)
            # Every 20 minutes, but only within hour range
            for h in $(seq $start_hour $((end_hour - 1))); do
                for m in 0 20 40; do
                    entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>${m}</integer></dict>\n"
                done
            done
            ;;
        30min|30minute)
            # Every 30 minutes at :00 and :30, within hour range
            for h in $(seq $start_hour $((end_hour - 1))); do
                for m in 0 30; do
                    entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>${m}</integer></dict>\n"
                done
            done
            ;;
        1h|1hour|hourly)
            # Every hour at :00, within hour range
            for h in $(seq $start_hour $((end_hour - 1))); do
                entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>0</integer></dict>\n"
            done
            ;;
        1h30|1h30min|90min)
            elapsed=0
            while true; do
                h=$((start_hour + (elapsed / 60)))
                m=$((elapsed % 60))
                [[ $h -ge $end_hour ]] && break
                entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>${m}</integer></dict>\n"
                elapsed=$((elapsed + 90))
                [[ $h -ge $end_hour ]] && break
            done
            ;;
        2h|2hour)
            # Every 2 hours (0,2,4,... but only within range)
            for h in $(seq $start_hour 2 $((end_hour - 1))); do
                entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>0</integer></dict>\n"
            done
            ;;
        3h|3hour)
            # Every 3 hours (0,3,6,... but only within range)
            for h in $(seq $start_hour 3 $((end_hour - 1))); do
                entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>0</integer></dict>\n"
            done
            ;;
        4h|4hour)
            # Every 4 hours (0,4,8,... but only within range)
            for h in $(seq $start_hour 4 $((end_hour - 1))); do
                entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>0</integer></dict>\n"
            done
            ;;
        *)
            # Default: 30min interval within range
            for h in $(seq $start_hour $((end_hour - 1))); do
                for m in 0 30; do
                    entries="${entries}        <dict><key>Hour</key><integer>${h}</integer><key>Minute</key><integer>${m}</integer></dict>\n"
                done
            done
            ;;
    esac
    
    echo -e "$entries"
}


# Remove existing EliaAI launchd agents
remove_elia_agents() {
    # Search for ANY plist in LaunchAgents that references EliaAI scripts
    # This catches alternative naming conventions (agency.elia.*, etc.)
    for plist in "$LAUNCHD_DIR"/*.plist; do
        [[ -f "$plist" ]] || continue
        if grep -q "cron_wrapper.sh\|trigger_opencode\|trigger_morning.sh\|EliaAI/scripts" "$plist" 2>/dev/null; then
            local label=$(basename "$plist" .plist)
            launchctl unload "$plist" 2>/dev/null || true
            rm -f "$plist"
            log "Removed ElIA-related plist: $(basename "$plist")"
        fi
    done
    
    # Also remove known named plists directly (backward compat)
    for known_plist in "$LAUNCHD_PLIST" "$LAUNCHD_MORNING_PLIST"; do
        if [[ -f "$known_plist" ]]; then
            launchctl unload "$known_plist" 2>/dev/null || true
            rm -f "$known_plist"
        fi
    done
    
    # Clean up state
    rm -f "$STATE_FILE"
}

install_scheduler() {
    local interval="${1:-$DEFAULT_INTERVAL}"
    local start_hour="${2:-$DEFAULT_START_HOUR}"
    local end_hour="${3:-$DEFAULT_END_HOUR}"
    
    # Validate hours
    if [[ $start_hour -lt 0 || $start_hour -gt 23 ]]; then
        error "Start hour must be 0-23"
        return 1
    fi
    
    if [[ $end_hour -lt 0 || $end_hour -gt 23 ]]; then
        error "End hour must be 0-23"
        return 1
    fi
    
    if [[ $start_hour -ge $end_hour ]]; then
        error "Start hour must be before end hour"
        return 1
    fi
    
    # Remove existing first
    remove_elia_agents
    
    # Generate StartCalendarInterval based on start/end hours
    calendar_entries=$(generate_calendar_entries "$interval" "$start_hour" "$end_hour")

    # If scheduler is disabled, save state but do NOT write plist to LaunchAgents
    # This prevents auto-load on next login
    if [[ -f "$DISABLED_FLAG" ]]; then
        warning "Scheduler is DISABLED (${DISABLED_FLAG} exists) — plist NOT written to LaunchAgents."
        warning "Run './manage_cron.sh enable' to activate."
        save_state "$interval" "$start_hour" "$end_hour" "$DEFAULT_MORNING_HOUR" "false" "false"
        return 0
    fi

    # Ensure LaunchAgents directory exists
    mkdir -p "$LAUNCHD_DIR"
    
    # Build the plist with StartCalendarInterval (fixed times like cron)
    cat > "$LAUNCHD_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.elia-agent</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>${AGENT_DIR}/scripts/cron_wrapper.sh</string>
    </array>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>StartCalendarInterval</key>
    <array>
${calendar_entries}
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>~/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:~/.local/bin:~/.npm-global/bin:~/.nvm/versions/node/v20.20.2/bin</string>
        <key>HOME</key>
        <string>~</string>
        <key>USER</key>
        <string>yourusername</string>
        <key>NO_PROXY</key>
        <string>127.0.0.1,localhost,::1</string>
        <key>no_proxy</key>
        <string>127.0.0.1,localhost,::1</string>
    </dict>
    
    <key>WorkingDirectory</key>
    <string>${AGENT_DIR}</string>
    
    <key>StandardOutPath</key>
    <string>${AGENT_DIR}/logs/cron.log</string>
    
    <key>StandardErrorPath</key>
    <string>${AGENT_DIR}/logs/cron.log</string>
    
    <key>ProcessType</key>
    <string>Standard</string>
</dict>
</plist>
EOF
    
    # Backup to EliaAI folder
    cp "$LAUNCHD_PLIST" "$LOCAL_PLIST" 2>/dev/null || true

    # Load the agent
    launchctl load "$LAUNCHD_PLIST"

    success "Scheduler installed (every ${interval})"
    case "$interval" in
        20min) log "Schedule: runs at :00, :20, :40 every hour within range" ;;
        30min|30minute) log "Schedule: runs at :00 and :30 every hour within range" ;;
        *) log "Schedule: runs at :00 every interval within range" ;;
    esac
    log "Hours: ${start_hour}:00 - ${end_hour}:00"
    
    # Save state
    save_state "$interval" "$start_hour" "$end_hour" "$DEFAULT_MORNING_HOUR" "true" "false"
}

install_morning_scheduler() {
    local morning_hour="${1:-$DEFAULT_MORNING_HOUR}"
    
    if [[ $morning_hour -lt 0 || $morning_hour -gt 23 ]]; then
        error "Morning hour must be 0-23"
        return 1
    fi
    
    # Load existing state if present
    load_state
    
    # If scheduler is disabled, save state but do NOT write plist to LaunchAgents
    if [[ -f "$DISABLED_FLAG" ]]; then
        warning "Scheduler is DISABLED (${DISABLED_FLAG} exists) — morning plist NOT written to LaunchAgents."
        warning "Run './manage_cron.sh enable' to activate."
        local current_interval="${interval:-${DEFAULT_INTERVAL}}"
        local current_start="${startHour:-${DEFAULT_START_HOUR}}"
        local current_end="${endHour:-${DEFAULT_END_HOUR}}"
        save_state "$current_interval" "$current_start" "$current_end" "$morning_hour" "false" "false"
        return 0
    fi
    
    # Remove existing morning agent first
    if [[ -f "$LAUNCHD_MORNING_PLIST" ]]; then
        launchctl unload "$LAUNCHD_MORNING_PLIST" 2>/dev/null || true
        rm -f "$LAUNCHD_MORNING_PLIST"
    fi
    
    # Ensure LaunchAgents directory exists
    mkdir -p "$LAUNCHD_DIR"
    
    # Build the morning plist content
    cat > "$LAUNCHD_MORNING_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elia.elia-agent-morning</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>${AGENT_DIR}/scripts/trigger_morning.sh</string>
    </array>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>${morning_hour}</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>~/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:~/.local/bin:~/.npm-global/bin:~/.nvm/versions/node/v20.20.2/bin</string>
        <key>HOME</key>
        <string>~</string>
        <key>USER</key>
        <string>yourusername</string>
        <key>NO_PROXY</key>
        <string>127.0.0.1,localhost,::1</string>
        <key>no_proxy</key>
        <string>127.0.0.1,localhost,::1</string>
    </dict>
    
    <key>WorkingDirectory</key>
    <string>${AGENT_DIR}</string>
    
    <key>StandardOutPath</key>
    <string>${AGENT_DIR}/logs/cron_morning.log</string>
    
    <key>StandardErrorPath</key>
    <string>${AGENT_DIR}/logs/cron_morning.log</string>
    
    <key>ProcessType</key>
    <string>Standard</string>
</dict>
</plist>
EOF
    
    # Load the agent
    launchctl load "$LAUNCHD_MORNING_PLIST"

    # Backup to EliaAI folder
    cp "$LAUNCHD_MORNING_PLIST" "$LOCAL_MORNING_PLIST" 2>/dev/null || true
    
    success "Morning scheduler installed (daily at ${morning_hour}:00)"
    log "Schedule: Daily at ${morning_hour}:00"
    
    # Save state (preserve existing if present)
    local current_interval="${interval:-${DEFAULT_INTERVAL}}"
    local current_start="${startHour:-${DEFAULT_START_HOUR}}"
    local current_end="${endHour:-${DEFAULT_END_HOUR}}"
    save_state "$current_interval" "$current_start" "$current_end" "$morning_hour" "${enabled:-false}" "true"
}

disable_scheduler() {
    if [[ -f "$LAUNCHD_PLIST" ]]; then
        launchctl unload "$LAUNCHD_PLIST" 2>/dev/null || true
        rm -f "$LAUNCHD_PLIST"
        log "Unloaded and removed standard launchd plist"
    fi
    if [[ -f "$LAUNCHD_MORNING_PLIST" ]]; then
        launchctl unload "$LAUNCHD_MORNING_PLIST" 2>/dev/null || true
        rm -f "$LAUNCHD_MORNING_PLIST"
        log "Unloaded and removed morning launchd plist"
    fi
    # Kill any currently running agent sessions started by the scheduler
    log "Killing any running agent sessions..."
    pkill -f "trigger_opencode_interactive" 2>/dev/null || true
    pkill -f "trigger_morning.sh" 2>/dev/null || true
    pkill -f "start_agents.sh" 2>/dev/null || true
    pkill -f "cron_wrapper.sh" 2>/dev/null || true
    pkill -f "oh-my-opencode.*run" 2>/dev/null || true
    pkill -f "ralph-loop" 2>/dev/null || true
    # Kill any Elia agent sessions started outside the scheduler
    pkill -f "opencode run.*elia" 2>/dev/null || true
    sleep 1
    touch "$DISABLED_FLAG"
    log "Disabled flag created: ${DISABLED_FLAG}"
    load_state
    local current_interval="${interval:-${DEFAULT_INTERVAL}}"
    local current_start="${startHour:-${DEFAULT_START_HOUR}}"
    local current_end="${endHour:-${DEFAULT_END_HOUR}}"
    local current_morning="${morningHour:-${DEFAULT_MORNING_HOUR}}"
    save_state "$current_interval" "$current_start" "$current_end" "$current_morning" "false" "false"
    success "Scheduler disabled (all agents killed, settings preserved for re-enable)"
}

enable_scheduler() {
    rm -f "$DISABLED_FLAG"
    log "Disabled flag removed"
    load_state
    local current_interval="${interval:-${DEFAULT_INTERVAL}}"
    local current_start="${startHour:-${DEFAULT_START_HOUR}}"
    local current_end="${endHour:-${DEFAULT_END_HOUR}}"
    local current_morning="${morningHour:-${DEFAULT_MORNING_HOUR}}"
    install_scheduler "$current_interval" "$current_start" "$current_end"
    install_morning_scheduler "$current_morning"
    success "Scheduler enabled (plists reloaded)"
}

show_schedulers() {
    echo "=========================================="
    echo "EliaAI Schedulers (launchd)"
    echo "=========================================="
    echo ""
    
    if [[ -f "$DISABLED_FLAG" ]]; then
        echo -e "${YELLOW}⏹  SCHEDULER DISABLED${NC} (remove .scheduler_disabled to re-enable)"
        echo ""
    fi

    # Check standard agent
    if [[ -f "$LAUNCHD_PLIST" ]]; then
        echo "Standard Agent: INSTALLED"
        launchctl list | grep "com.elia.elia-agent" && echo "Status: RUNNING" || echo "Status: NOT RUNNING"
    else
        echo "Standard Agent: NOT INSTALLED"
    fi
    echo ""
    
    # Check morning agent
    if [[ -f "$LAUNCHD_MORNING_PLIST" ]]; then
        echo "Morning Agent: INSTALLED"
        launchctl list | grep "com.elia.elia-agent-morning" && echo "Status: RUNNING" || echo "Status: NOT RUNNING"
    else
        echo "Morning Agent: NOT INSTALLED"
    fi
    echo ""
    
    # Show state file if exists
    if [[ -f "$STATE_FILE" ]]; then
        echo "=========================================="
        echo "Current Settings:"
        echo "=========================================="
        cat "$STATE_FILE"
    fi
    echo ""
}

uninstall_scheduler() {
    remove_elia_agents
    success "All EliaAI schedulers removed"
}

uninstall_morning_scheduler() {
    if [[ -f "$LAUNCHD_MORNING_PLIST" ]]; then
        launchctl unload "$LAUNCHD_MORNING_PLIST" 2>/dev/null || true
        rm -f "$LAUNCHD_MORNING_PLIST"
        log "Removed morning launchd agent"
    fi
    
    # Update state
    load_state
    local current_interval="${interval:-${DEFAULT_INTERVAL}}"
    local current_start="${startHour:-${DEFAULT_START_HOUR}}"
    local current_end="${endHour:-${DEFAULT_END_HOUR}}"
    save_state "$current_interval" "$current_start" "$current_end" "${morningHour:-${DEFAULT_MORNING_HOUR}}" "${enabled:-false}" "false"
    
    success "Morning scheduler removed"
}

# Main script logic
main() {
    local command="${1:-}"
    
    # Parse command
    case "$command" in
        install)
            shift
            local interval="$DEFAULT_INTERVAL"
            local start_hour="$DEFAULT_START_HOUR"
            local end_hour="$DEFAULT_END_HOUR"
            
            # Parse options
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --interval)
                        interval="$2"
                        shift 2
                        ;;
                    --start)
                        start_hour="$2"
                        shift 2
                        ;;
                    --end)
                        end_hour="$2"
                        shift 2
                        ;;
                    --sudo)
                        USE_SUDO=true
                        shift
                        ;;
                    --proxy)
                        USE_PROXY=true
                        shift
                        ;;
                    --help)
                        show_usage
                        exit 0
                        ;;
                    *)
                        error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                esac
            done
            
            install_scheduler "$interval" "$start_hour" "$end_hour"
            ;;
            
        install-morning)
            shift
            local morning_hour="$DEFAULT_MORNING_HOUR"
            
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --morning-hour)
                        morning_hour="$2"
                        shift 2
                        ;;
                    --sudo)
                        USE_SUDO=true
                        shift
                        ;;
                    --proxy)
                        USE_PROXY=true
                        shift
                        ;;
                    --help)
                        show_usage
                        exit 0
                        ;;
                    *)
                        error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                esac
            done
            
            install_morning_scheduler "$morning_hour"
            ;;
            
        disable)
            shift
            disable_scheduler
            ;;

        enable)
            shift
            enable_scheduler
            ;;

        uninstall|remove|delete|stop)
            shift
            uninstall_scheduler
            ;;
            
        uninstall-morning)
            shift
            uninstall_morning_scheduler
            ;;
            
        show|list|status)
            shift
            show_schedulers
            ;;
            
        --help|-h|help)
            show_usage
            exit 0
            ;;
            
        "")
            error "No command specified"
            show_usage
            exit 1
            ;;
            
        *)
            error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
