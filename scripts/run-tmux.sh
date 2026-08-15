#!/bin/zsh

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

SESSION="elia-ui"

# Track whether we're inside tmux (for attachment decision only)
INSIDE_TMUX=false
if [[ -n "$TMUX" ]]; then
    INSIDE_TMUX=true
    echo "[run-tmux] Already inside tmux session ($TMUX) — will create sessions but skip attach."
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -A -s "$SESSION"
    exit 0
fi
tmux new-session -d -s "$SESSION"
tmux split-window -h -t "$SESSION"
tmux split-window -h -t "$SESSION":0.1
if [[ -f "$HOME/EliaAI/.proxy_enabled" ]]; then
    tmux send-keys -t "$SESSION":0.0 "~/EliaAI/setup/opencode-proxy.sh serve --port 4096" C-m
else
    tmux send-keys -t "$SESSION":0.0 "opencode serve --port 4096" C-m
fi
tmux send-keys -t "$SESSION":0.1 "~/EliaAI/scripts/start_elias_discord.sh" C-m
tmux send-keys -t "$SESSION":0.2 "cd ~/EliaAI/ui_electron && npm start" C-m
sleep 3
if [[ "$INSIDE_TMUX" == "false" ]]; then
    TMUX= tmux new-session -A -s "$SESSION"
else
    echo "[run-tmux] Sessions are ready. Attach manually: tmux attach -t $SESSION"
fi