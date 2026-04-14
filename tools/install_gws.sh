#!/bin/bash
# Google Workspace CLI Installer
# Run this script to install the gws command

echo "🚀 Google Workspace CLI Installer"
echo "========================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script needs sudo privileges to install to /usr/local/bin"
    echo "Please run: sudo ./tools/install_gws.sh"
    exit 1
fi

# Create the gws script
cat > /usr/local/bin/gws << 'EOF'
#!/bin/bash
# Google Workspace CLI Wrapper
# Usage: gws [command] [args...]

SCRIPT_DIR="/Users/vakandi/EliaAI/tools"
PYTHON_SCRIPT="$SCRIPT_DIR/google_workspace.py"

# Function to show usage
show_usage() {
    echo "Google Workspace CLI - Working APIs (Calendar & Tasks)"
    echo ""
    echo "Usage: gws [command] [arguments]"
    echo ""
    echo "Commands:"
    echo "  create-event 'Summary' 'Description'  Create calendar event"
    echo "  create-task 'Title' 'Notes'       Create task"
    echo "  list-events                      List upcoming events"
    echo "  list-tasks                       List tasks"
    echo "  help                             Show this help"
    echo ""
    echo "Examples:"
    echo "  gws create-event 'Team Meeting' 'Discuss project progress'"
    echo "  gws create-task 'Review code' 'Check pull requests'"
    echo "  gws list-events"
    echo "  gws list-tasks"
    echo ""
    echo "Note: Uses service account - Calendar & Tasks sync to your phone!"
    echo "      Docs/Drive require OAuth for personal Gmail accounts"
}

# Parse command
case "$1" in
    create-event)
        if [ $# -lt 2 ]; then
            echo "Error: create-event requires summary and description"
            echo "Usage: gws create-event 'Summary' 'Description'"
            exit 1
        fi
        python3 "$PYTHON_SCRIPT" create-event "$2" "$3"
        ;;
    create-task)
        if [ $# -lt 2 ]; then
            echo "Error: create-task requires title"
            echo "Usage: gws create-task 'Title' [Notes]"
            exit 1
        fi
        python3 "$PYTHON_SCRIPT" create-task "$2" "$3"
        ;;
    list-events)
        python3 "$PYTHON_SCRIPT" list-events
        ;;
    list-tasks)
        python3 "$PYTHON_SCRIPT" list-tasks
        ;;
    help|--help|-h)
        show_usage
        ;;
    "")
        show_usage
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo "Run 'gws help' for usage information"
        exit 1
        ;;
esac
EOF

# Make executable
chmod 755 /usr/local/bin/gws

echo "✅ Installed gws command to /usr/local/bin/gws"
echo "📅 Calendar & Tasks APIs ready - events/tasks sync to your phone!"
echo ""
echo "Usage examples:"
echo "  gws create-event 'Meeting Title' 'Description'"
echo "  gws create-task 'Task Title' 'Notes'"
echo "  gws list-events"
echo "  gws list-tasks"
echo ""
echo "Run 'gws help' for full usage information"

# Verify installation
if command -v gws >/dev/null 2>&1; then
    echo "✅ Installation verified - gws command working!"
else
    echo "⚠️  Installation completed but verification failed"
fi
EOF
