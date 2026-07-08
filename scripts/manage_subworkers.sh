#!/bin/zsh
# EliaAI Subworkers Manager
# Enable, disable, install, uninstall subworkers via launchd plists
# Usage: ./manage_subworkers.sh [command] [subworker_name]

set -euo pipefail

AGENT_DIR="${AGENT_DIR:-$HOME/EliaAI}"
SW_DIR="${AGENT_DIR}/subworkers"
PLISTS_DIR="${SW_DIR}/plists"
SCRIPTS_DIR="${SW_DIR}/scripts"
LOGS_DIR="${SW_DIR}/logs"
LAUNCHD_DIR="${HOME}/Library/LaunchAgents"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success(){ echo -e "${GREEN}[OK]${NC} $1"; }
warn()   { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; }

# ── Subworker definitions ──────────────────────────────────────────
# Format: "dir_name:plist_name:trigger_script:log_file:display_name"
# Edit this array to match YOUR subworkers.
# Example:
#   "my-promoter:com.elia.my-promoter:trigger_my_promoter.sh:my_promoter.log:My Promoter"
SUBWORKERS=(
  # Add your subworkers here:
  # "agent-name:com.elia.agent-name:trigger_agent_name.sh:agent_name.log:Agent Display Name"
)

# ── Helpers ────────────────────────────────────────────────────────

find_subworker_index() {
  local name="$1"
  for i in {1..${#SUBWORKERS[@]}}; do
    local entry="${SUBWORKERS[$i]}"
    local dir="${entry%%:*}"
    if [[ "$dir" == "$name" ]]; then
      echo "$i"
      return 0
    fi
  done
  return 1
}

get_field() {
  local index="$1"
  local field="$2"
  local entry="${SUBWORKERS[$index]}"
  echo "$entry" | cut -d':' -f"$field"
}

subworker_dir_exists() {
  [[ -d "${SW_DIR}/$1" ]]
}

trigger_script_exists() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && return 1
  local script=$(get_field "$idx" 3)
  [[ -f "${SCRIPTS_DIR}/${script}" ]]
}

plist_local_exists() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && return 1
  local plist=$(get_field "$idx" 2)
  [[ -f "${PLISTS_DIR}/${plist}.plist" ]]
}

plist_launchd_exists() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && return 1
  local plist=$(get_field "$idx" 2)
  [[ -f "${LAUNCHD_DIR}/${plist}.plist" ]]
}

plist_is_loaded() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && return 1
  local plist=$(get_field "$idx" 2)
  launchctl list "$plist" >/dev/null 2>&1
}

is_enabled() {
  [[ -f "${SW_DIR}/$1/.enabled" ]]
}

# ── Commands ────────────────────────────────────────────────────────

list_subworkers() {
  echo ""
  echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
  echo -e "${CYAN}  Subworkers Status${NC}"
  echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
  printf "  %-24s %-8s %-8s %-8s %-8s\n" "SUBWORKER" "ENABLED" "PLIST" "LAUNCHD" "SCRIPT"
  echo "  ─────────────────────────────────────────────────────────────"

  local has_active=false
  local count=${#SUBWORKERS[@]}
  for ((i=1; i<=count; i++)); do
    local entry="${SUBWORKERS[$i]}"
    local dir="${entry%%:*}"
    local display_name="${entry##*:}"

    local e_txt="OFF"
    local s_txt="YES"
    local p_txt="--"
    local l_txt="--"
    is_enabled "$dir"         && e_txt="ON"
    trigger_script_exists "$dir" || s_txt="--"
    plist_launchd_exists "$dir"  && p_txt="YES"
    plist_is_loaded "$dir"       && l_txt="YES"

    printf "  %-24s %-8s %-8s %-8s %-8s\n" "$display_name" "$e_txt" "$p_txt" "$l_txt" "$s_txt"
    is_enabled "$dir" && has_active=true
  done

  echo ""
  if $has_active; then
    warn "Some subworkers are ENABLED — they will run on schedule."
  else
    success "All subworkers are DISABLED."
  fi
  echo ""
}

status_subworker() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  if [[ -z "$idx" ]]; then
    error "Unknown subworker: $name"
    return 1
  fi

  local dir=$(get_field "$idx" 1)
  local plist=$(get_field "$idx" 2)
  local script=$(get_field "$idx" 3)
  local logname=$(get_field "$idx" 4)
  local display=$(get_field "$idx" 5)

  echo ""
  echo -e "${CYAN}────────────────────────────────────────────────${NC}"
  echo -e "${CYAN}  Subworker: ${display}${NC}"
  echo -e "${CYAN}────────────────────────────────────────────────${NC}"

  if subworker_dir_exists "$dir"; then
    echo -e "  Directory:   ${GREEN}${SW_DIR}/${dir}${NC}"
  else
    echo -e "  Directory:   ${RED}MISSING (${SW_DIR}/${dir})${NC}"
  fi

  if is_enabled "$dir"; then
    e="✅ ENABLED"
  else
    e="❌ DISABLED"
  fi
  echo -e "  .enabled:    $e"

  if trigger_script_exists "$name"; then
    echo -e "  Script:      ${GREEN}${SCRIPTS_DIR}/${script}${NC}"
  else
    echo -e "  Script:      ${RED}NOT FOUND${NC}"
  fi

  if plist_local_exists "$name"; then
    echo -e "  Plist (src): ${GREEN}${PLISTS_DIR}/${plist}.plist${NC}"
  else
    echo -e "  Plist (src): ${RED}NOT FOUND${NC}"
  fi

  if plist_launchd_exists "$name"; then
    echo -e "  Plist (ld):  ${GREEN}${LAUNCHD_DIR}/${plist}.plist${NC}"
    if plist_is_loaded "$name"; then
      echo -e "  Launchd:     ${GREEN}✅ Loaded${NC}"
    else
      echo -e "  Launchd:     ${RED}❌ Not loaded (plist present but inactive)${NC}"
    fi
  else
    echo -e "  Plist (ld):  ${RED}NOT INSTALLED in ~/Library/LaunchAgents${NC}"
  fi

  local logfile="${LOGS_DIR}/${logname}"
  if [[ -f "$logfile" ]]; then
    local size=$(du -h "$logfile" 2>/dev/null | cut -f1)
    local lines=$(wc -l < "$logfile" 2>/dev/null)
    local last=$(tail -3 "$logfile" 2>/dev/null || echo "N/A")
    echo -e "  Log file:    ${logfile}"
    echo -e "  Log size:    ${size} (${lines} lines)"
    echo -e "  Last lines:"
    echo "$last" | sed 's/^/    /'
  else
    echo -e "  Log file:    ${YELLOW}No log yet${NC}"
  fi
  echo ""
}

enable_subworker() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && { error "Unknown subworker: $name"; return 1; }

  local dir=$(get_field "$idx" 1)
  local plist=$(get_field "$idx" 2)
  local display=$(get_field "$idx" 5)

  touch "${SW_DIR}/${dir}/.enabled"
  success "${display}: .enabled created"

  if plist_local_exists "$name"; then
    mkdir -p "$LAUNCHD_DIR"
    cp "${PLISTS_DIR}/${plist}.plist" "${LAUNCHD_DIR}/${plist}.plist"

    if grep -q '<key>Disabled</key>' "${LAUNCHD_DIR}/${plist}.plist" 2>/dev/null; then
      sed -i '' '/<key>Disabled<\/key>/{n;s/<true\/>/<false\/>/;}' \
        "${LAUNCHD_DIR}/${plist}.plist"
    fi

    launchctl load "${LAUNCHD_DIR}/${plist}.plist" 2>&1 || \
      launchctl bootstrap "gui/$(id -u)" "${LAUNCHD_DIR}/${plist}.plist" 2>&1 || true

    success "${display}: plist installed in ~/Library/LaunchAgents and loaded"
  else
    warn "${display}: no plist found in subworkers/plists/ — skipping launchd install"
  fi

  echo ""
}

disable_subworker() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && { error "Unknown subworker: $name"; return 1; }

  local dir=$(get_field "$idx" 1)
  local plist=$(get_field "$idx" 2)
  local display=$(get_field "$idx" 5)

  rm -f "${SW_DIR}/${dir}/.enabled"
  success "${display}: .enabled removed"

  if plist_is_loaded "$name" 2>/dev/null; then
    launchctl bootout "gui/$(id -u)/${plist}" 2>/dev/null || \
    launchctl unload "${LAUNCHD_DIR}/${plist}.plist" 2>/dev/null || true
    success "${display}: unloaded from launchd"
  fi

  if plist_launchd_exists "$name"; then
    if grep -q '<key>Disabled</key>' "${LAUNCHD_DIR}/${plist}.plist" 2>/dev/null; then
      sed -i '' '/<key>Disabled<\/key>/{n;s/<false\/>/<true\/>/;}' \
        "${LAUNCHD_DIR}/${plist}.plist"
    fi
    success "${display}: plist marked Disabled=true"
  fi

  echo ""
}

install_subworker() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && { error "Unknown subworker: $name"; return 1; }

  local dir=$(get_field "$idx" 1)
  local plist=$(get_field "$idx" 2)
  local display=$(get_field "$idx" 5)

  if ! plist_local_exists "$name"; then
    error "${display}: no plist found at ${PLISTS_DIR}/${plist}.plist"
    return 1
  fi

  mkdir -p "$LAUNCHD_DIR"
  cp "${PLISTS_DIR}/${plist}.plist" "${LAUNCHD_DIR}/${plist}.plist"
  launchctl load "${LAUNCHD_DIR}/${plist}.plist" 2>&1 || \
    launchctl bootstrap "gui/$(id -u)" "${LAUNCHD_DIR}/${plist}.plist" 2>&1 || true

  success "${display}: plist installed and loaded"
  echo ""
}

uninstall_subworker() {
  local name="$1"
  local idx=$(find_subworker_index "$name")
  [[ -z "$idx" ]] && { error "Unknown subworker: $name"; return 1; }

  local dir=$(get_field "$idx" 1)
  local plist=$(get_field "$idx" 2)
  local display=$(get_field "$idx" 5)

  if plist_launchd_exists "$name"; then
    launchctl bootout "gui/$(id -u)/${plist}" 2>/dev/null || \
    launchctl unload "${LAUNCHD_DIR}/${plist}.plist" 2>/dev/null || true
    rm -f "${LAUNCHD_DIR}/${plist}.plist"
    success "${display}: plist removed from ~/Library/LaunchAgents"
  else
    warn "${display}: no plist in ~/Library/LaunchAgents"
  fi

  echo ""
}

# ── Usage ──────────────────────────────────────────────────────────

show_usage() {
  cat << 'EOF'
Usage: ./manage_subworkers.sh [command] [subworker_name]

Commands:
  (no command)      List all subworkers with enable/plist/launchd status
  enable <name>     Enable subworker: create .enabled + install plist + load
  disable <name>    Disable subworker: remove .enabled + unload plist
  status <name>     Show detailed status for one subworker
  install <name>    Install plist to ~/Library/LaunchAgents + load (no .enabled)
  uninstall <name>  Remove plist from ~/Library/LaunchAgents (keep .enabled)

Subworkers:
  (Edit the SUBWORKERS array at the top of this script to add yours)

Examples:
  ./manage_subworkers.sh                          # show status table
  ./manage_subworkers.sh enable my-agent          # enable and install
  ./manage_subworkers.sh disable my-agent          # disable and unload
  ./manage_subworkers.sh status my-agent           # detailed status
EOF
}

# ── Main ───────────────────────────────────────────────────────────

main() {
  local cmd="${1:-}"
  local sw_name="${2:-}"

  mkdir -p "$LOGS_DIR" 2>/dev/null || true

  case "$cmd" in
    "")
      list_subworkers
      ;;

    list|status|show)
      if [[ -n "$sw_name" ]]; then
        status_subworker "$sw_name"
      else
        list_subworkers
      fi
      ;;

    enable)
      [[ -z "$sw_name" ]] && { error "Usage: $0 enable <subworker_name>"; show_usage; exit 1; }
      enable_subworker "$sw_name"
      ;;

    disable)
      [[ -z "$sw_name" ]] && { error "Usage: $0 disable <subworker_name>"; show_usage; exit 1; }
      disable_subworker "$sw_name"
      ;;

    install)
      [[ -z "$sw_name" ]] && { error "Usage: $0 install <subworker_name>"; show_usage; exit 1; }
      install_subworker "$sw_name"
      ;;

    uninstall)
      [[ -z "$sw_name" ]] && { error "Usage: $0 uninstall <subworker_name>"; show_usage; exit 1; }
      uninstall_subworker "$sw_name"
      ;;

    --help|-h|help)
      show_usage
      ;;

    *)
      local idx=$(find_subworker_index "$cmd")
      if [[ -n "$idx" ]]; then
        status_subworker "$cmd"
      else
        error "Unknown command or subworker: $cmd"
        show_usage
        exit 1
      fi
      ;;
  esac
}

main "$@"
