#!/bin/zsh

SESSION="elia"
~/EliaAI/scripts/kill_elia.sh

tmux new-session -d -s $SESSION
tmux split-window -h -t $SESSION
tmux split-window -h -t $SESSION
tmux select-layout -t $SESSION tiled

sleep 1
tmux send-keys -t $SESSION:0.0 "~/EliaAI/scripts/opencode-serve.sh 4096" $'\n'
sleep 1
tmux send-keys -t $SESSION:0.1 "~/EliaAI/scripts/start_elias_discord.sh" $'\n'
sleep 1
tmux send-keys -t $SESSION:0.2 "cd ~/EliaAI/ui_electron && npm start" $'\n'

tmux attach -t $SESSION