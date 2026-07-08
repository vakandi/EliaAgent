#!/bin/bash
# Bene2Luxe - Batch Video Generation Script
# ===========================================
# Usage: bash generate_batch.sh [PRODUCT_TYPE] [COUNT]
# Example: bash generate_batch.sh chanel 50

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/generated"
PROMPTS_DIR="$SCRIPT_DIR/batch-prompts"
LOG_FILE="$SCRIPT_DIR/generation.log"

# Models
MODEL="${MODEL:-kling-3}"
DURATION="${DURATION:-10}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${YELLOW}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check credentials
check_credentials() {
    if [ -z "$HF_CREDENTIALS" ]; then
        error "HF_CREDENTIALS not set. Run: export HF_CREDENTIALS='KEY_ID:KEY_SECRET'"
    fi
    info "Credentials loaded"
}

# Check Python dependencies
check_dependencies() {
    info "Checking dependencies..."
    python3 -c "import higgsfield_client" 2>/dev/null || {
        info "Installing higgsfield-client..."
        pip3 install higgsfield-client requests pillow --break-system-packages
    }
    success "Dependencies OK"
}

# Generate single video
generate_video() {
    local prompt="$1"
    local output="$2"
    local model="${3:-$MODEL}"
    
    info "Generating: ${prompt:0:50}..."
    
    python3 "$SCRIPT_DIR/higgfields_master.py" \
        video \
        --prompt "$prompt" \
        --output "$output" \
        --model "$model" \
        --duration "$DURATION" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        success "Generated: $output"
        return 0
    else
        error "Failed: $prompt"
        return 1
    fi
}

# Generate from file
generate_from_file() {
    local file="$1"
    local count="${2:-10}"
    local model="${3:-$MODEL}"
    
    if [ ! -f "$file" ]; then
        error "File not found: $file"
    fi
    
    local prompts=()
    while IFS= read -r line; do
        [ -n "$line" ] && prompts+=("$line")
    done < "$file"
    
    info "Found ${#prompts[@]} prompts in $file"
    
    local success_count=0
    local fail_count=0
    
    for i in "${!prompts[@]}"; do
        if [ $i -ge $count ]; then
            info "Reached count limit: $count"
            break
        fi
        
        local output="$OUTPUT_DIR/video_$(printf '%03d' $((i+1)))_$(date +%s).mp4"
        
        if generate_video "${prompts[$i]}" "$output" "$model"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
        
        # Rate limiting
        sleep 5
    done
    
    info "Generation complete: $success_count success, $fail_count failed"
}

# Generate mascott episodes
generate_mascott_batch() {
    local start_ep="${1:-1}"
    local end_ep="${2:-25}"
    local model="${3:-$MODEL}"
    
    info "Generating mascott episodes $start_ep to $end_ep..."
    
    local success_count=0
    local fail_count=0
    
    for ep in $(seq "$start_ep" "$end_ep"); do
        local output="$OUTPUT_DIR/mascott_ep$(printf '%02d' $ep)_$(date +%s).mp4"
        
        info "Episode $ep..."
        
        python3 "$SCRIPT_DIR/higgfields_master.py" \
            mascott \
            --episode "$ep" \
            --output "$output" \
            --model "$model" \
            >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            success "Episode $ep generated"
            ((success_count++))
        else
            error "Episode $ep failed"
            ((fail_count++))
        fi
        
        sleep 10
    done
    
    info "Mascoot batch complete: $success_count success, $fail_count failed"
}

# Show status
show_status() {
    info "=== Generation Status ==="
    info "Output directory: $OUTPUT_DIR"
    info "Model: $MODEL"
    info "Duration: ${DURATION}s"
    
    if [ -d "$OUTPUT_DIR" ]; then
        local total=$(find "$OUTPUT_DIR" -name "*.mp4" | wc -l)
        info "Videos generated: $total"
    fi
    
    if [ -f "$LOG_FILE" ]; then
        info "Log file: $LOG_FILE"
        local lines=$(wc -l < "$LOG_FILE")
        info "Log lines: $lines"
    fi
}

# Help
show_help() {
    cat << EOF
Bene2Luxe Video Generation Script
================================

Usage: bash generate_batch.sh [COMMAND] [OPTIONS]

Commands:
    video <prompt> <output>    Generate single video
    file <file> [count]        Generate from prompts file
    mascott <start> <end>       Generate mascott episodes
    status                      Show generation status
    help                       Show this help

Environment Variables:
    HF_CREDENTIALS             Your Higgsfield API credentials
    MODEL                      Model to use (default: kling-3)
    DURATION                  Video duration in seconds (default: 10)

Examples:
    # Single video
    HF_CREDENTIALS="key:secret" bash generate_batch.sh video "luxury sneakers" output.mp4
    
    # Batch from file
    HF_CREDENTIALS="key:secret" bash generate_batch.sh file prompts.txt 50
    
    # Mascoot episodes 1-25
    HF_CREDENTIALS="key:secret" bash generate_batch.sh mascott 1 25
    
    # Check status
    bash generate_batch.sh status

EOF
}

# Main
main() {
    local command="${1:-help}"
    
    log "Starting batch generation script"
    check_credentials
    check_dependencies
    
    case "$command" in
        video)
            generate_video "$2" "$3" "$4"
            ;;
        file)
            generate_from_file "$2" "$3" "$4"
            ;;
        mascott)
            generate_mascott_batch "$2" "$3" "$4"
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            ;;
    esac
}

main "$@"
