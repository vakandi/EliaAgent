#!/bin/zsh
set -euo pipefail
IFS=$'\n\t'

# =============================================================================
# EliaUI — Tmux launcher for Elia AI development environment
#
# Creates a single tmux session "elia" with 3 panes in one window:
#   Pane 0: OpenCode server (port 4096)
#   Pane 1: Discord bot (start_elias_discord.sh)
#   Pane 2: UI Electron (npm start)
#
# History: DO NOT CHANGE TO 4 WINDOWS. Original by Wael was always 3 panes.
# An AI agent broke it to 4 windows on May 2 which caused start_agents.sh to
# leak into the UI launcher. See git log if you're tempted to "improve" this.
# =============================================================================

SCRIPT_DIR="$HOME/EliaAI/scripts"
LOG_DIR="$HOME/EliaAI/logs"
SESSION_NAME="elia"

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [EliaUI] $*" >&2
}

log "=== EliaUI 3-Pane Tmux Launcher ==="

# Check tmux is installed
if ! command -v tmux &>/dev/null; then
    log "ERROR: tmux not found in PATH"
    exit 1
fi

mkdir -p "$LOG_DIR" 2>/dev/null || true

# If session already exists, just attach — don't kill and recreate
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    log "Session '$SESSION_NAME' already exists — attaching"
    exec tmux attach -t "$SESSION_NAME"
fi

log "Creating new tmux session: $SESSION_NAME"

# Create session with 1 window
tmux new-session -d -s "$SESSION_NAME" -n "Elia"
sleep 0.3

# Split into 3 panes: horizontal split first, then vertical split on left
# Layout after splits:
#   ┌─────────────────┬──────────────┐
#   │  Pane 0         │  Pane 1      │
#   │  opencode-serve │  discord     │
#   ├─────────────────┘              │
#   │  Pane 2         │              │
#   │  UI Electron    │              │
#   └─────────────────┴──────────────┘

# Split horizontally (creates pane 1 on the right, 50% width)
tmux split-window -h -t "$SESSION_NAME:0"
sleep 0.2

# Split pane 0 vertically (creates pane 2 below pane 0)
tmux split-window -v -t "$SESSION_NAME:0.0"
sleep 0.2

# Resize pane 2 (bottom-left) to be small — just shows UI logs
tmux resize-pane -t "$SESSION_NAME:0.2" -y 8
sleep 0.1

# Pane 0: OpenCode Server (top-left)
log "Starting OpenCode Server in Pane 0"
tmux send-keys -t "$SESSION_NAME:0.0" "bash $SCRIPT_DIR/opencode-serve.sh 4096" Enter

# Pane 1: Discord bot (right)
log "Starting Discord bot in Pane 1"
tmux send-keys -t "$SESSION_NAME:0.1" "bash $SCRIPT_DIR/start_elias_discord.sh" Enter

# Pane 2: UI Electron (bottom-left, small pane)
log "Starting UI Electron in Pane 2"
tmux send-keys -t "$SESSION_NAME:0.2" "cd ~/EliaAI/ui_electron && npm start" Enter

# Select pane 0 and attach
log "Attaching to session..."
tmux select-pane -t "$SESSION_NAME:0.0"
exec tmux attach -t "$SESSION_NAME"
