#!/bin/zsh
# =============================================================================
# DEPRECATED — DO NOT USE
#
# This was an AI-generated 4-window version created on May 2, 2026 that BROKE
# YourName's original 3-pane tmux setup. It introduced start_agents.sh into the
# UI launcher which caused problems.
#
# The correct launcher is EliaUI.command which uses 3 panes:
#   Pane 0: OpenCode server
#   Pane 1: Discord bot
#   Pane 2: UI Electron
#
# Kept only for reference. Delete when no one remembers this existed.
# =============================================================================

# Window 1: OpenCode server (opencode-serve.sh)
# Window 2: CodeMem Viewer (codemem-viewer.sh)
# Window 3: Agents (start_agents.sh)  ← WRONG, should not be here
# Window 4: UI (elia-ui.sh)

set -euo pipefail

AGENT_DIR="$HOME/EliaAI"
SCRIPTS_DIR="$AGENT_DIR/scripts"

# Kill any existing tmux session
tmux kill-session -t elia 2>/dev/null || true
sleep 1

# Create new tmux session with window 1 (OpenCode server)
echo "Creating tmux session 'elia' with 4 windows..."
tmux new-session -d -s elia -n "opencode" "bash $SCRIPTS_DIR/opencode-serve.sh 4096"

# Create window 2 (CodeMem Viewer)
tmux new-window -t elia -n "codemem" "bash $SCRIPTS_DIR/codemem-viewer.sh"

# Create window 3 (Agents)
tmux new-window -t elia -n "agents" "bash $SCRIPTS_DIR/start_agents.sh"

# Create window 4 (UI)
tmux new-window -t elia -n "ui" "bash $SCRIPTS_DIR/elia-ui.sh"

# Select first window
tmux select-window -t elia:1

echo "✅ EliaUI started with 4 tmux windows:"
echo "  Window 1: OpenCode server (opencode-serve.sh)"
echo "  Window 2: CodeMem Viewer (codemem-viewer.sh)"
echo "  Window 3: Agents (start_agents.sh)"
echo "  Window 4: UI (elia-ui.sh)"
echo ""
echo "Attach with: tmux attach -t elia"
echo "Switch windows: Ctrl-b 1, Ctrl-b 2, Ctrl-b 3, Ctrl-b 4"

# Attach to tmux session
tmux attach -t elia
