#!/bin/zsh
# EliaAI Agent Launcher - OpenCode + NVIDIA NIM + Ralph Loop
# Now uses temporary prompt files instead of modifying PROMPT.md

set -euo pipefail

# Configuration - dynamic path detection
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
TRIGGER_SCRIPT="${AGENT_DIR}/scripts/trigger_opencode_interactive.sh"
PROMPT_FILE="${AGENT_DIR}/PROMPT.md"
AGENT_PAYLOADS_DIR="${AGENT_DIR}/.agent_payloads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Show usage
show_usage() {
    echo "Usage: $0 [--extra-prompt=\"your message here\"] [--model=big-pickle|minimax|nvidia|nemotron|mimo] [--proxy]"
    echo ""
    echo "Options:"
    echo "  --extra-prompt=\"message\"  Add a custom message to beginning of prompt"
    echo "  --model=MODEL             Choose AI model (default: big-pickle):"
    echo "                           big-pickle- Big Pickle Free (OpenCode Zen) - DEFAULT"
    echo "                           minimax   - MiniMax M2.5 Free (no API key)"
    echo "                           nemotron  - Nemotron 3 Super Free (OpenCode Zen)"
    echo "                           mimo      - MiMo V2 Flash Free (OpenCode Zen)"
    echo "                           nvidia    - NVIDIA NIM API (requires API key)"
    echo "  --proxy                   Run opencode through proxychains4"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "OpenCode Zen Free Models:"
    echo "  - Big Pickle (stable, reliable) - DEFAULT"
    echo "  - MiniMax M2.5 (fast, recent)"
    echo "  - Nemotron 3 Super (advanced reasoning)"
    echo "  - MiMo V2 Flash (ultra-fast)"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 --extra-prompt=\"Urgent: Fix payment gateway issue\""
    echo "  $0 --model=minimax"
    echo "  $0 --model=nemotron --extra-prompt=\"Complex reasoning task\""
    echo "  $0 --model=nvidia --extra-prompt=\"Need NVIDIA\"  # NVIDIA with API key"
    echo "  $0 --proxy --extra-prompt=\"Run through proxy\"  # With proxy enabled"
}

# Parse command line arguments
EXTRA_PROMPT=""
MODEL="big-pickle"
USE_PROXY=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --extra-prompt=*)
            EXTRA_PROMPT="${1#*=}"
            shift
            ;;
        --model=*)
            MODEL="${1#*=}"
            shift
            ;;
        --proxy)
            USE_PROXY=1
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate model choice
if [[ "$MODEL" != "nvidia" && "$MODEL" != "minimax" && "$MODEL" != "big-pickle" && "$MODEL" != "nemotron" && "$MODEL" != "mimo" ]]; then
    warning "Unknown model: $MODEL. Using default: big-pickle"
    MODEL="big-pickle"
fi

# Create agent payloads directory if it doesn't exist
mkdir -p "$AGENT_PAYLOADS_DIR"

# Check if trigger script exists
if [[ ! -f "$TRIGGER_SCRIPT" ]]; then
    error "trigger_opencode_interactive.sh not found at: $TRIGGER_SCRIPT"
    exit 1
fi

# Check if trigger script is executable
if [[ ! -x "$TRIGGER_SCRIPT" ]]; then
    log "Making trigger_opencode_interactive.sh executable..."
    chmod +x "$TRIGGER_SCRIPT"
fi

# Create temporary prompt file if extra prompt is provided
if [[ -n "$EXTRA_PROMPT" ]]; then
    log "Creating temporary prompt file with extra context..."
    
    # Create timestamped prompt file
    TIMESTAMPED_PROMPT="${AGENT_PAYLOADS_DIR}/prompt_$(date +%Y%m%d_%H%M%S).txt"
    
    # Write the extra context to the temporary file only
    cat > "$TIMESTAMPED_PROMPT" << EOF
# 🚨 VOICE COMMAND - $(date '+%Y-%m-%d %H:%M:%S')

$EXTRA_PROMPT

EOF
    
    success "Temporary prompt created: $TIMESTAMPED_PROMPT"
    
    # Set the extra prompt file as environment variable for the trigger script
    export EXTRA_PROMPT_FILE="$TIMESTAMPED_PROMPT"
else
    log "Running without extra prompt context"
fi

# Check dependencies
log "Checking dependencies..."

# Check OpenCode CLI
if command -v opencode &> /dev/null; then
    log "OpenCode CLI found: $(which opencode)"
    OPENCODE_BIN="$(which opencode)"
else
    error "OpenCode CLI not found. Please install it first."
    exit 1
fi

# Check OpenCode version
if command -v opencode &> /dev/null; then
    log "OpenCode version: $(opencode --version 2>&1 | head -1)"
fi

# Check oh-my-opencode
if command -v oh-my-opencode &> /dev/null; then
    log "oh-my-opencode found: $(oh-my-opencode --version 2>&1 | head -1)"
fi

# Check NVIDIA NIM API key (in env var or settings.json) - only if using NVIDIA model
settings_file="${HOME}/.config/opencode/settings.json"
api_key_found=false

if [[ "$MODEL" == "nvidia" ]]; then
    if [[ -f "$settings_file" ]] && grep -q "apiKey.*nvapi-" "$settings_file" 2>/dev/null; then
        api_key_found=true
    fi

    if [[ -n "${NVIDIA_NIM_API_KEY:-}" ]] || [[ "$api_key_found" == "true" ]]; then
        log "NVIDIA NIM API key configured"
    else
        warning "NVIDIA_NIM_API_KEY not set. Get key from: https://build.nvidia.com/moonshotai/kimi-k2.5/deploy"
    fi
fi

# Check API key requirements
if [[ "$MODEL" == "nvidia" ]]; then
    log "Using NVIDIA NIM API (requires API key)..."
else
    log "Using $MODEL (OpenCode Zen free model)"
fi

# Check ULW/Ralph toggle state from ui_electron config
# ULW is DEFAULT - only Ralph mode uses a marker file
RALPH_MODE_FILE="${AGENT_DIR}/.ralph_mode"
if [[ -f "$RALPH_MODE_FILE" ]]; then
    log "RALPH loop mode active (via ui_electron toggle)"
else
    log "ULW-LOOP mode is ENABLED by DEFAULT (no .ralph_mode file)"
fi

# Execute trigger script which respects ULW/ralph toggle
# trigger_opencode_interactive.sh will check .ulw_mode and use appropriate loop
export USE_PROXY="$USE_PROXY"
if [[ "$USE_PROXY" == "1" ]]; then
    log "Proxy mode enabled (proxychains4)"
fi

if [[ -n "${EXTRA_PROMPT_FILE:-}" ]]; then
    EXTRA_CONTENT=$(cat "$EXTRA_PROMPT_FILE")
    "$TRIGGER_SCRIPT" "$EXTRA_CONTENT"
else
    "$TRIGGER_SCRIPT"
fi

EXIT_CODE=$?

echo ""
echo "=========================================="
if [[ $EXIT_CODE -eq 0 ]]; then
    success "✅ Agent system completed successfully"
else
    warning "⚠️  Agent system completed with exit code: $EXIT_CODE"
fi
echo "=========================================="

# Clean up temporary prompt file
if [[ -n "${EXTRA_PROMPT_FILE:-}" && -f "$EXTRA_PROMPT_FILE" ]]; then
    rm -f "$EXTRA_PROMPT_FILE"
    log "Temporary prompt file cleaned up: $EXTRA_PROMPT_FILE"
fi

# Exit with same code as trigger script
exit $EXIT_CODE
