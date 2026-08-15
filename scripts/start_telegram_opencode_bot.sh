#!/bin/zsh
# Start EliaAI Telegram OpenCode bot
# Run from EliaAI root. Uses .env in integrations/telegram-opencode-bot/ or EliaAI root.

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

AGENT_DIR="${0:A:h}"
BOT_DIR="${AGENT_DIR}/integrations/telegram-opencode-bot"

if [[ ! -d "$BOT_DIR" ]]; then
    echo "telegram-opencode-bot not found at: $BOT_DIR"
    exit 1
fi

for env in "${BOT_DIR}/.env" "${AGENT_DIR}/.env"; do
    if [[ -f "$env" ]]; then
        export ELIA_HELPER_DIR="$AGENT_DIR"
        cd "$BOT_DIR"
        if [[ -f dist/cli.js ]]; then
            node dist/cli.js
        else
            npm run build && node dist/cli.js
        fi
        exit 0
    fi
done

echo "No .env found. Copy integrations/telegram-opencode-bot/.env.example to integrations/telegram-opencode-bot/.env and set TELEGRAM_BOT_TOKENS."
exit 1