#!/bin/zsh
# Voice Command Wrapper - Respects ULW/Ralph toggle from ui_electron
# This is used by the voice trigger (big orb) instead of going through dictate.command

set -euo pipefail

# Get the directory where this script is located, then get parent (EliaAI root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

export HOME="$(eval echo ~$(whoami))"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="$HOME/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.nvm/versions/node/v20.20.2/bin:$PATH"

source "$HOME/.zshrc" 2>/dev/null || true

# Read model from .opencode_model if set
MODEL_FILE="${AGENT_DIR}/.opencode_model"
MODEL="big-pickle"
if [[ -f "$MODEL_FILE" ]]; then
    MODEL=$(cat "$MODEL_FILE" | tr -d '[:space:]')
fi

# Check for proxy
if [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
    echo "[VOICE] Proxy enabled - will use proxychains4"
else
    echo "[VOICE] Proxy disabled - direct connection"
fi

# Check ULW/Ralph toggle - this is the KEY check that voice trigger was missing!
RALPH_MODE_FILE="${AGENT_DIR}/.ralph_mode"
if [[ -f "$RALPH_MODE_FILE" ]]; then
    echo "[VOICE] Ralph mode ENABLED (via UI toggle)"
else
    echo "[VOICE] ULW mode ENABLED by DEFAULT"
fi

# Read transcript from /tmp/transcript.txt (created by dictate.command before calling this)
TRANSCRIPT_FILE="/tmp/transcript.txt"
EXTRA_PROMPT=""
if [[ -f "$TRANSCRIPT_FILE" ]]; then
    TRANSCRIPT=$(cat "$TRANSCRIPT_FILE" | tr -d '[:space:]')
    if [[ -n "$TRANSCRIPT" && ${#TRANSCRIPT} -gt 10 ]]; then
        echo "[VOICE] Transcript: ${TRANSCRIPT:0:50}..."
        EXTRA_PROMPT="$TRANSCRIPT"
    else
        echo "[VOICE] No transcript or too short"
    fi
fi

# Set model for trigger script
export OPENCODE_MODEL="$MODEL"

# Create extra prompt file if we have a transcript
EXTRA_PROMPT_FILE=""
if [[ -n "$EXTRA_PROMPT" ]]; then
    TIMESTAMPED_PROMPT="${AGENT_DIR}/.agent_payloads/prompt_$(date +%Y%m%d_%H%M%S).txt"
    cat > "$TIMESTAMPED_PROMPT" << EOF
# 🚨 VOICE COMMAND - $(date '+%Y-%m-%d %H:%M:%S')

$EXTRA_PROMPT

EOF
    EXTRA_PROMPT_FILE="$TIMESTAMPED_PROMPT"
fi

TRIGGER_SCRIPT="${AGENT_DIR}/subworkers/scripts/trigger_template.js"

echo "[VOICE] Starting EliaAI with model: $MODEL"
echo "[VOICE] Loop mode: $([[ -f "$RALPH_MODE_FILE" ]] && echo 'Ralph (50 iters)' || echo 'ULW (unlimited)')"

# Execute trigger script which will respect .ralph_mode
if [[ -n "$EXTRA_PROMPT_FILE" ]]; then
    EXTRA_CONTENT=$(cat "$EXTRA_PROMPT_FILE")
    node "$TRIGGER_SCRIPT" --agent elia --prompt "$EXTRA_CONTENT"
else
    node "$TRIGGER_SCRIPT" --agent elia
fi

EXIT_CODE=$?

# Cleanup
if [[ -n "$EXTRA_PROMPT_FILE" && -f "$EXTRA_PROMPT_FILE" ]]; then
    rm -f "$EXTRA_PROMPT_FILE"
fi

exit $EXIT_CODE
