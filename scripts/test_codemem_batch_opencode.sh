#!/usr/bin/env bash
set -euo pipefail

# Script to manually test codemem batch processing with OpenCode Zen (big-pickle)
# This bypasses the observer client and directly tests the LLM call

CODENEM_DIR="/path/to/EliaAI/integrations/codemem"
DB_PATH="/home/user/.codemem/mem.sqlite"
LOG_FILE="/path/to/EliaAI/logs/codemem_batch_test.log"

echo "=== CodeMem Batch Test with OpenCode Zen ===" | tee -a "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo ""

# Step 1: Check if there are pending batches
echo "=== Step 1: Check pending batches ===" | tee -a "$LOG_FILE"
PENDING=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM raw_event_flush_batches WHERE status='pending';" 2>&1)
echo "Pending batches: $PENDING" | tee -a "$LOG_FILE"

if [ "$PENDING" -eq 0 ]; then
    echo "No pending batches. Resetting failed batches..." | tee -a "$LOG_FILE"
    sqlite3 "$DB_PATH" "UPDATE raw_event_flush_batches SET status='pending', attempt_count=0, error_message=NULL, observer_error_message=NULL WHERE status IN ('failed', 'gave_up');" 2>&1 | tee -a "$LOG_FILE"
fi

# Step 2: Get the first pending batch
echo -e "\n=== Step 2: Get first pending batch ===" | tee -a "$LOG_FILE"
BATCH_INFO=$(sqlite3 "$DB_PATH" "SELECT id, source, start_event_seq, end_event_seq, observer_provider, observer_model FROM raw_event_flush_batches WHERE status='pending' ORDER BY id LIMIT 1;" 2>&1)
echo "Batch info: $BATCH_INFO" | tee -a "$LOG_FILE"

BATCH_ID=$(echo "$BATCH_INFO" | cut -d'|' -f1)
if [ -z "$BATCH_ID" ]; then
    echo "ERROR: No batch found!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "Testing batch ID: $BATCH_ID" | tee -a "$LOG_FILE"

# Step 3: Get raw events for this batch
echo -e "\n=== Step 3: Get raw events ===" | tee -a "$LOG_FILE"
START_SEQ=$(echo "$BATCH_INFO" | cut -d'|' -f3)
END_SEQ=$(echo "$BATCH_INFO" | cut -d'|' -f4)

EVENTS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM raw_events WHERE seq >= $START_SEQ AND seq <= $END_SEQ;" 2>&1)
echo "Events in batch: $EVENTS" | tee -a "$LOG_FILE"

# Step 4: Test OpenCode Zen API call directly
echo -e "\n=== Step 4: Test OpenCode Zen API (big-pickle) ===" | tee -a "$LOG_FILE"

# Check if OpenCode has a local API endpoint
echo "Checking for OpenCode API endpoints..." | tee -a "$LOG_FILE"
for PORT in 3000 5000 63731 38888 8080; do
    if lsof -i :$PORT 2>/dev/null | grep -q LISTEN; then
        echo "  Port $PORT: LISTENING" | tee -a "$LOG_FILE"
    fi
done

# Step 5: Try to call OpenCode Zen via opencode CLI
echo -e "\n=== Step 5: Test OpenCode CLI call ===" | tee -a "$LOG_FILE"

# Create a simple test prompt
TEST_PROMPT="Reply with just: HELLO_TEST"
SYSTEM_PROMPT="You are a test assistant."

echo "Testing OpenCode CLI with big-pickle model..." | tee -a "$LOG_FILE"
echo "Command: echo '$TEST_PROMPT' | opencode run --model big-pickle --agent elia" | tee -a "$LOG_FILE"

# Try to use opencode to make a direct LLM call
# Since OpenCode Zen doesn't need API key, we can test directly
opencode run --model big-pickle "Reply with just: HELLO_TEST" 2>&1 | tee -a "$LOG_FILE" || echo "OpenCode CLI test failed" | tee -a "$LOG_FILE"

# Step 6: Check viewer logs for observer calls
echo -e "\n=== Step 6: Check viewer logs ===" | tee -a "$LOG_FILE"
if [ -f "/path/to/EliaAI/logs/codemem_viewer.log" ]; then
    echo "Last 50 lines of viewer log:" | tee -a "$LOG_FILE"
    tail -50 /path/to/EliaAI/logs/codemem_viewer.log 2>&1 | grep -i "observer\|batch\|openai\|big.pickle\|zen" | tee -a "$LOG_FILE" || echo "No observer-related logs" | tee -a "$LOG_FILE"
fi

echo -e "\n=== Test complete ===" | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE"
