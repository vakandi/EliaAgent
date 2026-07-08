#!/bin/zsh
# EliaAI Agent with ULW/Ralph Loop Support
# ULW is the DEFAULT mode. Ralph mode uses .ralph_mode marker file.

set -euo pipefail

# ============================================================
# SCHEDULER DISABLE GUARD
# If .scheduler_disabled exists, exit immediately without running.
# Create this file to permanently disable all scheduled/interactive agent runs:
#   touch ~/EliaAI/.scheduler_disabled
# ============================================================
if [[ -f "$HOME/EliaAI/.scheduler_disabled" ]]; then
    echo "[GUARD] .scheduler_disabled found — agent disabled. Exiting."
    exit 0
fi

USER_MAC="$(whoami)"
export HOME="/Users/${USER_MAC}"

# Set up PATH
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="$HOME/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.nvm/versions/node/v20.20.2/bin:$PATH"

# Configuration - dynamic path detection
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
OPENCODE_BIN="$(which opencode 2>/dev/null || echo 'opencode')"
LOG_DIR="${AGENT_DIR}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ============================================================
# MCP SERVERS STARTUP - CRITICAL FOR CRON JOBS
# Cron runs don't have access to MCP servers by default
# This function starts them before opencode runs
# ============================================================
MCP_CONFIG_FILE="$HOME/.config/mcp/mcp_servers.json"
MCP_PID_DIR="/tmp/elia_mcp_pids"

start_mcp_servers() {
    echo "[MCP] Checking MCP servers..."
    
    # Check if MCP config exists
    if [[ ! -f "$MCP_CONFIG_FILE" ]]; then
        echo "[MCP] No MCP config found at $MCP_CONFIG_FILE, skipping..."
        return 0
    fi
    
    # Create PID directory
    mkdir -p "$MCP_PID_DIR"
    
    # List of servers that need to be started (skip HTTP-based ones)
    # HTTP-based (playwright, github-copilot) need external processes
    # whatsapp runs via WhatsApp bridge on port 8080
    LOCAL_SERVERS=("telegram" "mcp-atlassian" "bene2luxe_mcp" "discord-mcp" "gmail")
    
    for server in "${LOCAL_SERVERS[@]}"; do
        # Check if server config exists in JSON
        if grep -q "\"$server\":" "$MCP_CONFIG_FILE" 2>/dev/null; then
            # Check if server is already running
            if [[ -f "$MCP_PID_DIR/${server}.pid" ]]; then
                old_pid=$(cat "$MCP_PID_DIR/${server}.pid" 2>/dev/null)
                if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
                    echo "[MCP] $server already running (PID: $old_pid)"
                    continue
                else
                    echo "[MCP] Stale PID file for $server, removing..."
                    rm -f "$MCP_PID_DIR/${server}.pid"
                fi
            fi
            
            echo "[MCP] Starting $server..."
            
            # Extract command and args from JSON (simplified parsing)
            case "$server" in
                "telegram")
                    cd /Users/vakandi/Documents/mcps_server/telegram-mcp-server 2>/dev/null && \
                    TELEGRAM_API_ID="${TELEGRAM_API_ID:-}" \
                    TELEGRAM_API_HASH="${TELEGRAM_API_HASH:-}" \
                    TG_BOT_TOKEN="${TG_BOT_TOKEN:-}" \
                    TG_CHAT_ID="${TG_CHAT_ID:-}" \
                    TG_USER_ID="${TG_USER_ID:-}" \
                    DISABLE_APPROVALS_POLLING="true" \
                    node dist/index.js >> "$LOG_DIR/mcp_telegram.log" 2>&1 &
                    ;;
                "mcp-atlassian")
                    cd /Users/vakandi && \
                    JIRA_URL="https://bsbagency.atlassian.net" \
                    JIRA_USERNAME="${JIRA_USERNAME:-}" \
                    JIRA_API_TOKEN="${JIRA_API_TOKEN:-}" \
                    CONFLUENCE_URL="https://bsbagency.atlassian.net/wiki" \
                    CONFLUENCE_USERNAME="${CONFLUENCE_USERNAME:-}" \
                    CONFLUENCE_API_TOKEN="${CONFLUENCE_API_TOKEN:-}" \
                    /Users/vakandi/.local/bin/uvx mcp-atlassian >> "$LOG_DIR/mcp_atlassian.log" 2>&1 &
                    ;;
                "bene2luxe_mcp")
                    cd /Users/vakandi/Documents/mcps_server/bene2luxe_mcp 2>/dev/null && \
                    BENELUXE_API_URL="https://bene2luxe.com" \
                    .venv/bin/python main.py >> "$LOG_DIR/mcp_bene2luxe.log" 2>&1 &
                    ;;
                "discord-mcp")
                    cd /Users/vakandi/Documents/mcps_server/discord_mcp_custom 2>/dev/null && \
                    WATSON_DISCORD_HEADLESS=1 \
                    .venv/bin/python mcp_server.py >> "$LOG_DIR/mcp_discord.log" 2>&1 &
                    ;;
                "whatsapp")
                    cd /Users/vakandi/Documents/mcps_server/whatsapp-mcp/whatsapp-mcp-server 2>/dev/null && \
                    WHATSAPP_API_BASE_URL=http://localhost:8080/api \
                    .venv/bin/python main.py >> "$LOG_DIR/mcp_whatsapp.log" 2>&1 &
                    ;;
                "gmail")
                    cd /Users/vakandi/Documents/mcps_server/gmail-mcp-server 2>/dev/null && \
                    GMAIL_OAUTH_PATH=/Users/vakandi/.gmail-mcp/gcp-oauth.keys.json \
                    GMAIL_CREDENTIALS_PATH=/Users/vakandi/.gmail-mcp/credentials.json \
                    GMAIL_OAUTH_PORT=7878 \
                    nvm use 20 && node dist/index.js >> "$LOG_DIR/mcp_gmail.log" 2>&1 &
                    ;;
            esac
            
            new_pid=$!
            echo "$new_pid" > "$MCP_PID_DIR/${server}.pid"
            echo "[MCP] $server started (PID: $new_pid)"
        fi
    done
    
    echo "[MCP] MCP server startup complete"
}

# Only start MCP servers for CRON runs (not for manual/voice triggers)
# if [[ "${ELIA_CRON:-0}" == "1" ]]; then
#     start_mcp_servers
#     # Wait for MCP servers to initialize (critical!)
#     echo "[MCP] Waiting for servers to initialize..."
#     sleep 10
#     echo "[MCP] Proceeding with OpenCode..."
# fi
# ============================================================
# END MCP SERVERS STARTUP
# ============================================================

# ============================================================
# CODEMEM VIEWER STARTUP - CRITICAL FOR CODEMEM PLUGIN
# The codemem plugin needs the viewer running on port 38888
# ============================================================
CODEMEM_PORT="${CODEMEM_VIEWER_PORT:-38888}"

start_codemem_viewer() {
    if lsof -i :$CODEMEM_PORT 2>/dev/null | grep -q LISTEN; then
        echo "[CODEMEM] Viewer already running on port $CODEMEM_PORT"
        return 0
    fi
    
    echo "[CODEMEM] Starting codemem viewer from local dist..."
    # Method 1: local built dist (uses node from PATH: /opt/homebrew/bin/node v25 for native modules)
    nohup node \
        /Users/vakandi/EliaAI/integrations/codemem/packages/cli/dist/index.js \
        serve start --foreground --host 127.0.0.1 --port $CODEMEM_PORT \
        --db-path ~/.codemem/mem.sqlite \
        >> "$LOG_DIR/codemem_viewer.log" 2>&1 &
    
    sleep 3
    
    if lsof -i :$CODEMEM_PORT 2>/dev/null | grep -q LISTEN; then
        echo "[CODEMEM] Viewer started successfully via local dist"
        return 0
    fi
    
    # Method 2: npx fallback (works if codemem is in npm cache or can be fetched)
    echo "[CODEMEM] Local dist failed, trying npx fallback..."
    npx -y codemem@0.29.1 serve start --foreground --host 127.0.0.1 --port $CODEMEM_PORT --db-path ~/.codemem/mem.sqlite >> "$LOG_DIR/codemem_viewer.log" 2>&1 &
    
    sleep 3
    
    if lsof -i :$CODEMEM_PORT 2>/dev/null | grep -q LISTEN; then
        echo "[CODEMEM] Viewer started successfully via npx"
        return 0
    else
        echo "[CODEMEM] WARNING: Viewer may not have started. Check $LOG_DIR/codemem_viewer.log"
        return 1
    fi
}

# CRITICAL: Do NOT let set -e crash the script if viewer fails to start
# The agent can still run without the viewer (memory capture is best-effort)
start_codemem_viewer || true

# Check OMO and ULW/Ralph toggle states
OMO_DISABLED_FILE="${AGENT_DIR}/.omo_disabled"
RALPH_MODE_FILE="${AGENT_DIR}/.ralph_mode"

OMO_ENABLED=true
RALPH_MODE=false

echo "=========================================="
echo "[DEBUG] Ralph Mode Check"
echo "[DEBUG] AGENT_DIR: ${AGENT_DIR}"
echo "[DEBUG] RALPH_MODE_FILE: ${RALPH_MODE_FILE}"
echo "[DEBUG] File exists: $([[ -f "$RALPH_MODE_FILE" ]] && echo 'YES' || echo 'NO')"
echo "[DEBUG] ELIA_CRON: ${ELIA_CRON:-not set}"
echo "[DEBUG] RALPH_MODE env: ${RALPH_MODE:-not set}"
echo "=========================================="

if [[ -f "$OMO_DISABLED_FILE" ]]; then
    OMO_ENABLED=false
    echo "OMO is DISABLED (via toggle)"
else
    echo "OMO is ENABLED (via toggle)"
fi

if [[ -f "$RALPH_MODE_FILE" ]]; then
    RALPH_MODE=true
    echo "RALPH loop mode is active (via ui_electron toggle)"
elif [[ "${RALPH_MODE:-0}" == "1" ]]; then
    RALPH_MODE=true
    echo "RALPH loop mode is active (via RALPH_MODE env var)"
else
    echo "ULW-LOOP mode is ENABLED by DEFAULT (no .ralph_mode file)"
fi

CHECKPOINT_FILE="${AGENT_DIR}/.elia_checkpoint.json"

if [[ -f "$CHECKPOINT_FILE" ]]; then
    echo "[CHECKPOINT] Loading previous state..."
    LAST_RUN=$(cat "$CHECKPOINT_FILE" | grep -o '"last_run"[^,]*' | cut -d'"' -f4 || echo "unknown")
    NULL_RUNS=$(cat "$CHECKPOINT_FILE" | grep -o '"null_run_count"[^,]*' | grep -o '[0-9]*' || echo "0")
    echo "  Last run: $LAST_RUN"
    echo "  Null run count: $NULL_RUNS"
else
    echo "[CHECKPOINT] No previous state, starting fresh"
fi

# Create log directory
mkdir -p "$LOG_DIR"

# ============================================================
# LOCK FILE MECHANISM - Prevent concurrent CRON runs only
# Voice/manual triggers bypass the lock to allow immediate response
# ============================================================
LOCK_FILE="/tmp/elia_running.lock"
NTFY_TOPIC="AITeamHelper"

send_ntfy() {
    local title="$1"
    local message="$2"
    curl -s -H "Title: ${title}" "https://ntfy.sh/${NTFY_TOPIC}" -d "${message}" >/dev/null 2>&1 || true
}

# OpenCode server port
OPENCODE_PORT=4096

# Only apply lock mechanism for CRON runs (ELIA_CRON=1 set by cron_wrapper.sh)
# Voice trigger/manual runs bypass this check
if [[ "${ELIA_CRON:-0}" == "1" ]]; then
    LOCK_DIR="${LOCK_FILE}.d"
    LOCK_ACQUIRE_TIMEOUT=10
    LOCK_ACQUIRE_INTERVAL=1
    
    cleanup_lock() {
        if [[ -d "$LOCK_DIR" ]]; then
            OWNER_PID=$(cat "$LOCK_DIR/pid" 2>/dev/null || echo "")
            if [[ "$OWNER_PID" == "$$" ]]; then
                rm -rf "$LOCK_DIR"
            fi
        fi
        rm -f "$LOCK_FILE"
        save_checkpoint
    }
    
    save_checkpoint() {
        CHECKPOINT_FILE="${AGENT_DIR}/.elia_checkpoint.json"
        
        CURRENT_NULL_RUNS=0
        if [[ -f "$CHECKPOINT_FILE" ]]; then
            CURRENT_NULL_RUNS=$(cat "$CHECKPOINT_FILE" | grep -o '"null_run_count"[^,]*' | grep -o '[0-9]*' || echo "0")
        fi
        
        THIS_RUN_NULL="${ELIA_NULL_RUN:-0}"
        
        if [[ "$THIS_RUN_NULL" == "1" ]]; then
            CURRENT_NULL_RUNS=$((CURRENT_NULL_RUNS + 1))
        else
            CURRENT_NULL_RUNS=0
        fi
        
        cat > "$CHECKPOINT_FILE" << EOF
{
  "last_run": "$(date -Iseconds)",
  "last_run_timestamp": "$(date +%s)",
  "null_run_count": $CURRENT_NULL_RUNS,
  "tasks_completed": [],
  "pending_messages": []
}
EOF
        
        echo "[CHECKPOINT] State saved - null_run_count: $CURRENT_NULL_RUNS"
    }
    
    trap 'cleanup_lock' EXIT
    
    ACQUIRED=0
    ELAPSED=0
    
    while [[ $ELAPSED -lt $LOCK_ACQUIRE_TIMEOUT ]]; do
        if mkdir "$LOCK_DIR" 2>/dev/null; then
            echo $$ > "$LOCK_DIR/pid"
            echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$LOCK_DIR/started"
            echo "✅ Lock acquired (PID: $$) - Directory: $LOCK_DIR"
            ACQUIRED=1
            echo $$ > "$LOCK_FILE"
            
            if lsof -i :$OPENCODE_PORT 2>/dev/null | grep -q LISTEN; then
                EXISTING_PID=$(lsof -i :$OPENCODE_PORT 2>/dev/null | grep LISTEN | awk 'NR==1 {print $2}' | head -1)
                if [[ -n "$EXISTING_PID" ]] && [[ "$EXISTING_PID" != "$$" ]]; then
                    echo "⚠️ WARNING: Port $OPENCODE_PORT is occupied by PID $EXISTING_PID"
                    echo "This might indicate a stale session. Continuing anyway..."
                fi
            fi
            
            break
        else
            if [[ -f "$LOCK_DIR/pid" ]]; then
                LOCK_PID=$(cat "$LOCK_DIR/pid" 2>/dev/null || echo "")
                if [[ -n "$LOCK_PID" ]]; then
                    if kill -0 "$LOCK_PID" 2>/dev/null; then
                        echo "⏳ Lock held by active process (PID: $LOCK_PID). Waiting... ($ELAPSED/${LOCK_ACQUIRE_TIMEOUT}s)"
                    else
                        echo "🔧 Removing stale lock (PID: $LOCK_PID not running)"
                        rm -rf "$LOCK_DIR"
                        rm -f "$LOCK_FILE"
                    fi
                fi
            fi
            
            sleep $LOCK_ACQUIRE_INTERVAL
            ELAPSED=$((ELAPSED + LOCK_ACQUIRE_INTERVAL))
        fi
    done
    
    if [[ $ACQUIRED -eq 0 ]]; then
        echo "❌ Failed to acquire lock after ${LOCK_ACQUIRE_TIMEOUT}s"
        echo "Another EliaAI instance appears to be running."
        send_ntfy "⚠️ EliaAI Skip - Lock Timeout" "Could not acquire lock after ${LOCK_ACQUIRE_TIMEOUT}s. Another instance may be stuck."
        exit 1
    fi
fi

rm -f "${AGENT_DIR}/ralph-loop.local.md" "${AGENT_DIR}/.ralph-state.json" 2>/dev/null || true

# Set OpenCode configuration based on OPENCODE_MODEL environment variable
if [[ -n "${OPENCODE_MODEL:-}" ]]; then
    echo "Using OpenCode model from environment: $OPENCODE_MODEL"
    MODEL_TO_USE="$OPENCODE_MODEL"
else
    echo "No OPENCODE_MODEL set, using default: opencode/big-pickle"
    MODEL_TO_USE="opencode/big-pickle"
fi

# Load ALL OpenCode plugins (Ralph loop + rate-limit fallback + codemem memory)
# Ralph must be loaded for the loop to run; rate-limit-fallback for API resilience
# CRITICAL: Include codemem plugin path for memory system to work
export OPENCODE_PLUGIN_PATH="/Users/vakandi/.config/opencode/plugin:/Users/vakandi/EliaAI/integrations/codemem/packages/opencode-plugin"

# Enable codemem plugin logging so we can diagnose observer issues
export CODEMEM_PLUGIN_LOG="true"
export CODEMEM_PLUGIN_DEBUG="true"

# Check USE_PROXY flag - also check .proxy_enabled file as backup
if [[ "${USE_PROXY:-0}" == "1" ]]; then
    echo "Proxy mode enabled (HTTP_PROXY env)"
elif [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    export USE_PROXY=1
    echo "Proxy mode enabled (via .proxy_enabled file, HTTP_PROXY env)"
fi

# Load proxy from proxychains.conf for HTTP_PROXY env vars (local to commands only)
if [[ "${USE_PROXY:-0}" == "1" ]]; then
    PROXY_CONF="$HOME/.proxychains.conf"
    if [[ -f "$PROXY_CONF" ]]; then
        PROXY_LINE=$(grep -v "^#" "$PROXY_CONF" | grep "http " | head -1)
        if [[ -n "$PROXY_LINE" ]]; then
            _type=$(echo "$PROXY_LINE" | awk '{print $1}')
            ip=$(echo "$PROXY_LINE" | awk '{print $2}')
            port=$(echo "$PROXY_LINE" | awk '{print $3}')
            user=$(echo "$PROXY_LINE" | awk '{print $4}')
            pass=$(echo "$PROXY_LINE" | awk '{print $5}')
            # Store for use with env command (not exported globally)
            PROXY_HTTP="http://${user}:${pass}@${ip}:${port}"
            PROXY_HTTPS="http://${user}:${pass}@${ip}:${port}"
            echo "Loaded proxy: $ip:$port (HTTP_PROXY env vars ready)"
        fi
    fi
    
    # CRITICAL: Ensure localhost/127.0.0.1 bypasses the proxy
    # The codemem plugin, MCP servers, and other local services need direct access
    # Without this, Node.js fetch() routes 127.0.0.1 through the proxy which returns 403
    export NO_PROXY="127.0.0.1,localhost"
    export no_proxy="127.0.0.1,localhost"
fi



# Telegram session inbox: messages sent to bot (no /extraprompt) are queued here
# Merge with extra prompt so agent sees them on this run, then clear inbox
AGENT_PAYLOADS_DIR="${AGENT_DIR}/.agent_payloads"
TELEGRAM_INBOX="${AGENT_PAYLOADS_DIR}/telegram_inbox.txt"
_inbox_content=""
if [[ -f "$TELEGRAM_INBOX" ]]; then
    _inbox_content=$(cat "$TELEGRAM_INBOX")
    # Clear inbox after reading so same messages are not re-used
    rm -f "$TELEGRAM_INBOX"
fi

# Build raw extra: inbox (if any) + explicit extra from start_agents
_raw_extra="${1:-}"
if [[ -n "$_inbox_content" ]]; then
    _raw_extra="[Telegram session messages]
$_inbox_content

$_raw_extra"
fi

# Get extra context (escape for safe use inside double-quoted string to avoid parse errors)
EXTRA_CONTEXT="${_raw_extra//\\/\\\\}"
EXTRA_CONTEXT="${EXTRA_CONTEXT//\"/\\\"}"
EXTRA_CONTEXT="${EXTRA_CONTEXT//\`/\\\`}"
EXTRA_CONTEXT="${EXTRA_CONTEXT:-none}"

# Calculate NEXT_RUN_HOURS based on cron schedule
# Cron runs every hour from 11:00 to 21:00 (default)
# If outside active hours, assume next run is tomorrow morning at 10am
CURRENT_HOUR=$(date +%H)
if [[ $CURRENT_HOUR -ge 11 && $CURRENT_HOUR -lt 21 ]]; then
    # During active hours - next run is in 1 hour (or user-specified interval)
    NEXT_RUN_HOURS=1
else
    # Outside active hours - next run is tomorrow morning (10am)
    if [[ $CURRENT_HOUR -lt 10 ]]; then
        # Before 10am - hours until 10am
        NEXT_RUN_HOURS=$((10 - CURRENT_HOUR))
    else
        # After 9pm - hours until tomorrow 10am
        NEXT_RUN_HOURS=$((24 - CURRENT_HOUR + 10))
    fi
fi

# Add NEXT_RUN_HOURS to context - tells agent when it will run next
NEXT_RUN_INFO="
NEXT RUN INFO: This agent will run again in approximately ${NEXT_RUN_HOURS} hour(s). Use this to:
- Pre-prepare documents and research for tasks you anticipate
- Identify decisions needed from team members (Thomas, Rida, Ali, etc.)
- Prepare options/recommendations for upcoming conversations
- Do preparatory work now to save time on next run"

if [[ -n "$EXTRA_CONTEXT" && "$EXTRA_CONTEXT" != "none" ]]; then
    EXTRA_CONTEXT="${EXTRA_CONTEXT}
${NEXT_RUN_INFO}"
else
    EXTRA_CONTEXT="$NEXT_RUN_INFO"
fi

# Function to reset terminal after opencode
reset_terminal() {
    # Reset terminal to sane state
    stty sane 2>/dev/null || true
    # Clear any lingering escape sequences
    printf '\033[0m\033[?25h\033[?7h\n'
}

# Set trap to reset terminal on exit
trap reset_terminal EXIT


LOGFILE="${LOG_DIR}/opencode_interactive_${TIMESTAMP}.log"

# Run OpenCode with the appropriate loop command
# ULW is DEFAULT - unlimited iterations
# Ralph mode - 50 iterations max
echo "Starting EliaAI Agent with NVIDIA NIM..." | tee -a "$LOGFILE"
echo "Loop mode: $([[ "$RALPH_MODE" == "true" ]] && echo "Ralph (50 iters)" || echo "ULW (unlimited)")" | tee -a "$LOGFILE"
echo "Timestamp: ${TIMESTAMP}" | tee -a "$LOGFILE"
echo "Next run in: ${NEXT_RUN_HOURS} hour(s)" | tee -a "$LOGFILE"
echo "Extra context: ${EXTRA_CONTEXT:-none}" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

if [[ "$RALPH_MODE" == "true" ]]; then
    LOOP_PROMPT="You are EliaAI, an autonomous AI assistant for Wael Bousfira.

YOUR BUSINESSES:
- EliaIA: AI solutions and automation
- ZovaBoost: Digital marketing and growth  
- CoBou Agency: Creative and web agency
- Bene2Luxe: Luxury e-commerce platform

YOUR TASK:
1. Read context from ${AGENT_DIR}/context/ (business.md, opportunities.md, jira-projects.md, TOOLS.md)
2. Check docs/ for recent work logs and TODOs
3. Identify bugs, incomplete tasks, or issues mentioned in messages/logs
4. DO ACTUAL WORK - write code, fix bugs, complete tasks
5. VERIFY your work - check that code compiles/runs, bugs are fixed
6. Report progress via curl to ntfy.sh/AITeamHelper

IMPORTANT RULES:
- Be autonomous - don't ask for confirmation, just do the work
- Use ALL available tools (bash, file operations, code search)
- Focus on DELIVERABLES not just analysis
- When stuck, try a different approach
- Document what you did in work logs

EXTRA CONTEXT: ${EXTRA_CONTEXT:-none}

Output <promise>DONE</promise> when you have genuinely finished all tasks and verified your work."

    LOOP_COMMAND="ralph-loop"
    LOOP_ARGS="--completion-promise COMPLETE --max-iterations 50"
    echo "Using Ralph loop command (max 50 iterations)"
else
    LOOP_PROMPT="You are EliaAI, an autonomous AI assistant for Wael Bousfira.

YOUR BUSINESSES:
- EliaIA: AI solutions and automation
- ZovaBoost: Digital marketing and growth
- CoBou Agency: Creative and web agency
- Bene2Luxe: Luxury e-commerce platform

YOUR TASK:
1. Read context from ${AGENT_DIR}/context/ (business.md, opportunities.md, jira-projects.md, TOOLS.md)
2. Check docs/ for recent work logs and TODOs
3. Identify bugs, incomplete tasks, or issues mentioned in messages/logs
4. DO ACTUAL WORK - write code, fix bugs, complete tasks
5. VERIFY your work - check that code compiles/runs, bugs are fixed
6. Report progress via curl to ntfy.sh/AITeamHelper

IMPORTANT RULES:
- Be autonomous - don't ask for confirmation, just do the work
- Use ALL available tools (bash, file operations, code search)
- Focus on DELIVERABLES not just analysis
- When stuck, try a different approach
- Document what you did in work logs

EXTRA CONTEXT: ${EXTRA_CONTEXT:-none}

Output <promise>DONE</promise> when you have genuinely finished all tasks and verified your work."

    LOOP_COMMAND="ulw-loop"
    LOOP_ARGS="--completion-promise DONE --max-iterations 30"
    echo "Using ULW-LOOP command (max 30 iterations)"
fi

FULL_LOOP_MESSAGE=""
if [[ -n "$LOOP_COMMAND" ]]; then
    # Build prompt WITHOUT slash prefix - wrapper adds it
    FULL_LOOP_MESSAGE="${LOOP_PROMPT}"
    if [[ -n "$LOOP_ARGS" ]]; then
        FULL_LOOP_MESSAGE="${FULL_LOOP_MESSAGE}

${LOOP_ARGS}"
    fi
fi

echo "DEBUG: FULL_LOOP_MESSAGE length = ${#FULL_LOOP_MESSAGE}"
echo "DEBUG: FIRST 200 chars = ${FULL_LOOP_MESSAGE:0:200}"

# Check if existing server is healthy — if so, reuse instead of destroying it
SERVER_HEALTHY=false
if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
    SERVER_PID=$(lsof -ti :$OPENCODE_PORT 2>/dev/null | head -1)
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "[SERVER] Existing healthy server on port $OPENCODE_PORT (PID: $SERVER_PID) — reusing"
        SERVER_HEALTHY=true
    else
        echo "[SERVER] Stale process on port $OPENCODE_PORT — cleaning up"
        kill -9 $SERVER_PID 2>/dev/null || true
        sleep 1
    fi
fi

if [[ "$SERVER_HEALTHY" != "true" ]]; then
    echo "[SERVER] Starting fresh server on port $OPENCODE_PORT..."
    if [[ -n "${PROXY_HTTP:-}" ]]; then
        # IMPORTANT: OpenCode serve does NOT need HTTP_PROXY. If the proxy env vars
        # are present, the OpenCode binary's HTTP client routes ALL requests through
        # the proxy — including local plugin → viewer (127.0.0.1:38888) requests.
        # The Webshare proxy returns 403 for localhost destinations
        # (client_connect_invalid_ip), breaking the codemem plugin.
        # Only the RUN command (inherits proxy from shell) needs outbound proxy access.
        nohup env NO_PROXY="127.0.0.1,localhost,::1" no_proxy="127.0.0.1,localhost,::1" "$OPENCODE_BIN" serve --port $OPENCODE_PORT \
            > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
    else
        nohup "$OPENCODE_BIN" serve --port $OPENCODE_PORT \
            > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
    fi
    SERVER_PID=$!

    # Wait for server to become available (up to 10 seconds)
    echo "[SERVER] Waiting for server to become available on port $OPENCODE_PORT..."
    for i in $(seq 1 10); do
        if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
            echo "[SERVER] Server started successfully on port $OPENCODE_PORT (PID: $SERVER_PID, attempt: ${i}s)"
            break
        fi
        if [[ $i -eq 10 ]]; then
            echo "[SERVER] WARNING: Server may not have started properly after 10s - check /tmp/opencode_server_${OPENCODE_PORT}.log"
        else
            sleep 1
        fi
    done
fi


echo ""
echo "========================================" | tee -a "$LOGFILE"
echo "COMMAND TO EXECUTE:" | tee -a "$LOGFILE"
echo "========================================" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

if [[ "${USE_PROXY:-0}" == "1" ]]; then
    echo "Running with proxy (fresh server on port $OPENCODE_PORT)..." | tee -a "$LOGFILE"
    echo "EXEC: oh-my-opencode run -a elia --port $OPENCODE_PORT \"/${LOOP_COMMAND} ...\"" | tee -a "$LOGFILE"
    stdbuf -oL -eL oh-my-opencode run -a elia --port "$OPENCODE_PORT" "/${LOOP_COMMAND} ${FULL_LOOP_MESSAGE}" 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE=$?
elif [[ "$OMO_ENABLED" == "true" ]]; then
    echo "Running with oh-my-opencode (OMO enabled)..." | tee -a "$LOGFILE"
    echo "EXEC: oh-my-opencode run -a elia --port $OPENCODE_PORT \"/${LOOP_COMMAND} \$FULL_LOOP_MESSAGE\"" | tee -a "$LOGFILE"
    stdbuf -oL -eL oh-my-opencode run -a elia --port "$OPENCODE_PORT" "/${LOOP_COMMAND} ${FULL_LOOP_MESSAGE}" 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE=$?
else
    echo "Running with direct opencode (OMO disabled)..." | tee -a "$LOGFILE"
    echo "EXEC: $OPENCODE_BIN run --agent elia --model $MODEL_TO_USE --port $OPENCODE_PORT --dir $AGENT_DIR --yes \"\$FULL_LOOP_MESSAGE\"" | tee -a "$LOGFILE"
    "$OPENCODE_BIN" run \
      --agent elia \
      --model "$MODEL_TO_USE" \
      --port $OPENCODE_PORT \
      --dir "$AGENT_DIR" \
      --yes \
      "$FULL_LOOP_MESSAGE" 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE=$?
fi

echo ""
echo "========================================"
echo "EXECUTION COMPLETE"
echo "========================================"

# Reset terminal
reset_terminal

if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "Agent exited with code $EXIT_CODE"
fi

echo ""
echo "Log saved to: ${LOG_DIR}/opencode_interactive_${TIMESTAMP}.log"
