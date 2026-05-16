#!/bin/zsh
tmux kill-session -t elia 2>/dev/null
sleep 1
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