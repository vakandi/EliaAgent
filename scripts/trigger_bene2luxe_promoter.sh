#!/bin/zsh
AGENT_DIR="/Users/vakandi/EliaAI"
LOG_FILE="$AGENT_DIR/subworkers/logs/promoter_bene2luxe.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Bene2Luxe Promoter..." >> "$LOG_FILE"

RALPH_MODE_FILE="$AGENT_DIR/.ralph_mode"
if [[ -f "$RALPH_MODE_FILE" ]]; then
    LOOP_CMD="/ralph-loop"
else
    LOOP_CMD="/ulw-loop"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Using: $LOOP_CMD" >> "$LOG_FILE"

cd "$AGENT_DIR"
oh-my-opencode run -a bene2luxe-promoter "$LOOP_CMD"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bene2Luxe Promoter completed" >> "$LOG_FILE"