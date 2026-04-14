#!/bin/zsh
# Helper functions for AI Agent
# Location: helpers.sh

# Dynamic path detection - can be overridden by sourcing script
if [[ -z "${AGENT_DIR:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    AGENT_DIR="$(dirname "$SCRIPT_DIR")"
fi

# Safe PATH for cron environment (includes nvm, homebrew, npm globals, and local bin)
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.nvm/versions/node/current/bin"

# Also source nvm if available to get proper node env
if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
    source "$HOME/.nvm/nvm.sh" 2>/dev/null || true
fi

# ============================================
# AI BACKEND SELECTOR
# Set to: "copilot", "gemini", or "kiro"
# Can also be overridden via env: AI_BACKEND=kiro ./run_agent.sh
# ============================================
AI_BACKEND="${AI_BACKEND:-gemini}"

# Logging
LOG_FILE="${AGENT_DIR}/logs/output.log"

log_info() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"
    echo "$msg" | tee -a "$LOG_FILE" >&1
}

log_warn() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] WARN: $1"
    echo "$msg" | tee -a "$LOG_FILE" >&2
}

log_error() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1"
    echo "$msg" | tee -a "$LOG_FILE" >&2
}

# Lock file handling with long-running agent detection
acquire_lock_or_exit() {
    local lockfile="${AGENT_DIR}/.agent.lock"
    if [[ -f "$lockfile" ]]; then
        local pid
        pid=$(cat "$lockfile" 2>/dev/null) || pid=""
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            # Check how long the process has been running
            local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null | xargs -I {} date -j -f "%a %b %d %H:%M:%S %Y" "{}" +%s 2>/dev/null || echo "0")
            local current_time=$(date +%s)
            local runtime=$((current_time - start_time))
            
            # If running for more than 45 minutes (likely 1 hour of work)
            if [[ $runtime -gt 2700 ]]; then
                log_warn "Previous agent still running after ~$((runtime/60)) minutes (PID: $pid)"
                
                # Send macOS notification
                osascript -e 'display notification "Previous hour agent still running - capturing work output" with title "🤖 Mycroft Agent" sound name "Frog"' 2>/dev/null || true
                
                # Capture recent work from logs
                local recent_work=$(tail -200 "$OUTPUT_LOG" 2>/dev/null | grep -E "(Worker|completed|TASK|DONE|FIXED|wrote|edited|created|edit|write|fix|bug|code|file)" | tail -50)
                
                # Save work summary for analyzer
                local analyzer_input="${AGENT_DIR}/.agent_payloads/work_to_analyze_${pid}.txt"
                mkdir -p "${AGENT_DIR}/.agent_payloads"
                cat > "$analyzer_input" << EOF
=== WORK FROM LONG-RUNNING AGENT (PID: $pid) ===
Runtime: $((runtime/60)) minutes
Started: $(date -r $start_time '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "unknown")
Log File: $OUTPUT_LOG

LOG EXCERPT (last 200 lines filtered):
${recent_work:-"(No explicit work markers in logs - check full log)"}

FULL LOG SNIPPET (last 100 lines):
$(tail -100 "$OUTPUT_LOG" 2>/dev/null)

=== END WORK CAPTURE ===

Your task: Analyze what work was accomplished and send a summary.

⚠️ IMPORTANT - Telegram vs Discord for reports:
- Discord #reports (ELIA-HQ) = Regular reports (default)
- Telegram send_msg_to_default_group = URGENT/blockers only (Wael needs to fix ASAP for next runs)
EOF
                
                log_info "Spawning analyzer agent to summarize $((runtime/60)) minutes of work..."
                
                # Spawn analyzer agent in background to analyze work and send to Telegram
                (
                    cd "$AGENT_DIR"
                    # Use gemini to spawn analyzer agent which will read the file and send Telegram report
                    gemini /spawn analyzer "Read the analysis file at $analyzer_input and:
1. Identify what tasks were completed by the long-running agent
2. List specific files edited/created
3. Note what remains incomplete  
4. Send a detailed summary. For regular reports → use Discord #reports (ELIA-HQ). For urgent/blockers → use Telegram send_msg_to_default_group.

The runtime was $((runtime/60)) minutes - this is significant work that must be captured." 2>&1 >> "$OUTPUT_LOG"
                ) &
                local analyzer_pid=$!
                
                # Quick ntfy notification that analyzer is running
                curl -s -d "🤖 Analyzer spawned for $((runtime/60))min work (PID: $analyzer_pid)" ntfy.sh/AITeamHelper > /dev/null 2>&1 || true
                
                log_info "Analyzer agent spawned (PID: $analyzer_pid) to process work output"
            fi
            
            log_warn "Another agent instance is running (PID: $pid). Exiting."
            exit 0
        else
            log_warn "Stale lock file found. Removing..."
            rm -f "$lockfile"
        fi
    fi
    echo $$ > "$lockfile"
}

# Error handling
exit_with_error() {
    log_error "$1"
    exit 1
}

# Directory creation
ensure_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || exit_with_error "Failed to create directory: $dir"
    fi
}

# Rotate log file if it exceeds max_mb (prevents OOM and read_file 20MB limit)
# Usage: rotate_log_if_needed /path/to/log.log 20
rotate_log_if_needed() {
    local logpath="$1"
    local max_mb="${2:-20}"
    [[ -z "$logpath" ]] && return 0
    [[ ! -f "$logpath" ]] && return 0
    local size_bytes
    size_bytes=$(stat -f%z "$logpath" 2>/dev/null || stat -c%s "$logpath" 2>/dev/null || echo "0")
    local max_bytes=$((max_mb * 1024 * 1024))
    if [[ -n "$size_bytes" && $size_bytes -gt $max_bytes ]]; then
        local rotated="${logpath}.old.$(date +%Y%m%d_%H%M%S)"
        mv "$logpath" "$rotated" 2>/dev/null && touch "$logpath" && echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: Rotated log (was ${size_bytes} bytes) to $rotated" >> "$logpath"
    fi
}

# Dependency checks
check_gh_installed() {
    if ! command -v gh &>/dev/null; then
        return 1
    fi
    return 0
}

check_gh_copilot() {
    if ! gh copilot --help &>/dev/null 2>&1; then
        return 1
    fi
    # Check authentication - either GH_TOKEN env var or gh auth status
    if [[ -n "${GH_TOKEN:-}" ]]; then
        return 0  # GH_TOKEN is set, auth is valid
    fi
    if ! gh auth status &>/dev/null 2>&1; then
        return 1
    fi
    return 0
}

check_gemini_installed() {
    # Try PATH first
    if command -v gemini &>/dev/null; then
        return 0
    fi
    # Check common npm global locations
    local npm_global
    npm_global=$(npm root -g 2>/dev/null || echo "")
    if [[ -x "${npm_global}/../bin/gemini" ]]; then
        export PATH="${npm_global}/../bin:$PATH"
        return 0
    fi
    # Check nvm-managed node
    for nvmbin in /Users/$(whoami)/.nvm/versions/node/*/bin/gemini; do
        if [[ -x "$nvmbin" ]]; then
            export PATH="$(dirname "$nvmbin"):$PATH"
            return 0
        fi
    done
    return 1
}

check_gemini_auth() {
    # If API key is set, consider authenticated
    if [[ -n "${GEMINI_API_KEY:-}" ]]; then
        return 0
    fi
    # Try running gemini --version as a lightweight check
    if gemini --version &>/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# ============================================
# AI BACKEND VALIDATION & EXECUTION
# ============================================

# Check if Kiro CLI is installed - search in nvm and npm global locations
check_kiro_installed() {
    # Try PATH first
    if command -v kiro-cli &>/dev/null; then
        return 0
    fi
    # Check common npm global locations
    local npm_global
    npm_global=$(npm root -g 2>/dev/null || echo "")
    if [[ -x "${npm_global}/../bin/kiro-cli" ]]; then
        export PATH="${npm_global}/../bin:$PATH"
        return 0
    fi
    # Check nvm-managed node
    for nvmbin in /Users/$(whoami)/.nvm/versions/node/*/bin/kiro-cli; do
        if [[ -x "$nvmbin" ]]; then
            export PATH="$(dirname "$nvmbin"):$PATH"
            return 0
        fi
    done
    # Check common locations
    for loc in "$HOME/.local/bin/kiro-cli" "/opt/homebrew/bin/kiro-cli" "/usr/local/bin/kiro-cli"; do
        if [[ -x "$loc" ]]; then
            export PATH="$(dirname "$loc"):$PATH"
            return 0
        fi
    done
    return 1
}

# Validate the configured AI backend is installed and authenticated
check_ai_backend() {
    case "$AI_BACKEND" in
        copilot)
            if ! check_gh_installed; then
                log_error "GitHub CLI (gh) not found. Install: brew install gh"
                return 1
            fi
            if ! check_gh_copilot; then
                log_error "GitHub Copilot CLI not authenticated. Set GH_TOKEN or run: gh auth login"
                return 1
            fi
            log_info "AI Backend: GitHub Copilot CLI (gh copilot)"
            return 0
            ;;
        gemini)
            if ! check_gemini_installed; then
                log_error "Gemini CLI not found. Install: npm install -g @google/gemini-cli"
                return 1
            fi
            if ! check_gemini_auth; then
                log_error "Gemini CLI not authenticated. Set GEMINI_API_KEY or run: gemini (for browser login)"
                return 1
            fi
            log_info "AI Backend: Gemini CLI (gemini)"
            return 0
            ;;
        kiro)
            if ! check_kiro_installed; then
                log_error "Kiro CLI not found. Install: npm install -g @kiroai/cli"
                return 1
            fi
            log_info "AI Backend: Kiro CLI (kiro-cli)"
            return 0
            ;;
        *)
            log_error "Unknown AI_BACKEND='$AI_BACKEND'. Valid options: copilot, gemini, kiro"
            return 1
            ;;
    esac
}

# Execute AI with the configured backend
# Usage: run_ai "<prompt_or_payload>" "<output_log_path>"
run_ai() {
    local payload="$1"
    local output_log="$2"

    case "$AI_BACKEND" in
        copilot)
            log_info "Executing via GitHub Copilot CLI..."
            if gh copilot -p "$payload" --allow-all >> "$output_log" 2>&1; then
                log_info "GitHub Copilot execution completed successfully"
                return 0
            else
                local exit_code=$?
                log_error "GitHub Copilot execution failed (exit code: $exit_code)"
                return $exit_code
            fi
            ;;
        gemini)
            log_info "Executing via Gemini CLI..."
            if gemini -p "$payload" >> "$output_log" 2>&1; then
                log_info "Gemini execution completed successfully"
                return 0
            else
                local exit_code=$?
                log_error "Gemini execution failed (exit code: $exit_code)"
                return $exit_code
            fi
            ;;
        kiro)
            log_info "Executing via Kiro CLI (agent: elia)..."
            local temp_input="$(mktemp "${AGENT_DIR:-/tmp}/.kiro_input.XXXXXX")"
            echo "$payload" > "$temp_input"
            # Use --agent elia and --trust-all-tools to auto-approve
            if kiro-cli chat --agent elia --trust-all-tools < "$temp_input" >> "$output_log" 2>&1; then
                rm -f "$temp_input"
                log_info "Kiro execution completed successfully"
                return 0
            else
                local exit_code=$?
                rm -f "$temp_input"
                log_error "Kiro execution failed (exit code: $exit_code)"
                return $exit_code
            fi
            ;;
        *)
            log_error "Unknown AI_BACKEND='$AI_BACKEND' in run_ai()"
            return 1
            ;;
    esac
}

# Kill any running AI CLI processes (used to clear stale processes)
kill_ai_processes() {
    local killed=0
    case "$AI_BACKEND" in
        copilot)
            local pids
            pids=$(pgrep -f "gh copilot" 2>/dev/null || true)
            if [[ -n "$pids" ]]; then
                echo "$pids" | xargs kill -9 2>/dev/null && killed=1
                log_warn "Killed stale gh copilot processes: $pids"
            fi
            ;;
        gemini)
            local pids
            pids=$(pgrep -f "gemini -p" 2>/dev/null || true)
            if [[ -n "$pids" ]]; then
                echo "$pids" | xargs kill -9 2>/dev/null && killed=1
                log_warn "Killed stale gemini processes: $pids"
            fi
            ;;
        kiro)
            local pids
            pids=$(pgrep -f "kiro-cli" 2>/dev/null || true)
            if [[ -n "$pids" ]]; then
                echo "$pids" | xargs kill -9 2>/dev/null && killed=1
                log_warn "Killed stale kiro-cli processes: $pids"
            fi
            ;;
    esac
    return 0
}

# Safe file reading - only readable text files
is_text_file() {
    local file="$1"
    # Check if it's a regular file (not symlink, socket, etc.)
    [[ -f "$file" ]] || return 1
    # Check if readable
    [[ -r "$file" ]] || return 1
    # Skip hidden files, binaries, and known non-text extensions
    local ext="${file##*.}"
    ext="${ext:l}"  # lowercase
    case "$ext" in
        bin|exe|dll|so|dylib|o|a|obj|zip|tar|gz|rar|7z|jpg|jpeg|png|gif|bmp|ico|mp3|mp4|avi|mov|pdf|doc|docx|xls|xlsx|ppt|pptx|dmg|pkg|app|DS_Store)
            return 1
            ;;
    esac
    # Check MIME type if file command available
    if command -v file &>/dev/null; then
        local mime
        mime=$(file -b --mime-type "$file" 2>/dev/null)
        case "$mime" in
            text/*|application/json|application/xml|application/javascript|application/ecmascript|application/x-sh|application/x-shellscript|application/x-zsh|application/x-python-code|application/x-ruby|application/x-perl|application/x-yaml|application/toml)
                return 0
                ;;
            inode/directory)
                return 1
                ;;
            *)
                # For unknown types, allow if no null bytes in first 1KB
                if head -c 1024 "$file" 2>/dev/null | grep -qP '\x00'; then
                    return 1
                fi
                return 0
                ;;
        esac
    fi
    return 0
}

# Recursively gather context from directory
gather_context() {
    local context_dir="$1"
    local count=0
    
    echo "# === CONTEXT FILES ==="
    echo "# Source: $context_dir"
    echo ""
    
    # Find all readable text files recursively
    while IFS= read -r -d '' file; do
        if is_text_file "$file"; then
            local rel_path="${file#$context_dir/}"
            echo ""
            echo "# --- File: $rel_path ---"
            echo "# Path: $file"
            echo ""
            cat "$file" 2>/dev/null || echo "# [Error reading file: $file]"
            ((count++))
        fi
    done < <(find "$context_dir" -type f -print0 2>/dev/null)
    
    echo ""
    echo "# --- End of Context ($count files processed) ---"
    echo ""
    
    if [[ $count -eq 0 ]]; then
        echo "# WARNING: No readable text files found in context directory"
    fi
}

# Check if cron job exists
check_cron_job() {
    local cron_entry="$1"
    crontab -l 2>/dev/null | grep -F "$cron_entry" &>/dev/null
}

# Install cron job (idempotent)
install_cron_job() {
    local cron_entry="$1"
    local current_crontab
    
    # Get current crontab
    current_crontab=$(crontab -l 2>/dev/null || echo "")
    
    # Check if already exists
    if echo "$current_crontab" | grep -F "$cron_entry" &>/dev/null; then
        echo "Cron job already installed."
        return 0
    fi
    
    # Add new cron job
    (
        echo "$current_crontab"
        echo "# AI Agent - runs every 20 minutes"
        echo "$cron_entry"
    ) | crontab -
    
    echo "Cron job installed successfully."
}

# Remove cron job
remove_cron_job() {
    local pattern="$1"
    local current_crontab
    
    current_crontab=$(crontab -l 2>/dev/null || echo "")
    
    if echo "$current_crontab" | grep -F "$pattern" &>/dev/null; then
        echo "$current_crontab" | grep -vF "$pattern" | crontab -
        echo "Cron job removed."
    else
        echo "No matching cron job found."
    fi
}

# Get last execution info
get_last_execution() {
    local log_file="$1"
    if [[ -f "$log_file" ]]; then
        grep "AGENT EXECUTION" "$log_file" | tail -2
    fi
}

# Get last N log lines
get_recent_logs() {
    local log_file="$1"
    local n="${2:-10}"
    if [[ -f "$log_file" ]]; then
        tail -n "$n" "$log_file" 2>/dev/null
    fi
}

# ============================================
# MESSAGING & MONITORING HELPERS
# ============================================

# Work-related keywords for detecting actionable messages
WORK_KEYWORDS=("urgent" "asap" "deadline" "meeting" "call" "review" "need you" "can you" "please" "task" "project" "deliverable" "client" "boss" "team" "update" "status" "report")

# Check if a message contains work-related keywords
is_work_related() {
    local message="$1"
    local lower_msg="${message:l}"
    for keyword in "${WORK_KEYWORDS[@]}"; do
        if [[ "$lower_msg" == *"$keyword"* ]]; then
            return 0  # Work-related
        fi
    done
    return 1  # Not work-related
}

# Get timestamp 40 minutes ago in ISO format
get_40min_ago() {
    date -u -v-40M '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u --date='40 minutes ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null
}

# Format timestamp for MCP calls
format_mcp_timestamp() {
    # Returns ISO 8601 format accepted by MCP tools
    date -u '+%Y-%m-%dT%H:%M:%SZ'
}

# ============================================
# APPROVAL SYSTEM HELPERS
# ============================================

# Queue file for pending approvals
APPROVAL_QUEUE="${AGENT_DIR}/.approval_queue"

# Add a message to the approval queue
queue_for_approval() {
    local platform="$1"  # whatsapp, discord, etc.
    local recipient="$2"
    local message="$3"
    local context="$4"   # Original message that triggered this
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local id
    id="$(date +%s)_$RANDOM"
    
    # Save to queue file
    echo "---" >> "$APPROVAL_QUEUE"
    echo "ID: $id" >> "$APPROVAL_QUEUE"
    echo "TIMESTAMP: $timestamp" >> "$APPROVAL_QUEUE"
    echo "PLATFORM: $platform" >> "$APPROVAL_QUEUE"
    echo "RECIPIENT: $recipient" >> "$APPROVAL_QUEUE"
    echo "MESSAGE: $message" >> "$APPROVAL_QUEUE"
    echo "CONTEXT: $context" >> "$APPROVAL_QUEUE"
    echo "STATUS: PENDING" >> "$APPROVAL_QUEUE"
    echo "" >> "$APPROVAL_QUEUE"
    
    log_info "Queued message for approval [ID: $id] - $platform to $recipient"
    echo "$id"
}

# Get count of pending approvals
get_pending_count() {
    if [[ -f "$APPROVAL_QUEUE" ]]; then
        grep -c "STATUS: PENDING" "$APPROVAL_QUEUE" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Mark approval as sent/completed
mark_approved_sent() {
    local id="$1"
    local temp_file="${APPROVAL_QUEUE}.tmp"
    
    if [[ -f "$APPROVAL_QUEUE" ]]; then
        sed "s/^ID: $id$/{&}/; /{ID: $id}/,/STATUS: PENDING/{s/STATUS: PENDING/STATUS: SENT/}; s/{ID: $id}/ID: $id/" "$APPROVAL_QUEUE" > "$temp_file" && mv "$temp_file" "$APPROVAL_QUEUE"
    fi
}

# Mark approval as rejected
mark_rejected() {
    local id="$1"
    local temp_file="${APPROVAL_QUEUE}.tmp"
    
    if [[ -f "$APPROVAL_QUEUE" ]]; then
        sed "s/^ID: $id$/{&}/; /{ID: $id}/,/STATUS: PENDING/{s/STATUS: PENDING/STATUS: REJECTED/}; s/{ID: $id}/ID: $id/" "$APPROVAL_QUEUE" > "$temp_file" && mv "$temp_file" "$APPROVAL_QUEUE"
    fi
}

# ============================================
# MCP READINESS HELPERS
# ============================================

# Wait for MCP servers to be ready via MCP Manager
wait_for_mcp_ready() {
    local max_wait=30  # Maximum seconds to wait
    local interval=2   # Check every 2 seconds
    local waited=0
    
    log_info "Waiting for MCP servers to initialize..."
    
    # First, ensure MCP Manager is running
    if ! check_mcp_manager; then
        log_info "MCP Manager not running, attempting to start..."
        start_mcp_manager
    fi
    
    # Check MCP Manager status via API
    while [[ $waited -lt $max_wait ]]; do
        if check_mcp_manager; then
            # Get status of critical MCP servers
            local whatsapp_status=$(get_mcp_server_status "whatsapp" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            local discord_status=$(get_mcp_server_status "discord-mcp" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            local telegram_status=$(get_mcp_server_status "telegram" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            
            # Log status every 5 seconds
            if [[ $((waited % 5)) -eq 0 && $waited -gt 0 ]]; then
                log_info "MCP wait: ${waited}s elapsed (WhatsApp: ${whatsapp_status:-unknown}, Discord: ${discord_status:-unknown}, Telegram: ${telegram_status:-unknown})"
            fi
            
            # Check if critical servers are running
            local running_count=0
            [[ "$whatsapp_status" == "running" ]] && ((running_count++))
            [[ "$discord_status" == "running" ]] && ((running_count++))
            [[ "$telegram_status" == "running" ]] && ((running_count++))
            
            # Minimum wait of 5 seconds, then proceed if at least 1 server is running
            if [[ $waited -ge 5 && $running_count -ge 1 ]]; then
                log_info "MCP servers ready after ${waited}s ($running_count servers running)"
                return 0
            fi
        fi
        
        sleep $interval
        ((waited+=interval))
    done
    
    log_warn "MCP readiness timeout after ${max_wait}s, proceeding anyway..."
    return 0  # Don't fail, just warn
}

AGENT_OUTPUT_DIR="${AGENT_DIR}/output"

# ============================================
# MCP MANAGER INTEGRATION
# ============================================

MCP_MANAGER_URL="${MCP_MANAGER_URL:-http://localhost:7243}"
MCP_MANAGER_DIR="${AGENT_DIR}/mcp_manager"

# Check if MCP Manager is running
check_mcp_manager() {
    if curl -s "${MCP_MANAGER_URL}/status" &>/dev/null; then
        return 0
    fi
    return 1
}

# Start MCP Manager if not running
start_mcp_manager() {
    log_info "Starting MCP Manager..."
    
    # Find node binary - try multiple methods
    local NODE_BIN=""
    if command -v node &>/dev/null; then
        NODE_BIN="$(command -v node)"
    elif [[ -x "/Users/vakandi/.nvm/versions/node/v24.13.1/bin/node" ]]; then
        NODE_BIN="/Users/vakandi/.nvm/versions/node/v24.13.1/bin/node"
    elif [[ -x "/opt/homebrew/bin/node" ]]; then
        NODE_BIN="/opt/homebrew/bin/node"
    elif [[ -x "/usr/local/bin/node" ]]; then
        NODE_BIN="/usr/local/bin/node"
    else
        # Last resort - find it
        NODE_BIN="$(find /Users/vakandi/.nvm -name node -type f 2>/dev/null | head -1)"
    fi
    
    if [[ -z "$NODE_BIN" ]] || [[ ! -x "$NODE_BIN" ]]; then
        log_error "Node binary not found!"
        return 1
    fi
    
    log_info "Using node: $NODE_BIN"
    
    if [[ -d "$MCP_MANAGER_DIR" ]]; then
        cd "$MCP_MANAGER_DIR"
        export PATH="$(dirname "$NODE_BIN"):$PATH"
        nohup "$NODE_BIN" index.js > /tmp/mcp-manager.log 2>&1 &
        sleep 5
        
        if check_mcp_manager; then
            log_info "MCP Manager started successfully"
            return 0
        else
            log_warn "MCP Manager failed to start"
            # Show error from log
            if [[ -f /tmp/mcp-manager.log ]]; then
                tail -5 /tmp/mcp-manager.log | while read line; do log_warn "$line"; done
            fi
            return 1
        fi
    else
        log_error "MCP Manager directory not found: $MCP_MANAGER_DIR"
        return 1
    fi
}

# Get MCP server status via Manager API
get_mcp_server_status() {
    local server_name="$1"
    
    local response
    response=$(curl -s "${MCP_MANAGER_URL}/status/${server_name}" 2>/dev/null || echo '{"status":"unknown"}')
    echo "$response"
}

# Call MCP tool via Manager API
mcp_call_tool() {
    local server_name="$1"
    local tool_name="$2"
    local params="${3:-{}}"
    
    log_info "MCP: Calling ${server_name}.${tool_name}..."
    
    local response
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"server\":\"$server_name\",\"tool\":\"$tool_name\",\"params\":$params}" \
        "${MCP_MANAGER_URL}/call" 2>/dev/null || echo '{"error":"MCP Manager API call failed"}')
    
    echo "$response"
}

# WhatsApp MCP wrappers using Manager
mcp_whatsapp_search_contacts() {
    local query="$1"
    mcp_call_tool "whatsapp" "search_contacts" "{\"query\":\"$query\"}"
}

mcp_whatsapp_list_chats() {
    local limit="${1:-20}"
    mcp_call_tool "whatsapp" "list_chats" "{\"limit\":$limit}"
}

mcp_whatsapp_send_message() {
    local recipient="$1"
    local message="$2"
    mcp_call_tool "whatsapp" "send_message" "{\"recipient\":\"$recipient\",\"message\":\"$message\"}"
}

# Discord MCP wrappers using Manager
mcp_discord_send_dm() {
    local user_id="$1"
    local message="$2"
    mcp_call_tool "discord-mcp" "discord_send_dm" "{\"user_id\":\"$user_id\",\"message\":\"$message\"}"
}

# Telegram MCP wrappers using Manager
mcp_telegram_send_message() {
    local message="$1"
    mcp_call_tool "telegram" "send_message_to_default_group" "{\"message\":\"$message\"}"
}

# Save agent work output
save_agent_output() {
    local filename="$1"
    local content="$2"
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    local fullpath="${AGENT_OUTPUT_DIR}/${timestamp}_${filename}"
    
    ensure_dir "$AGENT_OUTPUT_DIR"
    echo "$content" > "$fullpath"
    log_info "Saved agent output: $fullpath"
    echo "$fullpath"
}

# Generate report filename
get_report_filename() {
    local timestamp
    timestamp=$(date '+%Y%m%d_%H%M%S')
    echo "${AGENT_OUTPUT_DIR}/report_${timestamp}.md"
}
