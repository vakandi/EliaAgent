#!/bin/bash

# get_windsurf_work.sh - Extract Windsurf IDE work history including file edits, tools, and MCP calls
# Usage: ./get_windsurf_work.sh [time_duration]
# Examples: ./get_windsurf_work.sh 5m (last 5 minutes)
#           ./get_windsurf_work.sh 1h (last 1 hour)
#           ./get_windsurf_work.sh 48h (last 48 hours)

set -e

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib_ide_utils.sh"

# Output under docs/YYYY-MM-DD/
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="${DOCS_DIR:-$ROOT/docs}"
DAY_DIR="$DOCS_DIR/$(date +%Y-%m-%d)"
mkdir -p "$DAY_DIR"

# Use library for time filtering - get last run timestamp or default cutoff
CUTOFF_EPOCH=$(get_last_run_timestamp)
MINUTES=$(( ($(date +%s) - CUTOFF_EPOCH) / 60 ))
CUTOFF_TIME=$CUTOFF_EPOCH
CUTOFF_ISO=$(date -r "$CUTOFF_TIME" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@$CUTOFF_TIME" "+%Y-%m-%d %H:%M:%S")

OUT="$DAY_DIR/windsurf_work_$(date +%H%M%S).md"

trap 'save_last_run_timestamp' EXIT

# Windsurf paths
WINDSURF_DIR="$HOME/Library/Application Support/Windsurf"
LOG_DIR="$WINDSURF_DIR/logs"
HISTORY_DIR="$WINDSURF_DIR/User/History"

echo "# 🌊 Windsurf IDE Work Timeline" | tee "$OUT"
echo "" | tee -a "$OUT"
echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$OUT"
echo "**Time Range:** Last $((MINUTES / 60))h $((MINUTES % 60))m (since $CUTOFF_ISO)" | tee -a "$OUT"
echo "**User:** $(whoami)" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "---" | tee -a "$OUT"
echo "" | tee -a "$OUT"

echo "🔍 Scanning Windsurf data since last run ($((MINUTES / 60))h $((MINUTES % 60))m ago)..."

# Check if Windsurf directory exists
if [ ! -d "$WINDSURF_DIR" ]; then
    echo "❌ Windsurf not found at: $WINDSURF_DIR" | tee -a "$OUT"
    exit 1
fi

# Collect events
temp_file="/tmp/windsurf_events_$$.txt"
> "$temp_file"

# 1. Parse History entries.json for file edits (Cascade Edit, Open diff zone)
if [ -d "$HISTORY_DIR" ]; then
    find "$HISTORY_DIR" -name "entries.json" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read histfile; do
        # Get file modification time
        mod_time_str=$(stat -f %Sm "$histfile" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        
        if [ "$mod_epoch" -ge "$CUTOFF_TIME" ]; then
            # Parse the JSON for Cascade Edit entries
            if command -v python3 &> /dev/null; then
                python3 -c "
import json
import sys

try:
    with open('$histfile', 'r') as f:
        data = json.load(f)
    
    resource = data.get('resource', '')
    entries = data.get('entries', [])
    
    for entry in entries:
        ts = entry.get('timestamp', 0)
        if ts > ${CUTOFF_TIME}000:
            source = entry.get('source', 'unknown')
            if 'Cascade' in source or 'diff' in source.lower():
                ts_sec = int(ts / 1000)
                ts_iso = __import__('datetime').datetime.fromtimestamp(ts_sec).strftime('%Y-%m-%d %H:%M:%S')
                # Try to extract line change info
                diff_info = entry.get('diff', {})
                if isinstance(diff_info, dict):
                    old_lines = diff_info.get('oldLineCount', 0) or 0
                    new_lines = diff_info.get('newLineCount', 0) or 0
                    if old_lines or new_lines:
                        changes = f"+{new_lines}/-{old_lines}"
                        print(f"{ts_sec}|{ts_iso}|EDIT|{source}|{resource}|{changes}")
                    else:
                        print(f"{ts_sec}|{ts_iso}|EDIT|{source}|{resource}|")
                else:
                    print(f"{ts_sec}|{ts_iso}|EDIT|{source}|{resource}|")
except Exception as e:
    pass
" 2>/dev/null
            fi
        fi
    done >> "$temp_file"
fi

# 2. Parse Windsurf.log for Cascade operations and file activity
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "Windsurf.log" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read logfile; do
        # Look for Cascade operations (RevertToStep, file edits, etc.)
        grep -hE "(RevertToStep|RevertToCascadeStep|GetRevertPreview|apply_diff|file_edit|tool_call)" "$logfile" 2>/dev/null | while read line; do
            # Extract timestamp
            if [[ "$line" =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2}":[0-9]{2}:[0-9]{2}) ]]; then
                ts="${BASH_REMATCH[1]}"
                ts_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$ts" +%s 2>/dev/null || echo 0)
                if [ "$ts_epoch" -ge "$CUTOFF_TIME" ]; then
                    # Categorize the operation
                    if echo "$line" | grep -q "RevertToStep.*finished"; then
                        echo "$ts_epoch|$ts|CASCADE|File Edit/Revert Completed"
                    elif echo "$line" | grep -q "GetRevertPreview.*started"; then
                        echo "$ts_epoch|$ts|PREVIEW|Preview Diff Started"
                    elif echo "$line" | grep -q "apply_diff\|file_edit"; then
                        echo "$ts_epoch|$ts|DIFF|Applying File Changes"
                    else
                        echo "$ts_epoch|$ts|CASCADE|Cascade Operation"
                    fi
                fi
            fi
        done
        
        # Look for MCP tool calls
        grep -hE "MCP-GO.*STDIO.*SendRequest" "$logfile" 2>/dev/null | while read line; do
            if [[ "$line" =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2}":[0-9]{2}:[0-9]{2}) ]]; then
                ts="${BASH_REMATCH[1]}"
                ts_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$ts" +%s 2>/dev/null || echo 0)
                if [ "$ts_epoch" -ge "$CUTOFF_TIME" ]; then
                    # Extract tool name from JSON if present
                    if echo "$line" | grep -q '"method":"tools/call"'; then
                        tool_name=$(echo "$line" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
                        if [ -n "$tool_name" ]; then
                            echo "$ts_epoch|$ts|MCP-TOOL|MCP Tool Call: $tool_name"
                        else
                            echo "$ts_epoch|$ts|MCP-TOOL|MCP Tool Call"
                        fi
                    else
                        echo "$ts_epoch|$ts|MCP-REQ|MCP Request"
                    fi
                fi
            fi
        done
        
        # Look for MCP responses
        grep -hE "MCP-GO.*readResponses.*got line.*result" "$logfile" 2>/dev/null | while read line; do
            if [[ "$line" =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2}":[0-9]{2}:[0-9]{2}) ]]; then
                ts="${BASH_REMATCH[1]}"
                ts_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$ts" +%s 2>/dev/null || echo 0)
                if [ "$ts_epoch" -ge "$CUTOFF_TIME" ]; then
                    echo "$ts_epoch|$ts|MCP-RESP|MCP Response Received"
                fi
            fi
        done
    done >> "$temp_file"
fi

# 3. Parse ptyhost.log for terminal commands
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "ptyhost.log" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read logfile; do
        # Look for command execution
        grep -hE "(shell integration|command|execute)" "$logfile" 2>/dev/null | while read line; do
            if [[ "$line" =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2}":[0-9]{2}:[0-9]{2}) ]]; then
                ts="${BASH_REMATCH[1]}"
                ts_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$ts" +%s 2>/dev/null || echo 0)
                if [ "$ts_epoch" -ge "$CUTOFF_TIME" ]; then
                    if echo "$line" | grep -q "Shell integration DETECTED"; then
                        echo "$ts_epoch|$ts|TERMINAL|Terminal Session"
                    fi
                fi
            fi
        done
    done >> "$temp_file"
fi

# 4. Check workspaceStorage modification times
if [ -d "$WINDSURF_DIR/User/workspaceStorage" ]; then
    find "$WINDSURF_DIR/User/workspaceStorage" -name "state.vscdb" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read dbfile; do
        mod_time_str=$(stat -f %Sm "$dbfile" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        if [ "$mod_epoch" -ge "$CUTOFF_TIME" ]; then
            workspace=$(basename "$(dirname "$dbfile")")
            mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
            echo "$mod_epoch|$mod_time_fmt|WORKSPACE|Workspace: $workspace"
        fi
    done >> "$temp_file"
fi

# 5. Check globalStorage for chat activity - EXTRACT ACTUAL PROMPTS
CHAT_DATA_FILE="$WINDSURF_DIR/User/globalStorage/state.vscdb"
if [ -f "$CHAT_DATA_FILE" ]; then
    mod_time_str=$(stat -f %Sm "$CHAT_DATA_FILE" 2>/dev/null)
    mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
    if [ "$mod_epoch" -ge "$CUTOFF_TIME" ]; then
        mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
        echo "$mod_epoch|$mod_time_fmt|STORAGE|Global Storage Modified"
        
        # Extract actual chat/prompt data from SQLite
        if command -v sqlite3 &> /dev/null; then
            # Query for chat messages - Windsurf stores chat data in SQLite
            chat_json=$(sqlite3 "$CHAT_DATA_FILE" "SELECT value FROM ItemTable WHERE key LIKE '%workbench.panel.aichat%' OR key LIKE '%caside.sidebar.chat%' OR key LIKE '%aiService%' OR key LIKE '%chatData%' ORDER BY rowid DESC LIMIT 1;" 2>/dev/null)
            if [ -n "$chat_json" ] && [ "${#chat_json}" -gt 50 ]; then
                # Try to extract prompts from the JSON using Python
                echo "$chat_json" | python3 -c '
import json, sys, re
from datetime import datetime

try:
    data = json.load(sys.stdin)
    
    def extract_prompts(obj, path=""):
        prompts = []
        if isinstance(obj, dict):
            if obj.get("role") == "user" or obj.get("type") == "user":
                text = obj.get("text") or obj.get("content") or obj.get("message") or ""
                if text and len(text) > 10:
                    ts = obj.get("timestamp", 0)
                    if isinstance(ts, (int, float)):
                        if ts > 1000000000000:
                            ts = int(ts / 1000)
                    else:
                        ts = int(datetime.now().timestamp())
                    prompts.append((ts, text[:300]))
            
            for key in ["conversations", "messages", "chats", "history", "threads"]:
                if key in obj and isinstance(obj[key], list):
                    for item in obj[key]:
                        prompts.extend(extract_prompts(item, path + "." + key))
            
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    prompts.extend(extract_prompts(v, path + "." + k))
                    
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                prompts.extend(extract_prompts(item, path + "[" + str(i) + "]"))
                
        return prompts
    
    all_prompts = extract_prompts(data)
    all_prompts.sort(key=lambda x: x[0], reverse=True)
    
    for ts, prompt in all_prompts[:5]:
        print(f"{ts}|{prompt}")
except Exception as e:
    pass
' 2>/dev/null | while IFS='|' read -r ts prompt; do
                    [ -n "$prompt" ] && echo "$ts|$mod_time_fmt|PROMPT|$prompt"
                done
            fi
        fi
    fi
fi >> "$temp_file"

# 6. Extract from workspaceStorage SQLite databases (like Cursor does)
if [ -d "$WINDSURF_DIR/User/workspaceStorage" ]; then
    find "$WINDSURF_DIR/User/workspaceStorage" -name "state.vscdb" -type f 2>/dev/null | while read dbfile; do
        mod_time_str=$(stat -f %Sm "$dbfile" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        [ "$mod_epoch" -lt "$CUTOFF_TIME" ] && continue
        
        workspace=$(basename "$(dirname "$dbfile")")
        mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
        
        # Query for chat-related keys
        if command -v sqlite3 &> /dev/null; then
            # Check for chat data
            has_chat=$(sqlite3 "$dbfile" "SELECT key FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%aiService%' OR key LIKE '%cascade%' OR key LIKE '%prompt%' LIMIT 1;" 2>/dev/null)
            if [ -n "$has_chat" ]; then
                echo "$mod_epoch|$mod_time_fmt|CHAT|Workspace $workspace - Chat/Composer activity"
                
                # Try to extract actual prompt content
                chat_value=$(sqlite3 "$dbfile" "SELECT value FROM ItemTable WHERE key LIKE '%aiService.generations%' OR key LIKE '%aiService.prompts%' OR key LIKE '%cascade.chat%' ORDER BY rowid DESC LIMIT 1;" 2>/dev/null)
                if [ -n "$chat_value" ] && [ "${#chat_value}" -gt 50 ]; then
                    # Extract user prompts from the JSON
                    echo "$chat_value" | python3 -c '
import json, sys
from datetime import datetime

try:
    data = json.load(sys.stdin)
    
    def find_user_prompts(obj):
        prompts = []
        if isinstance(obj, dict):
            role = obj.get("role", "").lower()
            msg_type = obj.get("type", "").lower()
            
            if role == "user" or msg_type == "user":
                text = ""
                if "text" in obj:
                    text = obj["text"]
                elif "content" in obj:
                    content = obj["content"]
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and c.get("type") == "text":
                                text += c.get("text", "")
                elif "message" in obj:
                    text = obj["message"]
                
                if text and len(text.strip()) > 5:
                    ts = obj.get("timestamp", int(datetime.now().timestamp()))
                    if isinstance(ts, (int, float)) and ts > 1000000000000:
                        ts = int(ts / 1000)
                    prompts.append((ts, text.strip()[:250]))
            
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    prompts.extend(find_user_prompts(v))
                    
        elif isinstance(obj, list):
            for item in obj:
                prompts.extend(find_user_prompts(item))
                
        return prompts
    
    prompts = find_user_prompts(data)
    prompts.sort(key=lambda x: x[0], reverse=True)
    
    for ts, text in prompts[:3]:
        print(f"{ts}|{text}")
        
except Exception as e:
    pass
' 2>/dev/null | while IFS='|' read -r ts prompt; do
                        [ -n "$prompt" ] && echo "$ts|$mod_time_fmt|PROMPT|[$workspace] $prompt"
                    done
                fi
            fi
        fi
    done >> "$temp_file"
fi

# 7. Scan Windsurf plans directory (~/.windsurf/plans/*.md) for prompts
WINDSURF_PLANS_DIR="$HOME/.windsurf/plans"
if [ -d "$WINDSURF_PLANS_DIR" ]; then
    find "$WINDSURF_PLANS_DIR" -name "*.md" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read planfile; do
        mod_time_str=$(stat -f %Sm "$planfile" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        [ "$mod_epoch" -lt "$CUTOFF_TIME" ] && continue
        
        mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
        plan_name=$(basename "$planfile" .md)
        
        # Extract first line as title/prompt summary
        first_line=$(head -1 "$planfile" 2>/dev/null | sed 's/^# //' | cut -c1-200)
        if [ -n "$first_line" ]; then
            echo "$mod_epoch|$mod_time_fmt|PROMPT|Plan: $first_line"
        else
            echo "$mod_epoch|$mod_time_fmt|PROMPT|Plan: $plan_name"
        fi
    done >> "$temp_file"
fi

# Sort and process events
echo "## 📊 Summary" | tee -a "$OUT"
echo "" | tee -a "$OUT"

if [ -s "$temp_file" ]; then
    sort -t'|' -k1,1n "$temp_file" | awk -F'|' '!seen[$2 $3 $4]++' > "$temp_file.sorted"
    
    EDIT_COUNT=$(awk -F'|' '$3=="EDIT" {c++} END {print c+0}' "$temp_file.sorted")
    CASCADE_COUNT=$(awk -F'|' '$3=="CASCADE" {c++} END {print c+0}' "$temp_file.sorted")
    PREVIEW_COUNT=$(awk -F'|' '$3=="PREVIEW" {c++} END {print c+0}' "$temp_file.sorted")
    MCP_TOOL_COUNT=$(awk -F'|' '$3=="MCP-TOOL" {c++} END {print c+0}' "$temp_file.sorted")
    MCP_REQ_COUNT=$(awk -F'|' '$3=="MCP-REQ" {c++} END {print c+0}' "$temp_file.sorted")
    TERM_COUNT=$(awk -F'|' '$3=="TERMINAL" {c++} END {print c+0}' "$temp_file.sorted")
    WS_COUNT=$(awk -F'|' '$3=="WORKSPACE" {c++} END {print c+0}' "$temp_file.sorted")
    
    echo "- **Total Events Found:** $(wc -l < "$temp_file.sorted" | tr -d ' ')" | tee -a "$OUT"
    echo "- **📝 File Edits (Cascade):** $EDIT_COUNT" | tee -a "$OUT"
    echo "- **🔧 Cascade Operations:** $CASCADE_COUNT" | tee -a "$OUT"
    echo "- **👁️ Diff Previews:** $PREVIEW_COUNT" | tee -a "$OUT"
    echo "- **🤖 MCP Tool Calls:** $MCP_TOOL_COUNT" | tee -a "$OUT"
    echo "- **📡 MCP Requests:** $MCP_REQ_COUNT" | tee -a "$OUT"
    echo "- **💻 Terminal Sessions:** $TERM_COUNT" | tee -a "$OUT"
    echo "- **💼 Workspaces Active:** $WS_COUNT" | tee -a "$OUT"
    
    # Count prompts and chat
    PROMPT_COUNT=$(awk -F'|' '$3=="PROMPT" {c++} END {print c+0}' "$temp_file.sorted")
    CHAT_COUNT=$(awk -F'|' '$3=="CHAT" {c++} END {print c+0}' "$temp_file.sorted")
    if [ "$PROMPT_COUNT" -gt 0 ]; then
        echo "- **📋 Prompts Captured:** $PROMPT_COUNT" | tee -a "$OUT"
    fi
    if [ "$CHAT_COUNT" -gt 0 ]; then
        echo "- **💬 Chat Sessions:** $CHAT_COUNT" | tee -a "$OUT"
    fi
    
    # File edit diff stats
    if [ "$EDIT_COUNT" -gt 0 ]; then
        echo "" | tee -a "$OUT"
        echo "### 📊 File Edit Diff Stats" | tee -a "$OUT"
        echo "" | tee -a "$OUT"
        awk -F'|' '$3=="EDIT" {if($6) files[$5]=$6; else files[$5]=""} END {for(f in files) print files[f], f}' "$temp_file.sorted" 2>/dev/null | sort -u | while read diff_info filepath; do
            filename=$(basename "$filepath")
            if [ -n "$diff_info" ]; then
                echo "- \`$filename\`: $diff_info lines" | tee -a "$OUT"
            else
                echo "- \`$filename\`" | tee -a "$OUT"
            fi
        done
        echo "" | tee -a "$OUT"
    fi
    
    echo "" | tee -a "$OUT"
    echo "## ⏱️ Timeline of Events" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
    
    last_date=""
    while IFS='|' read -r epoch timestamp category details resource; do
        date_part="${timestamp:0:10}"
        time_part="${timestamp:11:8}"
        
        if [ "$date_part" != "$last_date" ]; then
            echo "" | tee -a "$OUT"
            echo "### 📅 $date_part" | tee -a "$OUT"
            echo "" | tee -a "$OUT"
            last_date="$date_part"
        fi
        
        case "$category" in
            "EDIT")
                filename=$(basename "$resource" 2>/dev/null || echo "unknown")
                echo "#### \`$time_part\` 📝 File Edit: $details" | tee -a "$OUT"
                echo "   File: \`$filename\`" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "PROMPT")
                echo "#### \`$time_part\` 📋 Prompt: $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "CHAT")
                echo "#### \`$time_part\` 💬 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "CASCADE")
                echo "#### \`$time_part\` 🔧 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "PREVIEW")
                echo "#### \`$time_part\` 👁️ $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "DIFF")
                echo "#### \`$time_part\` 📊 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "MCP-TOOL")
                echo "#### \`$time_part\` 🤖 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "MCP-REQ")
                echo "#### \`$time_part\` 📡 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "MCP-RESP")
                echo "#### \`$time_part\` ✅ $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "TERMINAL")
                echo "#### \`$time_part\` 💻 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "WORKSPACE")
                echo "#### \`$time_part\` 💼 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "STORAGE")
                echo "#### \`$time_part\` 💾 $details" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
        esac
    done < "$temp_file.sorted"
else
    echo "- **Total Events Found:** 0" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
    echo "## ⏱️ Timeline of Events" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
    echo "*No events found in the specified time range.*" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
fi

# Add MCP server summary
echo "---" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "**Output saved to:** \`$OUT\`" | tee -a "$OUT"

# Cleanup
rm -f "$temp_file" "$temp_file.sorted"

echo ""
echo "✅ Windsurf work timeline saved to: $OUT"
