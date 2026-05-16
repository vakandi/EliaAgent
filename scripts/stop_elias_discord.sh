#!/bin/zsh

set -euo pipefail

BOT_DIR="${0:A:h}/integrations/elia-discord-bot"
PID_FILE="${BOT_DIR}/bot.pid"

if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping EliaDiscord bot (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Bot stopped."
    else
        echo "Bot not running (stale PID file)."
        rm -f "$PID_FILE"
    fi
else
    PID=$(pgrep -f "python.*integrations/elia-discord-bot/bot.py" 2>/dev/null | head -1)
    if [[ -n "$PID" ]]; then
        echo "Stopping EliaDiscord bot (PID: $PID)..."
        kill "$PID"
        echo "Bot stopped."
    else
        echo "EliaDiscord bot not running."
    fi
fi