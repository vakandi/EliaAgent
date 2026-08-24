#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Rebuild oh-my-openagent from source and deploy to bun runtime locations.
# Usage: bash scripts/rebuild-oh-my-openagent.sh

SRC=""$HOME/EliaAI"/setup/oh-my-openagent"
BUN_CACHE="$HOME/.bun/install/cache"
BUN_GLOBAL="$HOME/.bun/install/global/node_modules"
LOGFILE="/tmp/rebuild-omo-$(date +%Y%m%d%H%M%S).log"

log()  { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOGFILE"; }
die()  { echo "[$(date '+%H:%M:%S')] ERROR: $*" | tee -a "$LOGFILE" >&2; exit 1; }

# --- Preflight ---
[[ -d "$SRC" ]] || die "Source directory not found: $SRC"
command -v bun >/dev/null 2>&1 || die "bun not found in PATH"

# Find the installed oh-my-opencode version dir in bun cache
OC_CACHE_DIR=$(find "$BUN_CACHE" -maxdepth 1 -type d -name "oh-my-opencode@*@@@*" 2>/dev/null | sort -V | tail -1)
[[ -n "$OC_CACHE_DIR" ]] || die "No oh-my-opencode cache dir found in $BUN_CACHE"
OC_CACHE_JS="$OC_CACHE_DIR/dist/index.js"

# Find the global install dir
OC_GLOBAL_DIR="$BUN_GLOBAL/oh-my-opencode"
OC_GLOBAL_JS="$OC_GLOBAL_DIR/dist/index.js"

log "Source:        $SRC"
log "Cache target:  $OC_CACHE_JS"
log "Global target: $OC_GLOBAL_JS"

# --- Step 1: Clean opencode plugin cache ---
log "Step 1/5: Cleaning opencode plugin cache..."
rm -rf "$HOME/.cache/opencode/packages/oh-my-openagent"*
log "  Done."

# --- Step 2: Rebuild ESM bundle ---
log "Step 2/5: Building ESM bundle from source..."
cd "$SRC"
bun build packages/omo-opencode/src/index.ts \
  --outdir dist \
  --target bun \
  --format esm \
  --external zod \
  2>&1 | tee -a "$LOGFILE"
[[ -f dist/index.js ]] || die "Build failed — dist/index.js not found"
BUILD_SIZE=$(du -h dist/index.js | cut -f1)
log "  Built dist/index.js ($BUILD_SIZE)"

# --- Step 3: Apply node-require-shim ---
log "Step 3/5: Applying node-require-shim patch..."
bun run script/patch-node-require-shim.ts 2>&1 | tee -a "$LOGFILE"
log "  Done."

# --- Step 4: Deploy to bun cache ---
log "Step 4/5: Deploying to bun cache..."
if [[ -f "$OC_CACHE_JS" ]]; then
  cp dist/index.js "$OC_CACHE_JS"
  log "  Copied to $OC_CACHE_JS"
else
  log "  WARN: Cache file $OC_CACHE_JS does not exist, skipping."
fi

# --- Step 5: Deploy to bun global ---
log "Step 5/5: Deploying to bun global install..."
if [[ -f "$OC_GLOBAL_JS" ]]; then
  cp dist/index.js "$OC_GLOBAL_JS"
  log "  Copied to $OC_GLOBAL_JS"
else
  log "  WARN: Global file $OC_GLOBAL_JS does not exist, skipping."
fi

# --- Done ---
echo ""
log "=== REBUILD COMPLETE ==="
log "All done. Restart opencode to load the new plugin."
