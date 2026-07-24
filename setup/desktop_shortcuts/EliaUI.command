#!/bin/zsh
# EliaUI — Open tmux session with all 3 Elia services
# Discord bot + Electron UI + OpenCode serve

SESSION="elia-ui"

# Guard: already inside tmux
if [[ -n "$TMUX" ]]; then
    echo "Already inside a tmux session. To attach manually: tmux attach -t $SESSION"
    echo "This window will close in 5 seconds..."
    sleep 5
    exit 0
fi

# Create session only if it doesn't exist
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION" -n "EliaAI"

    # Split into 3 panes: left half, right top, right bottom
    # Pane 0 (left): opencode serve
    # Pane 1 (right top): Discord bot
    # Pane 2 (right bottom): Electron UI
    tmux split-window -h -t "$SESSION":0
    tmux split-window -v -t "$SESSION":0.1

    # Resize: give pane 0 50% width
    tmux select-layout -t "$SESSION":0 main-vertical
    sleep 1

    # Start opencode serve in pane 0
    tmux send-keys -t "$SESSION":0.0 "cd ~/EliaAgent && ./scripts/opencode-serve.sh 4096" Enter

    # Small delay so the scripts don't clash on startup
    sleep 2

    # Start Discord bot in pane 1 (right top)
    tmux send-keys -t "$SESSION":0.1 "cd ~/EliaAgent && ./scripts/start_elias_discord.sh" Enter

    sleep 1

    # Start Electron UI in pane 2 (right bottom)
    tmux send-keys -t "$SESSION":0.2 "cd ~/EliaAgent/ui_electron && npm start" Enter
fi

# Attach to the session
TMUX= tmux attach-session -t "$SESSION"
