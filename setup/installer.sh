#!/bin/zsh
# installer.sh - Full macOS installer for EliaAI + OpenCode + oh-my-opencode

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
ELIA_ROOT="$(dirname "$SCRIPT_DIR")"
OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"

log()  { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1" >&2; }
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
step() { echo -e "${BOLD}${CYAN}➤ $1${NC}"; }

BUN_INSTALLED=false
NODE_INSTALLED=false
GIT_INSTALLED=false
OPENCODE_INSTALLED=false
OMO_INSTALLED=false

check() {
    if command -v $1 &> /dev/null; then
        VERSION=$($1 --version 2>&1 | head -1 || echo "found")
        ok "$1: $($1 --version 2>&1 | head -1 || echo $1)"
        [[ "$1" == "bun" ]] && BUN_INSTALLED=true
        [[ "$1" == "node" || "$1" == "nodejs" ]] && NODE_INSTALLED=true
        [[ "$1" == "git" ]] && GIT_INSTALLED=true
        return 0
    fi
    return 1
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ${BOLD}EliaAI + OpenCode Installer${NC}  (macOS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

step "Phase 1: Checking system prerequisites"
log "Checking installed tools..."

check "bun" || info "bun: NOT FOUND - will install"
check "node" || check "nodejs" || info "node: NOT FOUND - will install"
check "git" || info "git: NOT FOUND - will install"

echo ""

# ─── Install system deps ───────────────────────────────────────────────────
if [[ "$BUN_INSTALLED" != "true" ]]; then
    step "Installing bun..."
    curl -fsSL https://bun.sh/install | bash
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
    if command -v bun &> /dev/null; then
        ok "bun installed: $(bun --version)"
    else
        err "bun installation failed"
        info "After script: run 'curl -fsSL https://bun.sh/install | bash' then re-run this installer"
        exit 1
    fi
fi

if [[ "$NODE_INSTALLED" != "true" ]]; then
    step "Installing Node.js..."
    if command -v brew &> /dev/null; then
        brew install node
    else
        curl -fsSL https://fnm.vercel.app/install | bash
        fnm install 20
        fnm use 20
    fi
    ok "Node.js installed: $(node --version)"
fi

if [[ "$GIT_INSTALLED" != "true" ]]; then
    step "Installing git..."
    if command -v brew &> /dev/null; then
        brew install git
    fi
fi

echo ""

# ─── Install OpenCode CLI ─────────────────────────────────────────────────
step "Phase 2: Installing OpenCode CLI"
OPENCODE_PATH=""
if command -v opencode &> /dev/null; then
    ok "OpenCode already installed: $(opencode --version 2>&1 | head -1)"
    OPENCODE_INSTALLED=true
    OPENCODE_PATH=$(which opencode)
else
    log "Installing OpenCode CLI..."
    info "Installation options:"
    info "  1. Visit https://opencode.ai/ and download the macOS app"
    info "  2. OR: npm install -g opencode"
    info "  3. OR: curl -sSL https://opencode.ai/install.sh | sh"
    echo ""
    read -q "REPLY?Do you want to install OpenCode via npm now? [y/N] "
    echo ""
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        npm install -g opencode
        if command -v opencode &> /dev/null; then
            ok "OpenCode installed: $(opencode --version 2>&1 | head -1)"
            OPENCODE_INSTALLED=true
            OPENCODE_PATH=$(which opencode)
        else
            warn "OpenCode installation via npm may have failed"
        fi
    fi

    if [[ "$OPENCODE_INSTALLED" != "true" ]]; then
        warn "OpenCode CLI not found. Please install manually from https://opencode.ai/"
        info "After installing, re-run this script or manually run: opencode"
    fi
fi

echo ""

# ─── Install oh-my-opencode ───────────────────────────────────────────────
step "Phase 3: Installing oh-my-opencode"
if command -v oh-my-opencode &> /dev/null; then
    ok "oh-my-opencode already installed: $(oh-my-opencode --version 2>&1 | head -1)"
    OMO_INSTALLED=true
else
    log "Installing oh-my-opencode via bun..."
    bunx oh-my-opencode install --no-tui --claude=no --openai=no --gemini=no --copilot=no --opencode-zen=yes
    if command -v oh-my-opencode &> /dev/null; then
        ok "oh-my-opencode installed: $(oh-my-opencode --version 2>&1 | head -1)"
        OMO_INSTALLED=true
    else
        warn "oh-my-opencode installation may have failed"
        info "Try manually: bunx oh-my-opencode install"
    fi
fi

echo ""

# ─── Set up OpenCode config directory ────────────────────────────────────
step "Phase 4: Setting up OpenCode configuration"

if [[ ! -d "$OPENCODE_CONFIG_DIR" ]]; then
    log "Creating OpenCode config directory: $OPENCODE_CONFIG_DIR"
    mkdir -p "$OPENCODE_CONFIG_DIR"
fi

# Copy EliaAI context files if they exist
CONTEXT_DIR="${ELIA_ROOT}/context"
if [[ -d "$CONTEXT_DIR" ]]; then
    log "Found context/ directory in EliaAI"
    info "Context files are part of EliaAI and managed separately"
fi

# Agent personality files
AGENTS_DIR="${OPENCODE_CONFIG_DIR}/agents"
if [[ ! -d "$AGENTS_DIR" ]]; then
    log "Creating agents directory: $AGENTS_DIR"
    mkdir -p "$AGENTS_DIR"
fi

# Skills directory
SKILLS_DIR="${OPENCODE_CONFIG_DIR}/skills"
if [[ ! -d "$SKILLS_DIR" ]]; then
    log "Creating skills directory: $SKILLS_DIR"
    mkdir -p "$SKILLS_DIR"
fi

# Themes directory
THEMES_DIR="${OPENCODE_CONFIG_DIR}/themes"
if [[ ! -d "$THEMES_DIR" ]]; then
    log "Creating themes directory: $THEMES_DIR"
    mkdir -p "$THEMES_DIR"
fi

# Docs directory
DOCS_DIR="${OPENCODE_CONFIG_DIR}/docs"
if [[ ! -d "$DOCS_DIR" ]]; then
    log "Creating docs directory: $DOCS_DIR"
    mkdir -p "$DOCS_DIR"
fi

# Plugin directory
PLUGIN_DIR="${OPENCODE_CONFIG_DIR}/plugin"
if [[ ! -d "$PLUGIN_DIR" ]]; then
    log "Creating plugin directory: $PLUGIN_DIR"
    mkdir -p "$PLUGIN_DIR"
fi

ok "Config directories created"

echo ""

# ─── Apply recommended configs ────────────────────────────────────────────
step "Phase 5: Applying recommended configuration"

# Create minimal config.json (no paid providers, big-pickle only)
CONFIG_JSON="${OPENCODE_CONFIG_DIR}/config.json"
if [[ ! -f "$CONFIG_JSON" ]]; then
    log "Creating config.json with big-pickle only..."
    cat > "$CONFIG_JSON" << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "allow",
    "edit": "allow",
    "glob": "allow",
    "grep": "allow",
    "list": "allow",
    "bash": "allow",
    "task": "allow",
    "external_directory": "allow",
    "todowrite": "allow",
    "todoread": "allow",
    "question": "allow",
    "webfetch": "allow",
    "websearch": "allow",
    "codesearch": "allow",
    "lsp": "allow",
    "doom_loop": "allow",
    "skill": "allow"
  },
  "theme": "dracula"
}
EOF
    ok "config.json created (dracula theme, big-pickle only)"
else
    info "config.json already exists - skipping"
fi

# Create oh-my-opencode.json with big-pickle only, no fallbacks
OMO_JSON="${OPENCODE_CONFIG_DIR}/oh-my-opencode.json"
if [[ ! -f "$OMO_JSON" ]]; then
    log "Creating oh-my-opencode.json..."
    cat > "$OMO_JSON" << 'EOF'
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
  "model_fallback": false,
  "default_run_agent": "sisyphus",
  "agents": {
    "sisyphus": { "model": "opencode/big-pickle", "fallback_models": [] },
    "sisyphus-junior": { "model": "opencode/big-pickle", "fallback_models": [] },
    "hephaestus": { "model": "opencode/big-pickle", "fallback_models": [] },
    "prometheus": { "model": "opencode/big-pickle", "fallback_models": [] },
    "metis": { "model": "opencode/big-pickle", "fallback_models": [] },
    "atlas": { "model": "opencode/big-pickle", "fallback_models": [] },
    "oracle": { "model": "opencode/big-pickle", "fallback_models": [] },
    "librarian": { "model": "opencode/big-pickle", "fallback_models": [] },
    "explore": { "model": "opencode/big-pickle", "fallback_models": [] },
    "momus": { "model": "opencode/big-pickle", "fallback_models": [] }
  },
  "agent_display_names": {
    "sisyphus": "Elia"
  }
}
EOF
    ok "oh-my-opencode.json created (big-pickle only, no fallbacks)"
else
    info "oh-my-opencode.json already exists - skipping"
fi

# Rate limit fallback config
RLF_JSON="${OPENCODE_CONFIG_DIR}/rate-limit-fallback.json"
if [[ ! -f "$RLF_JSON" ]]; then
    log "Creating rate-limit-fallback.json..."
    cat > "$RLF_JSON" << 'EOF'
{
  "enabled": true,
  "fallbackModel": "opencode/big-pickle",
  "cooldownMs": 60000,
  "patterns": [
    "rate limit", "usage limit", "too many requests",
    "quota exceeded", "overloaded", "capacity exhausted",
    "limit exceeded", "rate_limit_exceeded",
    "RESOURCE_EXHAUSTED", "No capacity available"
  ],
  "logging": true
}
EOF
    ok "rate-limit-fallback.json created"
fi

# Install Dracula theme
DRACULA_JSON="${THEMES_DIR}/dracula.json"
if [[ ! -f "$DRACULA_JSON" ]]; then
    log "Installing Dracula theme..."
    cat > "$DRACULA_JSON" << 'EOF'
{
  "black": "#000000",
  "red": "#ff5555",
  "green": "#50fa7b",
  "yellow": "#f1fa8c",
  "blue": "#6272a4",
  "magenta": "#ff79c6",
  "cyan": "#8be9fd",
  "white": "#f8f8f2",
  "brightBlack": "#555555",
  "brightRed": "#ff6e67",
  "brightGreen": "#69ff94",
  "brightYellow": "#ffffa5",
  "brightBlue": "#d6acff",
  "brightMagenta": "#ff92df",
  "brightCyan": "#a4ffff",
  "brightWhite": "#ffffff",
  "background": "#282a36",
  "foreground": "#f8f8f2",
  "selectionBackground": "#44475a",
  "cursorColor": "#f8f8f2"
}
EOF
    ok "Dracula theme installed"
fi

echo ""

# ─── Install rate-limit-fallback plugin ─────────────────────────────────
step "Phase 6: Installing rate-limit-fallback plugin"

RLF_PLUGIN="${PLUGIN_DIR}/rate-limit-fallback"
if [[ ! -d "$RLF_PLUGIN" ]]; then
    log "Installing rate-limit-fallback plugin..."
    mkdir -p "$RLF_PLUGIN/src"

    cat > "$RLF_PLUGIN/package.json" << 'EOF'
{
  "name": "rate-limit-fallback",
  "version": "1.0.0",
  "type": "module"
}
EOF

    cat > "$RLF_PLUGIN/src/config.ts" << 'EOFTS'
const DEFAULT_CONFIG = {
  enabled: true,
  fallbackModel: "opencode/big-pickle",
  cooldownMs: 300000,
  patterns: ["rate limit", "usage limit", "too many requests", "quota exceeded", "overloaded"],
  logging: false,
};
export function loadConfig() { return DEFAULT_CONFIG; }
export function parseModel(model) {
  const slashIndex = model.indexOf("/");
  if (slashIndex === -1) return { providerID: model, modelID: model };
  return { providerID: model.substring(0, slashIndex), modelID: model.substring(slashIndex + 1) };
}
EOFTS

    ok "rate-limit-fallback plugin installed"
else
    info "rate-limit-fallback plugin already exists - skipping"
fi

echo ""

# ─── Fix permissions ─────────────────────────────────────────────────────
step "Phase 7: Finalizing permissions..."
chmod 644 "$CONFIG_JSON" "$OMO_JSON" "$RLF_JSON" "$DRACULA_JSON" 2>/dev/null || true
chmod -R 755 "${OPENCODE_CONFIG_DIR}"/*/ 2>/dev/null || true
ok "Permissions set"

echo ""

# ─── Summary ─────────────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ok "Installation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
info "Installed:"
[[ "$BUN_INSTALLED" == "true" ]] && ok "  • bun ($(bun --version 2>&1 | head -1))"
[[ "$NODE_INSTALLED" == "true" ]] && ok "  • node ($(node --version 2>&1 | head -1))"
[[ "$OPENCODE_INSTALLED" == "true" ]] && ok "  • opencode ($(opencode --version 2>&1 | head -1))"
[[ "$OMO_INSTALLED" == "true" ]] && ok "  • oh-my-opencode ($(oh-my-opencode --version 2>&1 | head -1))"
ok "  • config directories"
ok "  • Dracula theme"
ok "  • rate-limit-fallback plugin"
echo ""
info "Config location: $OPENCODE_CONFIG_DIR"
info "Backup scripts: ${ELIA_ROOT}/setup/backup_config.sh"
info "Restore script:  ${ELIA_ROOT}/setup/restore_config.sh"
echo ""
info "To start EliaAI:"
info "  cd ${ELIA_ROOT}"
info "  opencode"
echo ""
