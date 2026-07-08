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
  uninstall       Remove all EliaAI schedulers
  uninstall-morning Remove only morning scheduler
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
        2h|2hour) echo "7200" ;;
        3h|3hour) echo "10800" ;;
        4h|4hour) echo "14400" ;;
        *) echo "3600" ;;  # default 1h
    esac
}

# Remove existing EliaAI launchd agents
remove_elia_agents() {
    # Unload and remove standard agent
    if [[ -f "$LAUNCHD_PLIST" ]]; then
        launchctl unload "$LAUNCHD_PLIST" 2>/dev/null || true
        rm -f "$LAUNCHD_PLIST"
        log "Removed standard launchd agent"
    fi
    
    # Unload and remove morning agent
    if [[ -f "$LAUNCHD_MORNING_PLIST" ]]; then
        launchctl unload "$LAUNCHD_MORNING_PLIST" 2>/dev/null || true
        rm -f "$LAUNCHD_MORNING_PLIST"
        log "Removed morning launchd agent"
    fi
    
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
    
    # Ensure LaunchAgents directory exists
    mkdir -p "$LAUNCHD_DIR"
    
    # Generate StartCalendarInterval based on interval (fixed times like cron)
    local calendar_entries=""
    case "$interval" in
        20min)
            calendar_entries="        <dict><key>Minute</key><integer>0</integer></dict>
        <dict><key>Minute</key><integer>20</integer></dict>
        <dict><key>Minute</key><integer>40</integer></dict>"
            ;;
        30min|30minute)
            calendar_entries="        <dict><key>Minute</key><integer>0</integer></dict>
        <dict><key>Minute</key><integer>30</integer></dict>"
            ;;
        1h|1hour|hourly)
            calendar_entries="        <dict><key>Minute</key><integer>0</integer></dict>"
            ;;
        2h|2hour)
            calendar_entries="        <dict><key>Hour</key><integer>0</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>2</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>4</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>22</integer><key>Minute</key><integer>0</integer></dict>"
            ;;
        3h|3hour)
            calendar_entries="        <dict><key>Hour</key><integer>0</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>6</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>21</integer><key>Minute</key><integer>0</integer></dict>"
            ;;
        4h|4hour)
            calendar_entries="        <dict><key>Hour</key><integer>0</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>4</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>"
            ;;
        *)
            calendar_entries="        <dict><key>Minute</key><integer>0</integer></dict>
        <dict><key>Minute</key><integer>30</integer></dict>"
            ;;
    esac
    
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
    <true/>
    
    <key>StartCalendarInterval</key>
    <array>
${calendar_entries}
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/vakandi/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/vakandi/.local/bin:/Users/vakandi/.npm-global/bin:/Users/vakandi/.nvm/versions/node/v20.20.2/bin</string>
        <key>HOME</key>
        <string>/Users/vakandi</string>
        <key>USER</key>
        <string>vakandi</string>
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
    
    # Load the agent
    launchctl load "$LAUNCHD_PLIST"

    # Backup to EliaAI folder
    cp "$LAUNCHD_PLIST" "$LOCAL_PLIST" 2>/dev/null || true

    success "Scheduler installed (every ${interval})"
    log "Schedule: runs at :00 and :30 every hour (fixed times)"
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
        <string>/Users/vakandi/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/vakandi/.local/bin:/Users/vakandi/.npm-global/bin:/Users/vakandi/.nvm/versions/node/v20.20.2/bin</string>
        <key>HOME</key>
        <string>/Users/vakandi</string>
        <key>USER</key>
        <string>vakandi</string>
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

show_schedulers() {
    echo "=========================================="
    echo "EliaAI Schedulers (launchd)"
    echo "=========================================="
    echo ""
    
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
