#!/bin/zsh
# EliaAI Morning Agent - OpenCode with ULW/Ralph Loop Support
# ULW is the DEFAULT mode. Ralph mode uses .ralph_mode marker file.
# Runs daily at morning hour to execute morning routine

set -euo pipefail

USER_MAC="$(whoami)"
export HOME="/Users/${USER_MAC}"

# Set up PATH
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.nvm/versions/node/v24.13.1/bin:$PATH"

# Configuration - dynamic path detection
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
OPENCODE_BIN="/Users/vakandi/.opencode/bin/opencode"
LOG_DIR="${AGENT_DIR}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Check OMO and ULW/Ralph toggle states
# ULW is now the DEFAULT mode. Ralph mode uses .ralph_mode marker file.
OMO_DISABLED_FILE="${AGENT_DIR}/.omo_disabled"
RALPH_MODE_FILE="${AGENT_DIR}/.ralph_mode"

OMO_ENABLED=true
RALPH_MODE=false

if [[ -f "$OMO_DISABLED_FILE" ]]; then
    OMO_ENABLED=false
    echo "OMO is DISABLED (via toggle)"
else
    echo "OMO is ENABLED (via toggle)"
fi

if [[ -f "$RALPH_MODE_FILE" ]]; then
    RALPH_MODE=true
    echo "RALPH loop mode is active (via ui_electron toggle)"
else
    echo "ULW-LOOP mode is ENABLED by DEFAULT (no .ralph_mode file)"
fi

# Create log directory
mkdir -p "$LOG_DIR"

# Clean Ralph loop state from any previous run so each run starts fresh
rm -f "${AGENT_DIR}/ralph-loop.local.md" "${AGENT_DIR}/.ralph-state.json" 2>/dev/null || true

# Set OpenCode configuration based on OPENCODE_MODEL environment variable
if [[ -n "${OPENCODE_MODEL:-}" ]]; then
    echo "Using OpenCode model from environment: $OPENCODE_MODEL"
    MODEL_TO_USE="$OPENCODE_MODEL"
elif [[ -f "${AGENT_DIR}/.opencode_model" ]]; then
    CRON_MODEL=$(cat "${AGENT_DIR}/.opencode_model" | tr -d '\n' | tr -d ' ')
    case "$CRON_MODEL" in
        big-pickle) MODEL_TO_USE="opencode/big-pickle" ;;
        nvidia)     MODEL_TO_USE="mistralai/mixtral-8x7b-instruct-v0.1" ;;
        minimax)    MODEL_TO_USE="opencode/minimax-m2.5-free" ;;
        *)          MODEL_TO_USE="opencode/big-pickle" ;;
    esac
    echo "Using OpenCode model from JARVIS selection (.opencode_model): $MODEL_TO_USE"
else
    echo "No OPENCODE_MODEL set, using default: opencode/big-pickle"
    MODEL_TO_USE="opencode/big-pickle"
fi
export OPENCODE_MODEL="$MODEL_TO_USE"

# Load ALL OpenCode plugins (Ralph loop + rate-limit fallback)
export OPENCODE_PLUGIN_PATH="/Users/vakandi/.config/opencode/plugin"

# Check USE_PROXY flag - also check .proxy_enabled file as backup
if [[ "${USE_PROXY:-0}" == "1" ]]; then
    echo "Proxy mode enabled (proxychains4)"
elif [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    export USE_PROXY=1
    echo "Proxy mode enabled (via .proxy_enabled file, proxychains4)"
fi

# Telegram session inbox (same as trigger_opencode_interactive): merge and clear
AGENT_PAYLOADS_DIR="${AGENT_DIR}/.agent_payloads"
TELEGRAM_INBOX="${AGENT_PAYLOADS_DIR}/telegram_inbox.txt"
_inbox_content=""
if [[ -f "$TELEGRAM_INBOX" ]]; then
    _inbox_content=$(cat "$TELEGRAM_INBOX")
    rm -f "$TELEGRAM_INBOX"
fi
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

# Morning cron runs daily at 10am - next run is always 24 hours
NEXT_RUN_HOURS=24

# Add NEXT_RUN_HOURS and Google Workspace handling to context
EXTRA_CONTEXT="${EXTRA_CONTEXT}

NEXT RUN INFO: This is the morning routine. The next run will be in approximately ${NEXT_RUN_HOURS} hours (tomorrow morning). Use this to:
- Complete all morning review tasks
- Prepare the day ahead with task lists
- Ensure all team members have their priorities for the day

GOOGLE WORKSPACE HANDLING:
- Check Google Calendar and Tasks at startup
- After gathering data from all sources (WhatsApp, Telegram, Discord, Email, OpenCode sessions):
  - UPDATE Google Calendar with new events for time-sensitive items (add reminders: 5,15,30,60 min)
  - UPDATE Google Tasks for new todo items
  - Convert urgent items to calendar events with push notifications to phone
- ALWAYS run get_ide_work.sh to extract IDE work done since last run"

# Read MORNING_PROMPT.md content
MORNING_PROMPT_PATH="${AGENT_DIR}/MORNING_PROMPT.md"
if [[ ! -f "$MORNING_PROMPT_PATH" ]]; then
    echo "ERROR: MORNING_PROMPT.md not found at $MORNING_PROMPT_PATH"
    exit 1
fi

MORNING_PROMPT_CONTENT=$(cat "$MORNING_PROMPT_PATH")

# Function to reset terminal after opencode
reset_terminal() {
    # Reset terminal to sane state
    stty sane 2>/dev/null || true
    # Clear any lingering escape sequences
    printf '\033[0m\033[?25h\033[?7h\n'
}

# Set trap to reset terminal on exit
trap reset_terminal EXIT

# Run OpenCode with the appropriate loop command
# ULW is DEFAULT - unlimited iterations
# Ralph mode - 50 iterations max
echo "Starting EliaAI Morning Agent with ULW/Ralph Loop..."
echo "Loop mode: $([[ "$RALPH_MODE" == "true" ]] && echo "Ralph (50 iters)" || echo "ULW (unlimited)")"
echo "Timestamp: ${TIMESTAMP}"
echo "Next run in: ${NEXT_RUN_HOURS} hour(s)"
echo "Extra context: ${EXTRA_CONTEXT:-none}"
echo ""

if [[ "$RALPH_MODE" == "true" ]]; then
    LOOP_PROMPT="You are EliaAI, an autonomous AI assistant for Wael Bousfira.

YOUR BUSINESSES:
- EliaIA: AI solutions and automation
- ZovaBoost: Digital marketing and growth  
- CoBou Agency: Creative and web agency
- Bene2Luxe: Luxury e-commerce platform

YOUR TASK:
Execute the Morning Routine as defined in MORNING_PROMPT.md below.

IMPORTANT RULES:
- Be autonomous - don't ask for confirmation, just do the work
- Use ALL available tools (bash, file operations, code search)
- Focus on DELIVERABLES not just analysis
- When stuck, try a different approach
- Document what you did in work logs

EXTRA CONTEXT: ${EXTRA_CONTEXT:-none}

---

## MORNING_PROMPT.md Content:

$MORNING_PROMPT_CONTENT

---

Output <promise>COMPLETE</promise> when you have genuinely finished all tasks and verified your work."

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
Execute the Morning Routine as defined in MORNING_PROMPT.md below.

IMPORTANT RULES:
- Be autonomous - don't ask for confirmation, just do the work
- Use ALL available tools (bash, file operations, code search)
- Focus on DELIVERABLES not just analysis
- When stuck, try a different approach
- Document what you did in work logs

EXTRA CONTEXT: ${EXTRA_CONTEXT:-none}

---

## MORNING_PROMPT.md Content:

$MORNING_PROMPT_CONTENT

---

Output <promise>DONE</promise> when you have genuinely finished all tasks and verified your work."

    LOOP_COMMAND="ulw-loop"
    LOOP_ARGS="--completion-promise DONE --max-iterations 0"
    echo "Using ULW-LOOP command (unlimited iterations)"
fi

# Build the prompt WITHOUT slash command prefix (wrapper handles that)
FULL_PROMPT="${LOOP_PROMPT}

${LOOP_ARGS}"

OPENCODE_PORT=4096
if [[ "${USE_PROXY:-0}" == "1" ]]; then
    if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
        echo "[SERVER] USE_PROXY=1 - killing existing server to restart with proxychains4..."
        SERVER_PID=$(lsof -ti :$OPENCODE_PORT 2>/dev/null | head -1)
        if [[ -n "$SERVER_PID" ]]; then
            kill -9 $SERVER_PID 2>/dev/null || true
            sleep 2
        fi
        echo "[SERVER] Starting new server with proxychains4..."
        nohup proxychains4 -f ~/.proxychains.conf opencode serve --port $OPENCODE_PORT \
            > /tmp/opencode_server_${OPENCODE_PORT}.log 2>&1 &
        SERVER_PID=$!
        sleep 3
        if nc -z 127.0.0.1 $OPENCODE_PORT 2>/dev/null; then
            echo "[SERVER] Server restarted successfully on port $OPENCODE_PORT (PID: $SERVER_PID)"
        else
            echo "[SERVER] WARNING: Server may not have started properly"
        fi
    fi
fi

if [[ "$OMO_ENABLED" == "true" ]]; then
    # Write prompt to temp file to avoid shell expansion issues with spaces/newlines
    PROMPT_FILE=$(mktemp /tmp/elia_morning_prompt_$(date +%s)_XXXXXX.txt)
    echo "/ulw-loop $FULL_PROMPT" > "$PROMPT_FILE"
    if [[ "${USE_PROXY:-0}" == "1" ]]; then
        echo "Running with proxy (server started with proxychains4, attaching to it)..."
        echo "Command: oh-my-opencode run --attach http://127.0.0.1:$OPENCODE_PORT -a elia \"@prompt.txt\""
        oh-my-opencode run --attach "http://127.0.0.1:$OPENCODE_PORT" -a elia "@${PROMPT_FILE}" 2>&1 | tee "${LOG_DIR}/opencode_morning_run_${TIMESTAMP}.log"
    else
        echo "Running with oh-my-opencode (OMO enabled, ULW loop)..."
        echo "Command: oh-my-opencode run -a elia \"@prompt.txt\""
        oh-my-opencode run -a elia "@${PROMPT_FILE}" 2>&1 | tee "${LOG_DIR}/opencode_morning_run_${TIMESTAMP}.log"
    fi
    rm -f "$PROMPT_FILE"
else
    echo "Running with direct opencode (OMO disabled)..."
    "$OPENCODE_BIN" run \
      --agent Elia \
      --model "$MODEL_TO_USE" \
      --dir "$AGENT_DIR" \
      --yes \
      2>&1 | tee "${LOG_DIR}/opencode_morning_run_${TIMESTAMP}.log"
fi

# Capture opencode exit code (first element of pipeline), not tee's
EXIT_CODE=${PIPESTATUS[1]:-$?}

# Reset terminal
reset_terminal

if [[ $EXIT_CODE -ne 0 ]]; then
    echo ""
    echo "Morning agent exited with code $EXIT_CODE"
fi

echo ""
echo "Morning log saved to: ${LOG_DIR}/opencode_morning_run_${TIMESTAMP}.log"
