#!/usr/bin/env bash
# =============================================================================
# lib_ide_utils.sh - Shared utility library for IDE extraction scripts
# =============================================================================
# This is a library file meant to be sourced, NOT executed directly.
# Usage: source tools/lib_ide_utils.sh
# =============================================================================

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
STATE_DIR="${HOME}/.ide_work_state"
TIMESTAMP_FILE="${STATE_DIR}/last_run"
LAST_RUN_DEFAULT_HOURS=10

# Browser DB paths
CHROME_DB_PATH="${HOME}/Library/Application Support/Google/Chrome/Default/History"
EDGE_DB_PATH="${HOME}/Library/Application Support/Microsoft Edge/Default/History"

# -----------------------------------------------------------------------------
# State Management
# -----------------------------------------------------------------------------

# get_last_run_timestamp - Reads last run timestamp, defaults to 10 hours ago
# Returns: Epoch timestamp (seconds)
get_last_run_timestamp() {
    if [[ -f "${TIMESTAMP_FILE}" ]]; then
        cat "${TIMESTAMP_FILE}"
    else
        echo $(( $(date +%s) - (LAST_RUN_DEFAULT_HOURS * 3600) ))
    fi
}

# save_last_run_timestamp - Saves current timestamp to state file
save_last_run_timestamp() {
    mkdir -p "${STATE_DIR}"
    date +%s > "${TIMESTAMP_FILE}"
}

# -----------------------------------------------------------------------------
# Duration Parsing
# -----------------------------------------------------------------------------

# parse_duration_to_minutes - Converts duration string to minutes
# Input: "10h", "30m", "2d" etc.
# Returns: Number of minutes
parse_duration_to_minutes() {
    local duration="$1"
    
    if [[ -z "${duration}" ]]; then
        echo "0"
        return
    fi
    
    local value="${duration%[hmd]*}"
    local unit="${duration##*[0-9]}"
    
    case "${unit}" in
        d)
            echo $(( value * 24 * 60 ))
            ;;
        h)
            echo $(( value * 60 ))
            ;;
        m)
            echo "${value}"
            ;;
        *)
            echo "0"
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Browser History Extraction
# -----------------------------------------------------------------------------

# extract_chrome_history - Extracts recent Chrome URLs
# Input: cutoff_minutes (minutes before now to query from)
# Returns: Tab-separated URLs and titles
extract_chrome_history() {
    local cutoff_minutes="${1:-60}"
    local cutoff_epoch=$(( $(date +%s) - (cutoff_minutes * 60) ))
    
    # Chrome uses 1601-01-01 as epoch, need to calculate microseconds
    local chrome_epoch=11644473600  # seconds between 1601-01-01 and 1970-01-01
    local cutoff_chrome_time=$(( (cutoff_epoch + chrome_epoch) * 1000000 ))
    
    local temp_db="/tmp/chrome_history_$$.db"
    
    if ! cp "${CHROME_DB_PATH}" "${temp_db}" 2>/dev/null; then
        echo "Failed to copy Chrome history database" >&2
        return 1
    fi
    
    sqlite3 -separator $'\t' "${temp_db}" \
        "SELECT url, title, datetime(last_visit_time/1000000 + 11644473600, 'unixepoch', 'localtime') 
         FROM urls 
         WHERE last_visit_time > ${cutoff_chrome_time}
         ORDER BY last_visit_time DESC
         LIMIT 500" 2>/dev/null
    
    rm -f "${temp_db}"
}

# extract_edge_history - Extracts recent Edge URLs
# Input: cutoff_minutes (minutes before now to query from)
# Returns: Tab-separated URLs and titles
extract_edge_history() {
    local cutoff_minutes="${1:-60}"
    local cutoff_epoch=$(( $(date +%s) - (cutoff_minutes * 60) ))
    
    # Edge also uses 1601-01-01 as epoch
    local chrome_epoch=11644473600
    local cutoff_chrome_time=$(( (cutoff_epoch + chrome_epoch) * 1000000 ))
    
    local temp_db="/tmp/edge_history_$$.db"
    
    if ! cp "${EDGE_DB_PATH}" "${temp_db}" 2>/dev/null; then
        echo "Failed to copy Edge history database" >&2
        return 1
    fi
    
    sqlite3 -separator $'\t' "${temp_db}" \
        "SELECT url, title, datetime(last_visit_time/1000000 + 11644473600, 'unixepoch', 'localtime') 
         FROM urls 
         WHERE last_visit_time > ${cutoff_chrome_time}
         ORDER BY last_visit_time DESC
         LIMIT 500" 2>/dev/null
    
    rm -f "${temp_db}"
}

# -----------------------------------------------------------------------------
# Markdown Formatting
# -----------------------------------------------------------------------------

# format_markdown_header - Creates a consistent markdown header
# Input: title (string)
# Returns: Formatted markdown header
format_markdown_header() {
    local title="$1"
    local title_length=${#title}
    local separator=$(printf '=%.0s' $(seq 1 $title_length))
    
    echo "${title}"
    echo "${separator}"
}

# -----------------------------------------------------------------------------
# Git Integration
# -----------------------------------------------------------------------------

# get_git_log_summary - Returns recent commits with stat info
# Input: repo_path (path to git repository), hours (number of hours to look back)
# Returns: Formatted git log with stats
get_git_log_summary() {
    local repo_path="$1"
    local hours="${2:-24}"
    
    if [[ ! -d "${repo_path}/.git" ]]; then
        echo "Not a git repository: ${repo_path}" >&2
        return 1
    fi
    
    # Change to repo directory and get log
    (
        cd "${repo_path}" || exit 1
        git log --since="${hours} hours ago" --oneline --stat=5 --format="%h %s%n%b" 2>/dev/null
    )
}
