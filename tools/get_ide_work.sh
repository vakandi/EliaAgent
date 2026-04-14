#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    cat << EOF
Usage: $(basename "$0")

Merge OpenCode, Cursor, and Windsurf extractions into one summary under docs/<today>/ide_work_summary_*.md.
Each sub-extractor is run with a time window in hours derived from the last successful run (see lib_ide_utils.sh), not from CLI args.

Environment (1 = include, 0 = skip):
  INCLUDE_OPENCODE   (default 1)
  INCLUDE_CURSOR     (default 1)
  INCLUDE_WINDSURF   (default 1)
  INCLUDE_BROWSER    (default 0)  — Chrome history snippet
  INCLUDE_GIT        (default 0)  — recent commits

OpenCode only with an explicit hour window: ./tools/get_opencode_work.sh [hours]
EOF
    exit 0
fi

source "${SCRIPT_DIR}/lib_ide_utils.sh"

DOCS_DIR="${DOCS_DIR:-$SCRIPT_DIR/../docs}"
DAY_DIR="$DOCS_DIR/$(date +%Y-%m-%d)"
mkdir -p "$DAY_DIR"
OUT="$DAY_DIR/ide_work_summary_$(date +%H%M%S).md"

INCLUDE_OPENCODE="${INCLUDE_OPENCODE:-1}"
INCLUDE_CURSOR="${INCLUDE_CURSOR:-1}"
INCLUDE_WINDSURF="${INCLUDE_WINDSURF:-1}"
INCLUDE_BROWSER="${INCLUDE_BROWSER:-0}"
INCLUDE_GIT="${INCLUDE_GIT:-0}"

for s in get_opencode_work.sh get_cursor_work.sh get_windsurf_work.sh; do
    chmod +x "${SCRIPT_DIR}/$s" 2>/dev/null || true
done

SINCE_EPOCH=$(get_last_run_timestamp)
SINCE_DATE=$(date -r "$SINCE_EPOCH" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@$SINCE_EPOCH" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$SINCE_EPOCH")
HOURS=$(( ($(date +%s) - SINCE_EPOCH) / 3600 ))

{
    echo "# IDE Work Summary"
    echo ""
    echo '> **📎 See also**: [[../wiki/businesses/CoBou-Agency|CoBou Agency]] | [[../wiki/topics/CoBou-Agency-Timeline|CoBou Timeline]] | [[../wiki/businesses/Bene2Luxe|Bene2Luxe]] | [[../wiki/businesses/ZovaBoost|ZovaBoost]] | [[../wiki/topics/Infrastructure-Timeline|Infrastructure]] | [[../wiki/tools/MCP-Tools|MCP Tools]]'
    echo ""
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S') | **Since:** $SINCE_DATE (${HOURS}h) | **User:** $(whoami)"
    echo ""
} > "$OUT"

echo "📦 Running IDE extractions..."
echo ""

run_script() {
    local n="$1" s="$2" l
    l=$(echo "$n" | tr '[:upper:]' '[:lower:]')
    echo "   $n..."
    "${SCRIPT_DIR}/${s}" "$HOURS" >/dev/null 2>&1 || true
    ls -t "$DAY_DIR"/${l}_work_*.md 2>/dev/null | head -1
}

get_size() { stat -f%z "$1" 2>/dev/null || stat -c%s "$1" 2>/dev/null || echo "?"; }

[[ "$INCLUDE_OPENCODE" == "1" ]] && {
    OC=$(run_script "OpenCode" "get_opencode_work.sh")
    echo "   ✅ $(basename "$OC") ($(du -h "$OC" | cut -f1))"
} || { OC=""; echo "   ⚠️  No OpenCode data"; }

[[ "$INCLUDE_CURSOR" == "1" ]] && {
    CU=$(run_script "Cursor" "get_cursor_work.sh")
    echo "   ✅ $(basename "$CU") ($(du -h "$CU" | cut -f1))"
} || { CU=""; echo "   ⚠️  No Cursor data"; }

[[ "$INCLUDE_WINDSURF" == "1" ]] && {
    WI=$(run_script "Windsurf" "get_windsurf_work.sh")
    echo "   ✅ $(basename "$WI") ($(du -h "$WI" | cut -f1))"
} || { WI=""; echo "   ⚠️  No Windsurf data"; }

{
    echo ""
    echo "---"
    echo ""
    echo "## Latest Reports"
    echo ""
    [[ -n "$OC" ]] && echo "- **OpenCode:** $(basename "$OC") ($(du -h "$OC" | cut -f1))"
    [[ -n "$CU" ]] && echo "- **Cursor:** $(basename "$CU") ($(du -h "$CU" | cut -f1))"
    [[ -n "$WI" ]] && echo "- **Windsurf:** $(basename "$WI") ($(du -h "$WI" | cut -f1))"
    echo ""
    echo "_All reports in: $DAY_DIR/_"
} >> "$OUT"

[[ "$INCLUDE_BROWSER" == "1" ]] && {
    echo "" >> "$OUT"
    echo "## 🌐 Browser History" >> "$OUT"
    echo "" >> "$OUT"
    extract_chrome_history $((HOURS * 60)) 2>/dev/null | head -50 >> "$OUT" || echo "_Failed_" >> "$OUT"
}

[[ "$INCLUDE_GIT" == "1" ]] && {
    echo "" >> "$OUT"
    echo "## 📝 Recent Commits" >> "$OUT"
    echo "" >> "$OUT"
    get_git_log_summary "$SCRIPT_DIR/.." "$HOURS" >> "$OUT" 2>/dev/null || echo "_No commits_" >> "$OUT"
}

save_last_run_timestamp

echo ""
echo "✅ Done! Summary: $OUT"
echo "   Lines: $(wc -l < "$OUT"), Size: $(du -h "$OUT" | cut -f1)"
