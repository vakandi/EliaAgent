#!/bin/zsh
# backup_config.sh - Backup all OpenCode + oh-my-opencode configs
# Run from anywhere, saves to setup/elia_backup_YYYYMMDD_HHMMSS.zip

set -euo pipefail

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR="${0:a:h}"
ELIA_ROOT="${SCRIPT_DIR:A}"
OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"
BACKUP_DIR="${ELIA_ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILENAME="elia_config_backup_${TIMESTAMP}.zip"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# ─── Logging helpers ──────────────────────────────────────────────────────────
log()  { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1" >&2; }
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }

# ─── Show usage ───────────────────────────────────────────────────────────────
show_usage() {
    cat << 'EOF'
Usage: ./backup_config.sh [--output PATH]

Options:
  --output PATH   Custom backup output path (default: setup/backups/)
  -h, --help      Show this help

Backup includes:
  • ~/.config/opencode/ (all files, agents, skills, plugins, themes, docs)
  • ~/.config/opencode/commands/ (custom commands directory)
  • ~/.config/opencode/command (custom command file)
  • oh-my-opencode npm package (if installed)
  • This script can be run from any location
EOF
}

# ─── Parse args ───────────────────────────────────────────────────────────────
CUSTOM_OUTPUT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --output) CUSTOM_OUTPUT="$2"; shift 2 ;;
        -h|--help) show_usage; exit 0 ;;
        *) err "Unknown option: $1"; show_usage; exit 1 ;;
    esac
done

if [[ -n "$CUSTOM_OUTPUT" ]]; then
    BACKUP_DIR="$(dirname "$CUSTOM_OUTPUT")"
    BACKUP_FILENAME="$(basename "$CUSTOM_OUTPUT")"
    BACKUP_PATH="$CUSTOM_OUTPUT"
fi

# ─── Check prerequisites ───────────────────────────────────────────────────────
log "Checking prerequisites..."

# Check if opencode config exists
if [[ ! -d "$OPENCODE_CONFIG_DIR" ]]; then
    warn "OpenCode config directory not found: $OPENCODE_CONFIG_DIR"
    info "OpenCode may not be installed. This is OK for backup purposes."
    OPENCODE_INSTALLED=false
else
    OPENCODE_INSTALLED=true
    ok "Found OpenCode config at: $OPENCODE_CONFIG_DIR"
fi

# ─── Check opencode installation ─────────────────────────────────────────────
log "Checking OpenCode installation..."

if command -v opencode &> /dev/null; then
    OPENCODE_VERSION=$(opencode --version 2>&1 | head -1 || echo "unknown")
    ok "OpenCode CLI found: $(which opencode) ($OPENCODE_VERSION)"
    OPENCODE_CLI_FOUND=true
else
    warn "OpenCode CLI not found in PATH"
    info "To install OpenCode, run:"
    info "  curl -sSL https://opencode.ai/install.sh | sh"
    info "  OR: npm install -g opencode"
    OPENCODE_CLI_FOUND=false
fi

# ─── Check oh-my-opencode installation ───────────────────────────────────────
log "Checking oh-my-opencode installation..."

if command -v oh-my-opencode &> /dev/null; then
    OMO_VERSION=$(oh-my-opencode --version 2>&1 | head -1 || echo "unknown")
    ok "oh-my-opencode found: $(which oh-my-opencode) ($OMO_VERSION)"
    OMO_INSTALLED=true
    OMO_PATH=$(which oh-my-opencode)
    # Find npm package path
    OMO_PKG_DIR=$(dirname "$(dirname "$OMO_PATH")")
    if [[ "$OMO_PKG_DIR" == *"/lib/node_modules" ]]; then
        OMO_FULL_PKG="${OMO_PKG_DIR}/node_modules/oh-my-opencode"
    else
        OMO_FULL_PKG=""
    fi
else
    warn "oh-my-opencode not found in PATH"
    info "To install oh-my-opencode, run:"
    info "  bunx oh-my-opencode install"
    info "  OR: npm install -g oh-my-opencode"
    OMO_INSTALLED=false
    OMO_FULL_PKG=""
fi

# ─── Find NVM node_modules path for oh-my-opencode ───────────────────────────
log "Searching for oh-my-opencode npm package..."
OMO_NPM_PKG=""
for nvm_dir in "$HOME"/.nvm/versions/node/*/lib/node_modules/oh-my-opencode; do
    if [[ -d "$nvm_dir" ]]; then
        OMO_NPM_PKG="$nvm_dir"
        ok "Found npm package: $OMO_NPM_PKG"
        break
    fi
done

if [[ -z "$OMO_NPM_PKG" && "$OMO_INSTALLED" == "true" ]]; then
    warn "oh-my-opencode CLI found but npm package location could not be determined"
    info "Package may be installed globally via a different method"
fi

# ─── Create backup directory ──────────────────────────────────────────────────
log "Creating backup directory..."
mkdir -p "$BACKUP_DIR"
ok "Backup directory: $BACKUP_DIR"

# ─── Create staging directory ────────────────────────────────────────────────
STAGING_DIR="${BACKUP_DIR}/.staging_${TIMESTAMP}"
log "Creating staging directory..."
mkdir -p "$STAGING_DIR/opencode_config"
mkdir -p "$STAGING_DIR/oh-my-opencode_pkg"

# ─── Backup OpenCode config ──────────────────────────────────────────────────
if [[ "$OPENCODE_INSTALLED" == "true" ]]; then
    log "Backing up ~/.config/opencode/ ..."

    # Copy entire opencode config directory
    cp -R "$OPENCODE_CONFIG_DIR"/* "$STAGING_DIR/opencode_config/" 2>/dev/null || true

    # Count files backed up
    FILE_COUNT=$(find "$STAGING_DIR/opencode_config" -type f 2>/dev/null | wc -l | tr -d ' ')
    ok "Backed up $FILE_COUNT files from ~/.config/opencode/"
else
    warn "Skipping opencode config backup (directory not found)"
fi

# ─── Backup oh-my-opencode npm package ───────────────────────────────────────
if [[ -n "$OMO_NPM_PKG" && -d "$OMO_NPM_PKG" ]]; then
    log "Backing up oh-my-opencode npm package..."
    cp -R "$OMO_NPM_PKG"/* "$STAGING_DIR/oh-my-opencode_pkg/" 2>/dev/null || true
    OMO_FILE_COUNT=$(find "$STAGING_DIR/oh-my-opencode_pkg" -type f 2>/dev/null | wc -l | tr -d ' ')
    ok "Backed up $OMO_FILE_COUNT files from oh-my-opencode npm package"
elif [[ "$OMO_INSTALLED" == "true" ]]; then
    warn "oh-my-opencode CLI found but npm package not found - CLI-only install"
    info "This means oh-my-opencode was installed globally without npm package"
else
    warn "Skipping oh-my-opencode package backup (not installed)"
fi

# ─── Save backup metadata ─────────────────────────────────────────────────────
log "Saving backup metadata..."
cat > "$STAGING_DIR/backup_info.txt" << EOF
# EliaAI Config Backup Info
# Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')
# Host: $(hostname)
# User: $(whoami)

OPENCODE_CONFIG_DIR: $OPENCODE_CONFIG_DIR
OPENCODE_INSTALLED: $OPENCODE_INSTALLED
OPENCODE_CLI_FOUND: $OPENCODE_CLI_FOUND
$(command -v opencode &> /dev/null && echo "OPENCODE_VERSION: $(opencode --version 2>&1 | head -1)" || echo "OPENCODE_VERSION: not found")

OH-MY-OPENCODE_INSTALLED: $OMO_INSTALLED
OH-MY-OPENCODE_CLI_PATH: $(command -v oh-my-opencode 2>/dev/null || echo "not found")
OH-MY-OPENCODE_NPM_PKG: $OMO_NPM_PKG
$(command -v oh-my-opencode &> /dev/null && echo "OH-MY-OPENCODE_VERSION: $(oh-my-opencode --version 2>&1 | head -1)" || echo "OH-MY-OPENCODE_VERSION: not found")

BACKUP_FILES_OPENCODE: $FILE_COUNT
BACKUP_FILES_OMO_PKG: ${OMO_FILE_COUNT:-0}
BACKUP_PATH: $BACKUP_PATH

# Contents:
# • opencode_config/ - Full ~/.config/opencode/ backup (including commands/ and command)
# • oh-my-opencode_pkg/ - oh-my-opencode npm package (if available)
# • backup_info.txt - This file

# To restore:
#   cd EliaAI/setup
#   ./restore_config.sh
EOF
ok "Metadata saved"

# ─── Create ZIP archive ───────────────────────────────────────────────────────
log "Creating ZIP archive..."
cd "$STAGING_DIR"

if command -v zip &> /dev/null; then
    zip -r "$BACKUP_PATH" . -x "*.DS_Store" 2>/dev/null
elif command -v 7z &> /dev/null; then
    7z a "$BACKUP_PATH" . -x!"*.DS_Store" > /dev/null 2>&1
else
    # Fallback to tar.gz if no zip
    TAR_PATH="${BACKUP_PATH%.zip}.tar.gz"
    tar czf "$TAR_PATH" . 2>/dev/null
    warn "zip/7z not found, created tar.gz instead: $TAR_PATH"
    BACKUP_PATH="$TAR_PATH"
fi

# ─── Cleanup staging ──────────────────────────────────────────────────────────
log "Cleaning up staging directory..."
rm -rf "$STAGING_DIR"

# ─── Final output ─────────────────────────────────────────────────────────────
if [[ -f "$BACKUP_PATH" ]]; then
    SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    ok "Backup created successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📦 Backup: $BACKUP_PATH"
    echo "  📊 Size:   $SIZE"
    echo "  📁 Files:  OpenCode config (${FILE_COUNT:-0}) + oh-my-opencode (${OMO_FILE_COUNT:-0})"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    info "To restore this backup:"
    info "  cd ${ELIA_ROOT}/setup"
    info "  ./restore_config.sh ${BACKUP_PATH}"
    echo ""
else
    err "Backup creation failed!"
    exit 1
fi
