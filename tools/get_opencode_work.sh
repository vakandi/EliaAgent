#!/bin/bash
#
# get_opencode_work.sh - Extract OpenCode IDE work history
# Usage: ./get_opencode_work.sh [hours] (default: 10 hours)
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$ROOT/docs"

usage() {
    cat << 'EOF'
Usage: get_opencode_work.sh [hours]

Extract OpenCode prompts, opencode_run_*.log tool use, and opencode_interactive_*.log
into docs/<today>/opencode_work_HHMMSS.md.

  hours    Look back this many hours (default: 10)

Paths searched are listed in OPENCODE_SEARCH_LOCATIONS in this script (EliaAI/logs,
sibling project .tmp dirs, etc.).
EOF
}

case "${1:-}" in
    -h|--help) usage; exit 0 ;;
esac

# ============================================================================
# Multi-location search for OpenCode sessions
# Now uses `opencode session list` which shows ALL sessions across all folders!
# ============================================================================
OPENCODE_SEARCH_LOCATIONS=(
    "$ROOT/logs"                                    # EliaAI main logs (fallback)
)

# Helper function to find files across all locations (portable, no mapfile)
find_opencode_files() {
    local pattern="$1"
    local temp_file="/tmp/opencode_files_$$.txt"
    > "$temp_file"
    for loc in "${OPENCODE_SEARCH_LOCATIONS[@]}"; do
        if [[ -d "$loc" ]]; then
            find "$loc" -maxdepth 3 -name "$pattern" -type f 2>/dev/null >> "$temp_file"
        fi
    done
    cat "$temp_file"
    rm -f "$temp_file"
}

HOURS="${1:-10}"
CUTOFF_EPOCH=$(date -j -v-${HOURS}H +%s 2>/dev/null || date -d "${HOURS} hours ago" +%s)
CUTOFF_DATE=$(date -j -v-${HOURS}H +"%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "${HOURS} hours ago" +"%Y-%m-%d %H:%M:%S")

DAY_DIR="$DOCS_DIR/$(date +%Y-%m-%d)"
mkdir -p "$DAY_DIR"
OUT="$DAY_DIR/opencode_work_$(date +%H%M%S).md"

TEMP_DIR=$(mktemp -d)
SESSIONS_FILE="$TEMP_DIR/sessions.txt"

trap 'rm -rf "$TEMP_DIR"' EXIT

> "$SESSIONS_FILE"

echo "OpenCode Work Extraction" | tee "$OUT"
echo "Since: $CUTOFF_DATE (${HOURS}h)" | tee -a "$OUT"
echo "Using: opencode session list (retrieves ALL sessions from ALL folders)" | tee -a "$OUT"
echo "" | tee -a "$OUT"

# ============================================================================
# 1. GET ALL SESSIONS FROM ALL FOLDERS USING opencode session list
# ============================================================================
echo "Fetching OpenCode sessions..." | tee -a "$OUT"

OPENCODE_BIN="${HOME}/.opencode/bin/opencode"
SESSION_LIST=$("$OPENCODE_BIN" session list 2>/dev/null) || SESSION_LIST=""

if [[ -z "$SESSION_LIST" ]]; then
    echo "No sessions found" | tee -a "$OUT"
else
    # Just get all sessions - skip time filtering for simplicity
    echo "$SESSION_LIST" | tail -n +2 | while IFS= read -r line; do
        session_id=$(echo "$line" | awk '{print $1}' | tr -d '\n')
        [[ -z "$session_id" ]] && continue
        title=$(echo "$line" | cut -d'|' -f2 | sed 's/|$//' | xargs | cut -c1-60)
        echo "## $session_id" >> "$SESSIONS_FILE"
        echo "$title" >> "$SESSIONS_FILE"
        echo "" >> "$SESSIONS_FILE"
    done
    
    session_count=$(wc -l < "$SESSIONS_FILE")
    session_count=$((session_count / 3))  # Each session takes 3 lines
    echo "Found $session_count session(s)" | tee -a "$OUT"
    
    # Output sessions to main file
    echo "" | tee -a "$OUT"
    echo "## Sessions" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
    cat "$SESSIONS_FILE" | tee -a "$OUT"
fi

echo "" | tee -a "$OUT"

# ============================================================================
# 2. EXTRACT BASH COMMANDS AND FILE EDITS FROM opencode_run_*.log (all locations)
# ============================================================================
echo "" | tee -a "$OUT"
echo "Extracting bash commands and file edits..." | tee -a "$OUT"

PYTHON_JSON_SCRIPT=$(cat << 'PYEOF'
import sys, json
log_file = sys.argv[1]
try:
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                if d.get('type') == 'tool_use':
                    part = d.get('part', {})
                    tool = part.get('tool', '')
                    inp = part.get('state', {}).get('input', {})
                    if tool == 'bash':
                        cmd = inp.get('command', '')
                        if cmd:
                            print('CMD: ' + cmd[:200])
                    elif tool in ('edit', 'write'):
                        path = inp.get('filePath', '')
                        if path:
                            print('EDIT: ' + tool + ' ' + path)
            except: pass
except: pass
PYEOF
)

RUN_LOG_COUNT=0
while IFS= read -r run_log; do
    [[ -z "$run_log" ]] && continue
    file_epoch=$(stat -f %m "$run_log" 2>/dev/null || stat -c %Y "$run_log" 2>/dev/null)
    
    if [[ $file_epoch -ge $CUTOFF_EPOCH ]]; then
        echo "$PYTHON_JSON_SCRIPT" | python3 /dev/stdin "$run_log" >> "$BASH_CMDS_FILE" 2>/dev/null || true
        ((RUN_LOG_COUNT++))
    fi
done < <(find_opencode_files "opencode_run_*.log")

grep "^EDIT:" "$BASH_CMDS_FILE" >> "$FILE_EDITS_FILE" 2>/dev/null || true
grep -v "^EDIT:" "$BASH_CMDS_FILE" > "${BASH_CMDS_FILE}.tmp" 2>/dev/null || true
mv "${BASH_CMDS_FILE}.tmp" "$BASH_CMDS_FILE"

bash_count=$(grep -c "^CMD:" "$BASH_CMDS_FILE" 2>/dev/null || echo 0)
edit_count=$(grep -c "^EDIT:" "$FILE_EDITS_FILE" 2>/dev/null || echo 0)
echo "Found $bash_count bash command(s), $edit_count file edit(s) from $RUN_LOG_COUNT log(s)" | tee -a "$OUT"

# ============================================================================
# 3. EXTRACT AI RESPONSES FROM opencode_interactive_*.log (all locations)
# ============================================================================
echo "" | tee -a "$OUT"
echo "Extracting AI responses..." | tee -a "$OUT"

PYTHON_AI_SCRIPT=$(cat << 'PYEOF'
import sys, re
log_file = sys.argv[1]
try:
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    ansi = re.compile(r'\x1b\[[0-9;]*m')
    content = ansi.sub('', content)
    content = re.sub(r'\[38;[0-9;]*m', '', content)
    lines = content.split('\n')
    results = []
    seen = set()
    in_thinking = False
    
    for line in lines:
        s = line.strip()
        if not s: continue
        
        # Track thinking block
        if 'Thinking:' in s:
            in_thinking = True
            continue
        if '└─' in s or '→' in s:
            in_thinking = False
            continue
        if in_thinking: continue
        
        # Skip tool outputs and metadata
        if any(x in s for x in ['<path>', '<type>', '<content>', '│', '┃', 'big-pickle', 'Sisyphus']): continue
        if 'http' in s[:60]: continue
        # Extract from timestamped lines only
        m = re.match(r'^\[[\d:T\-]+\]\s+(.*)$', s)
        if m:
            part = m.group(1).strip()
            # Skip if too short or too long
            if len(part) < 50 or len(part) > 600: continue
            # Skip file content (lines starting with number)
            if re.match(r'^\d+:', part): continue
            # Skip markdown headers and list items
            if s.startswith('#'): continue
            if re.match(r'^\d+\.\s', part): continue
            # Skip internal processing
            skip_patterns = ['thinking:', "here's my", 'let me', "i'll", 'i will', "i'm"]
            if any(x in part.lower() for x in skip_patterns): continue
            if part not in seen:
                seen.add(part)
                results.append(part[:500])
    
    if results:
        for r in results[:10]:
            print(r)
    else:
        print('(No responses)')
except:
    print('(Error)')
PYEOF
)

INT_LOG_COUNT=0
session_count=0
while IFS= read -r interactive_log; do
    [[ -z "$interactive_log" ]] && continue
    file_epoch=$(stat -f %m "$interactive_log" 2>/dev/null || stat -c %Y "$interactive_log" 2>/dev/null)
    
    if [[ $file_epoch -ge $CUTOFF_EPOCH ]]; then
        ((session_count++))
        ((INT_LOG_COUNT++))
        filename=$(basename "$interactive_log")
        session_id=$(echo "$filename" | sed -n 's/opencode_interactive_\([0-9]*\)_\([0-9]*\)\.log/ses_\1\2/p')
        source_folder=$(dirname "$interactive_log" | xargs basename)
        echo "=== SESSION: $session_id ($source_folder) ===" >> "$AI_FILE"
        echo "$PYTHON_AI_SCRIPT" | python3 /dev/stdin "$interactive_log" >> "$AI_FILE" 2>/dev/null || echo "(No responses)" >> "$AI_FILE"
        echo "" >> "$AI_FILE"
    fi
done < <(find_opencode_files "opencode_interactive_*.log")

echo "Processed $session_count session(s) from $INT_LOG_COUNT log(s)" | tee -a "$OUT"

# ============================================================================
# 4. GENERATE FINAL OUTPUT
# ============================================================================
echo "" | tee -a "$OUT"
echo "================================" | tee -a "$OUT"
echo "" | tee -a "$OUT"

session_count=$(grep -c "^=== SESSION:" "$SESSIONS_FILE" 2>/dev/null || true)
prompt_count=$(grep -c "^=== PROMPT:" "$PROMPTS_FILE" 2>/dev/null || true)
total_sessions=${session_count:-0}
total_sessions=$((total_sessions + ${prompt_count:-0}))

cat >> "$OUT" << 'ENDHEADER'
# OpenCode Work Summary

> **📎 See also**: [[../wiki/businesses/CoBou-Agency|CoBou Agency]] | [[../wiki/topics/CoBou-Agency-Timeline|CoBou Timeline]] | [[../wiki/businesses/Bene2Luxe|Bene2Luxe]] | [[../wiki/businesses/ZovaBoost|ZovaBoost]] | [[../wiki/topics/Infrastructure-Timeline|Infrastructure]] | [[../wiki/tools/MCP-Tools|MCP Tools]]

ENDHEADER

echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  " >> "$OUT"
echo "**Since:** $CUTOFF_DATE (${HOURS}h)  " >> "$OUT"
echo "**Sessions:** $total_sessions" >> "$OUT"
echo "" >> "$OUT"
echo "---" >> "$OUT"
echo "" >> "$OUT"

# Output prompts first
if [[ -f "$PROMPTS_FILE" ]] && [[ -s "$PROMPTS_FILE" ]]; then
    while IFS= read -r line; do
        if echo "$line" | grep -q "^=== PROMPT:"; then
            sid=$(echo "$line" | sed 's/=== PROMPT: //' | sed 's/ ===//')
            echo "## PROMPT: $sid" >> "$OUT"
            echo "" >> "$OUT"
        else
            content=$(echo "$line" | head -c 1000 | tr '\n' ' ')
            if [[ -n "$content" ]]; then
                echo "**Prompt:** \"$content\"" >> "$OUT"
                echo "" >> "$OUT"
            fi
        fi
    done < "$PROMPTS_FILE"
    echo "---" >> "$OUT"
    echo "" >> "$OUT"
fi

# Output sessions with their AI responses
if [[ -f "$AI_FILE" ]] && [[ -s "$AI_FILE" ]]; then
    while IFS= read -r line; do
        if echo "$line" | grep -q "^=== SESSION:"; then
            sid=$(echo "$line" | sed 's/=== SESSION: //' | sed 's/ ===//')
            echo "## SESSION: $sid" >> "$OUT"
            echo "" >> "$OUT"
        elif [[ -n "$line" ]] && [[ "$line" != "(No responses)" ]]; then
            echo "$line" | head -c 500 >> "$OUT"
            echo "" >> "$OUT"
        fi
    done < "$AI_FILE"
    echo "---" >> "$OUT"
    echo "" >> "$OUT"
fi

# Output bash commands if any
if [[ -f "$BASH_CMDS_FILE" ]] && [[ -s "$BASH_CMDS_FILE" ]]; then
    echo "## Bash Commands" >> "$OUT"
    echo "" >> "$OUT"
    grep "^CMD:" "$BASH_CMDS_FILE" 2>/dev/null | head -30 | sed 's/^CMD: /- `/' | sed 's/$/`/' >> "$OUT"
    echo "" >> "$OUT"
fi

# Output file edits if any
if [[ -f "$FILE_EDITS_FILE" ]] && [[ -s "$FILE_EDITS_FILE" ]]; then
    echo "## File Edits" >> "$OUT"
    echo "" >> "$OUT"
    grep "^EDIT:" "$FILE_EDITS_FILE" 2>/dev/null | head -20 | while IFS= read -r line; do
        tool=$(echo "$line" | awk '{print $2}')
        path=$(echo "$line" | awk '{print $3}')
        echo "- \`$path\` ($tool)" >> "$OUT"
    done
    echo "" >> "$OUT"
fi

# Summary
echo "## Summary" >> "$OUT"
echo "" >> "$OUT"
echo "| Metric | Count |" >> "$OUT"
echo "|--------|-------|" >> "$OUT"
echo "| Sessions | $total_sessions |" >> "$OUT"
echo "| Bash Commands | $bash_count |" >> "$OUT"
echo "| File Edits | $edit_count |" >> "$OUT"
echo "" >> "$OUT"
echo "*Generated: $(date '+%Y-%m-%d %H:%M:%S')*" >> "$OUT"

# Size check
SIZE=$(wc -c < "$OUT")
SIZE_KB=$((SIZE / 1024))
echo "" | tee -a "$OUT"
echo "Output size: ${SIZE_KB}KB" | tee -a "$OUT"
if [[ $SIZE_KB -gt 100 ]]; then
    echo "WARNING: Output exceeds 100KB" | tee -a "$OUT"
elif [[ $SIZE_KB -gt 50 ]]; then
    echo "NOTE: Output exceeds 50KB target" | tee -a "$OUT"
else
    echo "OK: Within 50KB target" | tee -a "$OUT"
fi

echo "" | tee -a "$OUT"
echo "Saved to: $OUT" | tee -a "$OUT"
