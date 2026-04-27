#!/bin/zsh
AGENT_DIR="/Users/vakandi/EliaAI"
LOG_FILE="$AGENT_DIR/subworkers/logs/promoter_cobou.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting CoBou Promoter..." >> "$LOG_FILE"

RALPH_MODE_FILE="$AGENT_DIR/.ralph_mode"
if [[ -f "$RALPH_MODE_FILE" ]]; then
    LOOP_CMD="/ralph-loop"
else
    LOOP_CMD="/ulw-loop"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Using: $LOOP_CMD" >> "$LOG_FILE"

cd "$AGENT_DIR"
oh-my-opencode run -a cobou-promoter "$LOOP_CMD"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] CoBou Promoter completed" >> "$LOG_FILE"