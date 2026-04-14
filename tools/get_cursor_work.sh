#!/bin/bash

# get_cursor_work.sh - Extract Cursor IDE work history from workspaceStorage and logs
# Usage: ./get_cursor_work.sh [time_duration]
# Examples: ./get_cursor_work.sh 5m (last 5 minutes)
#           ./get_cursor_work.sh 1h (last 1 hour)
#           ./get_cursor_work.sh 48h (last 48 hours)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib_ide_utils.sh"

# Output under docs/YYYY-MM-DD/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="${DOCS_DIR:-$ROOT/docs}"
DAY_DIR="$DOCS_DIR/$(date +%Y-%m-%d)"
mkdir -p "$DAY_DIR"

CUTOFF_TIME=$(get_last_run_timestamp)
MINUTES=$(( ($(date +%s) - CUTOFF_TIME) / 60 ))
CUTOFF_ISO=$(date -r "$CUTOFF_TIME" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@$CUTOFF_TIME" "+%Y-%m-%d %H:%M:%S")

trap 'save_last_run_timestamp' EXIT

TIME_DURATION="${1:-${MINUTES}m}"

OUT="$DAY_DIR/cursor_work_$(date +%H%M%S).md"

# Cursor paths
CURSOR_DIR="$HOME/Library/Application Support/Cursor"
LOG_DIR="$CURSOR_DIR/logs"
WORKSPACE_STORAGE="$CURSOR_DIR/User/workspaceStorage"
HISTORY_DIR="$CURSOR_DIR/User/History"
# Cursor IDE stores agent chat transcripts per project (prompts, edits)
CURSOR_PROJECTS="$HOME/.cursor/projects"

echo "# 🖱️ Cursor IDE Work Timeline" | tee "$OUT"
echo "" | tee -a "$OUT"
echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$OUT"
echo "**Time Range:** Last $TIME_DURATION (since $CUTOFF_ISO)" | tee -a "$OUT"
echo "**User:** $(whoami)" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "---" | tee -a "$OUT"
echo "" | tee -a "$OUT"

echo "🔍 Scanning Cursor data for last $TIME_DURATION..."

# Check if Cursor directory exists
if [ ! -d "$CURSOR_DIR" ]; then
    echo "❌ Cursor not found at: $CURSOR_DIR" | tee -a "$OUT"
    exit 1
fi

# Collect events
temp_file="/tmp/cursor_events_$$.txt"
> "$temp_file"

# 1. Check workspaceStorage SQLite databases for chat/composer data
if [ -d "$WORKSPACE_STORAGE" ]; then
    find "$WORKSPACE_STORAGE" -name "state.vscdb" -type f 2>/dev/null | while read dbfile; do
        # Get file modification time using stat -f %Sm gives "Feb 24 15:18:57 2026" format
        mod_time_str=$(stat -f %Sm "$dbfile" 2>/dev/null)
        # Convert to epoch
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        
        if [ "$mod_epoch" -ge "$CUTOFF_TIME" ]; then
            workspace=$(basename "$(dirname "$dbfile")")
            
            # Query for chat-related data - Cursor uses different key names
            chat_keys=$(sqlite3 "$dbfile" "SELECT key FROM ItemTable WHERE key LIKE '%aiService.generations%' OR key LIKE '%aiService.prompts%' OR key LIKE '%composer.composerData%' OR key LIKE '%chat%' OR key LIKE '%cursor%ai%';" 2>/dev/null)
            
            if [ -n "$chat_keys" ]; then
                # Format timestamp for output
                mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                echo "$mod_epoch|$mod_time_fmt|CHAT|Workspace $workspace - Chat/Composer activity"
                
                chat_data=$(sqlite3 "$dbfile" "SELECT value FROM ItemTable WHERE key='aiService.generations' OR key='aiService.prompts' OR key='composer.composerData' LIMIT 1" 2>/dev/null | head -c 500)
                if [ -n "$chat_data" ] && [ "${#chat_data}" -gt 10 ]; then
                    echo "$mod_epoch|$mod_time_fmt|DATA|$workspace - Has chat data"
                fi
            fi
            
            # Check for any cursor AI activity
            cursor_keys=$(sqlite3 "$dbfile" "SELECT key FROM ItemTable WHERE key LIKE '%cursor%' OR key LIKE '%ai-chat%' OR key LIKE '%conversation%'" 2>/dev/null)
            if [ -n "$cursor_keys" ]; then
                mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                echo "$mod_epoch|$mod_time_fmt|CURSOR|Workspace $workspace - Cursor AI activity"
            fi
        fi
    done >> "$temp_file"
fi

# 2. Parse Cursor log files for AI activity
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "*.log" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | head -10 | while read logfile; do
        grep -hE "(copilot|openai|claude|anthropic|chat|completion|agent|prompt)" "$logfile" 2>/dev/null | head -100 | while read line; do
            # Extract timestamp
            if [[ "$line" =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2}[T\ ][0-9]{2}:[0-9]{2}:[0-9]{2}) ]]; then
                ts="${BASH_REMATCH[1]}"
                ts="${ts/T/ }"
                ts_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$ts" +%s 2>/dev/null || date -d "$ts" +%s 2>/dev/null || echo 0)
                if [ "$ts_epoch" -ge "$CUTOFF_TIME" ]; then
                    echo "$ts_epoch|$ts|AI|$line"
                fi
            fi
        done
    done >> "$temp_file"
fi

# 3. Check for recent file modifications in workspace storage
if [ -d "$WORKSPACE_STORAGE" ]; then
    find "$WORKSPACE_STORAGE" -type f -mmin -$MINUTES 2>/dev/null | while read file; do
        mod_time_str=$(stat -f %Sm "$file" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        if [ "$mod_epoch" -ge "$CUTOFF_TIME" ]; then
            rel_path=$(echo "$file" | sed "s|$WORKSPACE_STORAGE/||")
            mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
            echo "$mod_epoch|$mod_time_fmt|FILE|$rel_path"
        fi
    done >> "$temp_file"
fi

# 4. Cursor agent transcripts (prompts, chat) - ~/.cursor/projects/<project>/agent-transcripts/
if [ -d "$CURSOR_PROJECTS" ]; then
    find "$CURSOR_PROJECTS" -path "*/agent-transcripts/*/*.jsonl" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read jsonl; do
        mod_time_str=$(stat -f %Sm "$jsonl" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        [ "$mod_epoch" -lt "$CUTOFF_TIME" ] && continue
        mod_time_fmt=$(date -r "$mod_epoch" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
        project=$(echo "$jsonl" | sed "s|$CURSOR_PROJECTS/||" | cut -d'/' -f1)
        # Extract first user prompt via Python (handles nested JSON and escaped chars)
        prompt=$(python3 << PYEOF 2>/dev/null
import json, sys
path = r"""$jsonl"""
try:
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get('role') == 'user':
                content = d.get('message', {}).get('content', [])
                for c in content:
                    if c.get('type') == 'text':
                        t = (c.get('text') or '').strip().replace('\n', ' ')
                        if '<user_query>' in t:
                            t = t.split('<user_query>', 1)[-1].split('</user_query>', 1)[0].strip()
                        if t:
                            print((t[:200] + '...') if len(t) > 200 else t)
                        sys.exit(0)
except Exception:
    pass
PYEOF
)
        [ -n "$prompt" ] && echo "$mod_epoch|$mod_time_fmt|PROMPT|[$project] $prompt"
        echo "$mod_epoch|$mod_time_fmt|TRANSCRIPT|Agent transcript: $project - $(basename "$(dirname "$jsonl")")"
    done >> "$temp_file"
fi

# 5. Cursor file edit history (User/History/*/entries.json) - like Windsurf
if [ -d "$HISTORY_DIR" ]; then
    find "$HISTORY_DIR" -name "entries.json" -type f -mmin -$((MINUTES + 5)) 2>/dev/null | while read histfile; do
        mod_time_str=$(stat -f %Sm "$histfile" 2>/dev/null)
        mod_epoch=$(date -j -f "%b %d %H:%M:%S %Y" "$mod_time_str" +%s 2>/dev/null || echo 0)
        [ "$mod_epoch" -lt "$CUTOFF_TIME" ] && continue
        if command -v python3 &> /dev/null; then
            python3 -c "
import json, sys, os
try:
    with open('$histfile', 'r') as f:
        data = json.load(f)
    resource = data.get('resource', '')
    if resource.startswith('file:///'):
        path = resource.replace('file://', '')
    else:
        path = resource
    for entry in data.get('entries', []):
        ts = entry.get('timestamp', 0)
        if ts > ${CUTOFF_TIME}000:
            ts_sec = int(ts / 1000)
            from datetime import datetime
            ts_iso = datetime.fromtimestamp(ts_sec).strftime('%Y-%m-%d %H:%M:%S')
            source = entry.get('source', 'edit')
            print(f\"{ts_sec}|{ts_iso}|EDIT|{source}|{path}\")
except Exception as e:
    pass
" 2>/dev/null
        fi
    done >> "$temp_file"
fi

# Sort and process events
echo "## 📊 Summary" | tee -a "$OUT"
echo "" | tee -a "$OUT"

if [ -s "$temp_file" ]; then
    sort -t'|' -k1,1n "$temp_file" | awk -F'|' '!seen[$2 $3]++' > "$temp_file.sorted"
    
    EVENT_COUNT=$(wc -l < "$temp_file.sorted" | tr -d ' ')
    CHAT_COUNT=$(awk -F'|' '$3=="CHAT" {c++} END {printf "%d", c+0}' "$temp_file.sorted")
    AI_COUNT=$(awk -F'|' '$3=="AI" {c++} END {printf "%d", c+0}' "$temp_file.sorted")
    FILE_COUNT=$(awk -F'|' '$3=="FILE" {c++} END {printf "%d", c+0}' "$temp_file.sorted")
    PROMPT_COUNT=$(awk -F'|' '$3=="PROMPT" {c++} END {printf "%d", c+0}' "$temp_file.sorted")
    TRANSCRIPT_COUNT=$(awk -F'|' '$3=="TRANSCRIPT" {c++} END {printf "%d", c+0}' "$temp_file.sorted")
    EDIT_COUNT=$(awk -F'|' '$3=="EDIT" {c++} END {printf "%d", c+0}' "$temp_file.sorted")
    
    echo "- **Total Events Found:** $EVENT_COUNT" | tee -a "$OUT"
    echo "- **Cursor prompts (agent transcripts):** $PROMPT_COUNT" | tee -a "$OUT"
    echo "- **Agent transcript sessions:** $TRANSCRIPT_COUNT" | tee -a "$OUT"
    echo "- **File edits (History):** $EDIT_COUNT" | tee -a "$OUT"
    echo "- **Chat/Composer Sessions:** $CHAT_COUNT" | tee -a "$OUT"
    echo "- **AI Activity (logs):** $AI_COUNT" | tee -a "$OUT"
    echo "- **File Operations (workspaceStorage):** $FILE_COUNT" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
    
    # Files edited: unique path + name (path = fields 5 onward in case of | in path)
    EDIT_PATHS=$(awk -F'|' '$3=="EDIT" {p=""; for(i=5;i<=NF;i++) p=p (i>5?"|":"") $i; if(p!="") print p}' "$temp_file.sorted" | sort -u)
    if [ -n "$EDIT_PATHS" ]; then
        echo "## 📁 Files edited (name and path)" | tee -a "$OUT"
        echo "" | tee -a "$OUT"
        echo "$EDIT_PATHS" | while read -r path; do
            [ -z "$path" ] && continue
            name=$(basename "$path")
            echo "- **$name**" | tee -a "$OUT"
            echo "  \`$path\`" | tee -a "$OUT"
        done
        echo "" | tee -a "$OUT"
    fi
    
    # Calculate diff stats for edited files
    EDIT_DATA=$(awk -F'|' '$3=="EDIT" {f=""; for(i=5;i<=NF;i++) f=f (i>5?"|":"") $i; print f}' "$temp_file.sorted" | sort -u)
    if [ -n "$EDIT_DATA" ]; then
        echo "## 📊 File Edit Diff Stats" | tee -a "$OUT"
        echo "" | tee -a "$OUT"
        echo "| File | Changes |" | tee -a "$OUT"
        echo "|------|---------|" | tee -a "$OUT"
        while read -r edit_path; do
            [ -z "$edit_path" ] && continue
            edit_count=$(grep -c "|$edit_path" "$temp_file.sorted" 2>/dev/null || echo "1")
            edit_name=$(basename "$edit_path")
            echo "| \`$edit_name\` | ${edit_count} edit(s) |" | tee -a "$OUT"
        done <<< "$EDIT_DATA"
        echo "" | tee -a "$OUT"
    fi
    
    echo "## ⏱️ Timeline of Events" | tee -a "$OUT"
    echo "" | tee -a "$OUT"
    
    last_date=""
    while IFS='|' read -r epoch timestamp category line; do
        date_part="${timestamp:0:10}"
        time_part="${timestamp:11:8}"
        
        if [ "$date_part" != "$last_date" ]; then
            echo "" | tee -a "$OUT"
            echo "### 📅 $date_part" | tee -a "$OUT"
            echo "" | tee -a "$OUT"
            last_date="$date_part"
        fi
        
        case "$category" in
            "CHAT")
                echo "#### \`$time_part\` 💬 Chat/Composer Activity" | tee -a "$OUT"
                echo "   $line" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "DATA")
                echo "#### \`$time_part\` 📝 Chat Data Available" | tee -a "$OUT"
                echo "   $line" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "CURSOR")
                echo "#### \`$time_part\` 🤖 Cursor AI Activity" | tee -a "$OUT"
                echo "   $line" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "AI")
                echo "#### \`$time_part\` 🤖 AI/LLM Activity" | tee -a "$OUT"
                excerpt=$(echo "$line" | sed 's/^[^[]*\[[^]]*\] //g' | head -c 200)
                echo "   $excerpt..." | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "FILE")
                echo "#### \`$time_part\` 📁 File Activity" | tee -a "$OUT"
                echo "   $line" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "PROMPT")
                echo "#### \`$time_part\` 📋 Cursor prompt (agent)" | tee -a "$OUT"
                echo "   $line" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "TRANSCRIPT")
                echo "#### \`$time_part\` 💬 Agent transcript" | tee -a "$OUT"
                echo "   $line" | tee -a "$OUT"
                echo "" | tee -a "$OUT"
                ;;
            "EDIT")
                edit_source="${line%%|*}"
                edit_path="${line#*|}"
                edit_name=$(basename "$edit_path" 2>/dev/null || echo "$edit_path")
                echo "#### \`$time_part\` ✏️ File edit" | tee -a "$OUT"
                echo "   **File:** $edit_name" | tee -a "$OUT"
                echo "   **Path:** \`$edit_path\`" | tee -a "$OUT"
                echo "   **Action:** $edit_source" | tee -a "$OUT"
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

# Agent transcript conversations (all user prompts + AI replies)
if [ -d "$CURSOR_PROJECTS" ]; then
    transcript_detail="/tmp/cursor_transcript_detail_$$.md"
    > "$transcript_detail"
    CURSOR_PROJECTS="$CURSOR_PROJECTS" CUTOFF_TIME="$CUTOFF_TIME" python3 << 'PYEOF' 2>/dev/null >> "$transcript_detail"
import os, json, glob
from pathlib import Path
projects = os.environ.get("CURSOR_PROJECTS", "")
cutoff = int(os.environ.get("CUTOFF_TIME", "0"))
if not projects or not cutoff:
    exit(0)
for jsonl_path in Path(projects).glob("*/agent-transcripts/*/*.jsonl"):
    try:
        if jsonl_path.stat().st_mtime < cutoff:
            continue
        # path: .../projects/PROJECT/agent-transcripts/UUID/UUID.jsonl
        project = jsonl_path.parent.parent.parent.name  # PROJECT folder
        transcript_id = jsonl_path.parent.name          # UUID folder
        print("")
        print("## 💬 Transcript: {} / {}".format(project, transcript_id))
        print("")
        with open(jsonl_path) as f:
            for idx, line in enumerate(f):
                try:
                    d = json.loads(line)
                    role = d.get("role", "")
                    content = d.get("message", {}).get("content", [])
                    text = ""
                    for c in content:
                        if c.get("type") == "text":
                            text = (c.get("text") or "").strip()
                            break
                    if not text:
                        continue
                    if "<user_query>" in text:
                        text = text.split("<user_query>", 1)[-1].split("</user_query>", 1)[0].strip()
                    text = text.replace("\\n", "\n")
                    if role == "user":
                        excerpt = text[:800] + ("..." if len(text) > 800 else "")
                        print("### 👤 User")
                        print("")
                        print(excerpt)
                        print("")
                    elif role == "assistant":
                        excerpt = text[:500] + ("..." if len(text) > 500 else "")
                        print("### 🤖 Assistant")
                        print("")
                        print(excerpt)
                        print("")
                except (json.JSONDecodeError, KeyError):
                    pass
        print("---")
    except (OSError, ValueError):
        pass
PYEOF
    if [ -s "$transcript_detail" ]; then
        echo "" | tee -a "$OUT"
        echo "---" | tee -a "$OUT"
        echo "" | tee -a "$OUT"
        echo "## 💬 Agent transcript conversations (prompts + AI replies)" | tee -a "$OUT"
        echo "" | tee -a "$OUT"
        cat "$transcript_detail" >> "$OUT"
    fi
    rm -f "$transcript_detail"
fi

# Add workspace summary
echo "" | tee -a "$OUT"
echo "---" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "## 💼 Workspaces with Activity" | tee -a "$OUT"
echo "" | tee -a "$OUT"

if [ -d "$WORKSPACE_STORAGE" ]; then
    find "$WORKSPACE_STORAGE" -name "state.vscdb" -type f -mmin -$MINUTES 2>/dev/null | while read dbfile; do
        workspace=$(basename "$(dirname "$dbfile")")
        mod_time=$(stat -f %Sm -t %Y-%m-%d %H:%M:%S "$dbfile" 2>/dev/null || echo "")
        echo "- **$workspace** - Modified: $mod_time" | tee -a "$OUT"
    done
fi

echo "" | tee -a "$OUT"
echo "---" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "## 📝 Notes" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "- Chat data is stored in SQLite databases (.vscdb files)" | tee -a "$OUT"
echo "- Each workspace has its own storage directory" | tee -a "$OUT"
echo "- To extract full chat history, use sqlite3 to query the databases" | tee -a "$OUT"
echo "" | tee -a "$OUT"
echo "**Output saved to:** \`$OUT\`" | tee -a "$OUT"

# Cleanup
rm -f "$temp_file" "$temp_file.sorted"

echo ""
echo "✅ Cursor work timeline saved to: $OUT"
