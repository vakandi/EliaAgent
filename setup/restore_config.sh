#!/bin/zsh
# restore_config.sh - Restore OpenCode + oh-my-opencode from backup

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

SCRIPT_DIR="${0:a:h}"
ELIA_ROOT="${SCRIPT_DIR}"
OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"
BACKUP_FILE=""
RESTORE_DIR=""
FORCE_RESTORE=false

log()  { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1" >&2; }
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }

show_usage() {
    cat << 'USAGE_EOF'
Usage: ./restore_config.sh <backup_file> [--force]

Options:
  <backup_file>    Path to .zip or .tar.gz backup file
  --force          Overwrite existing configs without prompting
  -h, --help       Show this help

Examples:
  ./restore_config.sh backups/elia_config_backup_20260319_120000.zip
  ./restore_config.sh /tmp/my_backup.zip --force
USAGE_EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --force) FORCE_RESTORE=true; shift ;;
        -h|--help) show_usage; exit 0 ;;
        -*) err "Unknown option: $1"; show_usage; exit 1 ;;
        *) BACKUP_FILE="$1"; shift ;;
    esac
done

if [[ -z "$BACKUP_FILE" ]]; then
    err "No backup file specified."
    show_usage
    exit 1
fi

BACKUP_FILE="${BACKUP_FILE:A}"
if [[ ! -f "$BACKUP_FILE" ]]; then
    err "Backup file not found: $BACKUP_FILE"
    exit 1
fi

EXT="${BACKUP_FILE##*.}"
if [[ "$EXT" != "zip" && "$EXT" != "gz" ]]; then
    warn "Unknown backup format: .$EXT (expected .zip or .tar.gz)"
    info "Will attempt to extract anyway..."
fi

log "Starting restore from: $BACKUP_FILE"

for cmd in unzip tar; do
    if ! command -v $cmd &> /dev/null; then
        err "Missing required command: $cmd"
        info "Install with: brew install $cmd"
        exit 1
    fi
done

RESTORE_DIR="${ELIA_ROOT}/.restore_$$"
log "Creating staging directory..."
mkdir -p "$RESTORE_DIR"

cleanup() { rm -rf "$RESTORE_DIR"; }
trap cleanup EXIT

log "Extracting backup..."
cd "$RESTORE_DIR"
if [[ "$EXT" == "zip" ]]; then
    unzip -q "$BACKUP_FILE" || { err "Failed to extract ZIP"; exit 1; }
elif [[ "$BACKUP_FILE" == *.tar.gz ]]; then
    tar xzf "$BACKUP_FILE" || { err "Failed to extract tar.gz"; exit 1; }
else
    unzip -q "$BACKUP_FILE" || { err "Failed to extract backup"; exit 1; }
fi

if [[ -f "$RESTORE_DIR/backup_info.txt" ]]; then
    info "Backup info:"
    cat "$RESTORE_DIR/backup_info.txt" | grep -v "^#" | grep -v "^$"
fi

HAS_OPENCODE_CONFIG=false
HAS_OMO_PKG=false
[[ -d "$RESTORE_DIR/opencode_config" && -n "$(ls -A "$RESTORE_DIR/opencode_config" 2>/dev/null)" ]] && HAS_OPENCODE_CONFIG=true
[[ -d "$RESTORE_DIR/oh-my-opencode_pkg" && -n "$(ls -A "$RESTORE_DIR/oh-my-opencode_pkg" 2>/dev/null)" ]] && HAS_OMO_PKG=true

log "Backup contents:"
[[ "$HAS_OPENCODE_CONFIG" == "true" ]] && ok "  - opencode_config/" || warn "  - opencode_config/ (empty/not found)"
[[ "$HAS_OMO_PKG" == "true" ]] && ok "  - oh-my-opencode_pkg/" || warn "  - oh-my-opencode_pkg/ (empty/not found)"

if [[ "$FORCE_RESTORE" != "true" ]]; then
    echo ""
    info "This will restore configs to:"
    info "  - $OPENCODE_CONFIG_DIR/"
    if [[ "$HAS_OMO_PKG" == "true" ]]; then
        info "  - npm global node_modules/ (oh-my-opencode)"
    fi
    echo ""
    read -q "REPLY?Continue with restore? [y/N] "
    echo ""
    if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
        log "Restore cancelled."
        exit 0
    fi
fi

if [[ "$HAS_OPENCODE_CONFIG" == "true" ]]; then
    log "Restoring ~/.config/opencode/..."
    BACKUP_CONFIG="$RESTORE_DIR/opencode_config"
    TOTAL_FILES=$(find "$BACKUP_CONFIG" -type f 2>/dev/null | wc -l | tr -d ' ')

    if [[ -d "$OPENCODE_CONFIG_DIR" ]]; then
        if [[ "$FORCE_RESTORE" == "true" ]]; then
            log "Backing up existing config first..."
            "${SCRIPT_DIR}/backup_config.sh" --output "${ELIA_ROOT}/backups/pre_restore_$(date +%Y%m%d_%H%M%S).zip" 2>/dev/null || true
        fi
        info "Merging into existing directory..."
        cp -rn "$BACKUP_CONFIG"/* "$OPENCODE_CONFIG_DIR/" 2>/dev/null || true
    else
        log "Creating new config directory..."
        mkdir -p "$OPENCODE_CONFIG_DIR"
        cp -r "$BACKUP_CONFIG"/* "$OPENCODE_CONFIG_DIR/" 2>/dev/null || true
    fi

    ok "Restored $TOTAL_FILES files to ~/.config/opencode/"
else
    warn "No opencode_config/ found in backup - skipping"
fi

if [[ "$HAS_OMO_PKG" == "true" ]]; then
    log "Restoring oh-my-opencode npm package..."
    OMO_PKG_JSON="$RESTORE_DIR/oh-my-opencode_pkg/package.json"
    OMO_VERSION="unknown"
    if [[ -f "$OMO_PKG_JSON" ]]; then
        OMO_VERSION=$(grep '"version"' "$OMO_PKG_JSON" 2>/dev/null | head -1 | sed 's/[^0-9.]//g')
        info "Package version: $OMO_VERSION"
    fi

    NPM_PREFIX=$(npm prefix -g 2>/dev/null || echo "${HOME}/.npm-global/lib/node_modules")
    if [[ -z "$NPM_PREFIX" ]]; then
        NPM_PREFIX="${HOME}/.npm-global/lib/node_modules"
    fi
    OMO_TARGET_DIR="${NPM_PREFIX}/oh-my-opencode"

    if [[ -d "$NPM_PREFIX" ]]; then
        log "Installing to global npm: $NPM_PREFIX"
        mkdir -p "$OMO_TARGET_DIR"
        cp -r "$RESTORE_DIR/oh-my-opencode_pkg"/* "$OMO_TARGET_DIR/" 2>/dev/null || true
        ok "Restored oh-my-opencode to $OMO_TARGET_DIR"

        if command -v npm &> /dev/null; then
            log "Linking oh-my-opencode binary..."
            npm link -g oh-my-opencode 2>/dev/null || warn "Could not npm link -g oh-my-opencode"
            if command -v oh-my-opencode &> /dev/null; then
                ok "Binary linked: $(which oh-my-opencode)"
            fi
        fi
    else
        warn "Global npm directory not found: $NPM_PREFIX"
        info "To install manually:"
        info "  npm install -g oh-my-opencode@${OMO_VERSION:-latest}"
        info "  OR: bunx oh-my-opencode install"
    fi
else
    warn "No oh-my-opencode_pkg/ found in backup"
    info "To install oh-my-opencode after restore:"
    info "  bunx oh-my-opencode install"
fi

log "Fixing file permissions..."
chmod 644 "$OPENCODE_CONFIG_DIR"/*.json "$OPENCODE_CONFIG_DIR"/*.md 2>/dev/null || true
chmod -R 755 "$OPENCODE_CONFIG_DIR"/*/ 2>/dev/null || true
ok "Permissions set"

echo ""
echo "========================================"
ok "Restore complete!"
echo "========================================"
echo ""
info "Next steps:"
info "  1. Verify: opencode --version"
info "  2. Verify: oh-my-opencode --version"
info "  3. Run: cd ${ELIA_ROOT} && opencode"
info "  4. If issues: ./installer.sh"
echo ""
