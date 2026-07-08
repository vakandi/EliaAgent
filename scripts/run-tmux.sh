#!/bin/zsh

# ============================================================
# TMUX INSIDE TMUX GUARD
# If already inside a tmux session, do NOT exec tmux attach —
# that would replace the calling shell and kill the parent pane.
# ============================================================
if [[ -n "$TMUX" ]]; then
    echo "[GUARD] Already inside tmux session ($TMUX) — skipping tmux attach."
    echo "[GUARD] To attach to the 'elia' session manually: tmux attach -t elia"
    exit 0
fi

if tmux has-session -t elia 2>/dev/null; then
    exec tmux attach -t elia
fi
tmux new-session -d -s elia
tmux split-window -h -t elia
tmux split-window -h -t elia:0.1
if [[ -f "$HOME/EliaAI/.proxy_enabled" ]]; then
    tmux send-keys -t elia:0.0 "~/EliaAI/setup/opencode-proxy.sh serve --port 4096" C-m
else
    tmux send-keys -t elia:0.0 "opencode serve --port 4096" C-m
fi
tmux send-keys -t elia:0.1 "~/EliaAI/scripts/start_elias_discord.sh" C-m
tmux send-keys -t elia:0.2 "cd ~/EliaAI/ui_electron && npm start" C-m
sleep 3
tmux attach -t elia