#!/usr/bin/env bash
# install.sh — one-time setup for the omp-server Bun wrapper (omp-server/).
#
# Usage:
#   ./install.sh [--no-docker] [--skip-upstream]
#
#   --no-docker      Skip `docker build` (deps + token + dirs only).
#   --skip-upstream  Assume omp-server/ already holds the omp SDK source
#                    (vendored checkout). Default is to fetch it if missing.
#
# What it does:
#   0. Fetches the omp SDK source into omp-server/ if it is not there yet
#      (see "upstream" below). No-op when the checkout already exists.
#   1. Checks prereqs: bun >= 1.3.14 (fatal), docker CLI (warn-only).
#   2. Runs `bun install` in omp-server/ (upstream manifest lives there).
#   3. Mints ELIA_AUTH_TOKEN into omp-server/.env (chmod 600) if absent, else keeps it.
#   4. Ensures omp-server/data + omp-server/config exist, and seeds the example
#      proxies pool from proxies.txt.example when no pool exists yet.
#   5. Builds the image: `docker build -f omp-server/Dockerfile -t omp-server .`
#
# Upstream: this repo ships ONLY the Elia wrapper layer. The agent runtime under
#   omp-server/packages, omp-server/crates and omp-server/assets is upstream
#   omp (https://github.com/can1357/oh-my-pi, MIT), ~180MB, and is NOT committed
#   here. install.sh fetches it at the pinned ref below; `--skip-upstream` opts out.
#   Upstream files are never edited — only the wrapper files at omp-server/*.ts,
#   omp-server/routes, omp-server/extensions, omp-server/config.
#
# Natives note: on darwin the .node binary resolves from the bun cache;
# on linux pack host natives via `bun --cwd=omp-server scripts/bazel-natives.ts host`.
#
# Next steps after install:
#   1. Edit omp-server/config/subworkers.json
#   2. Edit ~/.omp/agent/models.yml (provider `zen-free`) + ~/.omp/agent/agents/*.md
#   3. Run ./start.sh (or with --docker)
#   4. curl http://127.0.0.1:5677/health
set -euo pipefail
IFS=$'\n\t'

ROOT="$(cd "$(dirname "$0")" && pwd)"
ELIA_DIR="$ROOT/omp-server"
ENV_FILE="$ELIA_DIR/.env"
MIN_BUN="1.3.14"
WITH_DOCKER=1
SKIP_UPSTREAM=0

UPSTREAM_URL="https://github.com/can1357/oh-my-pi.git"
UPSTREAM_REF="78b7531"

log() { printf '[install] %s\n' "$*"; }
die() { printf '[install] ERROR: %s\n' "$*" >&2; exit 1; }

for arg in "$@"; do
  case "$arg" in
    --no-docker) WITH_DOCKER=0 ;;
    --skip-upstream) SKIP_UPSTREAM=1 ;;
    -h|--help)
      sed -n '1,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "unknown flag: $arg (see --help)" ;;
  esac
done

command -v bun >/dev/null 2>&1 || die "bun not found — install it: curl -fsSL https://bun.sh/install | bash"
BUN_VER="$(bun --version)"
log "bun $BUN_VER"
if [ "$(printf '%s\n%s\n' "$MIN_BUN" "$BUN_VER" | sort -V | head -n1)" != "$MIN_BUN" ]; then
  die "bun >= $MIN_BUN required (found $BUN_VER) — upgrade: bun upgrade"
fi

if command -v docker >/dev/null 2>&1; then
  log "docker: $(docker --version | head -n1)"
else
  log "WARNING: docker CLI not found — docker image build/run will be unavailable; continuing with host mode only."
fi

if [ "$SKIP_UPSTREAM" -eq 0 ]; then
  if [ -d "$ELIA_DIR/packages/coding-agent" ] && [ -d "$ELIA_DIR/crates" ]; then
    log "upstream omp source already present in omp-server/ — skipping fetch."
  else
    command -v git >/dev/null 2>&1 || die "git not found — needed to fetch the omp SDK source (or pass --skip-upstream)"
    TMP_UP="$(mktemp -d)"
    trap 'rm -rf "$TMP_UP"' EXIT
    log "fetching upstream omp @ $UPSTREAM_REF into omp-server/ (one-time, ~180MB)…"
    git clone --quiet --filter=blob:none --no-checkout "$UPSTREAM_URL" "$TMP_UP/omp"
    git -C "$TMP_UP/omp" sparse-checkout init --cone
    git -C "$TMP_UP/omp" sparse-checkout set packages crates assets python patches bazel nix infra scripts
    git -C "$TMP_UP/omp" checkout --quiet "$UPSTREAM_REF"
    for entry in packages crates assets python patches bazel nix infra; do
      [ -e "$TMP_UP/omp/$entry" ] && cp -R "$TMP_UP/omp/$entry" "$ELIA_DIR/"
    done
    for f in package.json bun.lock bun.lockb bunfig.toml Cargo.toml Cargo.lock MODULE.bazel MODULE.bazel.lock BUILD.bazel rust-toolchain.toml rustfmt.toml rust-analyzer.toml tsconfig.json tsconfig.base.json tsconfig.tools.json deny.toml about.toml; do
      [ -e "$TMP_UP/omp/$f" ] && cp "$TMP_UP/omp/$f" "$ELIA_DIR/"
    done
    cp -R "$TMP_UP/omp/scripts/." "$ELIA_DIR/scripts/" 2>/dev/null || true
    rm -rf "$TMP_UP"
    trap - EXIT
    log "upstream omp fetched. Never edit omp-server/packages or omp-server/crates."
  fi
fi

log "installing deps in omp-server/: $ROOT/omp-server"
(cd "$ROOT/omp-server" && bun install)

if [ -f "$ENV_FILE" ] && grep -q '^ELIA_AUTH_TOKEN=.\+' "$ENV_FILE" 2>/dev/null; then
  log "omp-server/.env already has ELIA_AUTH_TOKEN — keeping existing token."
else
  command -v openssl >/dev/null 2>&1 || die "openssl not found — required to mint ELIA_AUTH_TOKEN"
  TOKEN="$(openssl rand -hex 32)"
  if [ -f "$ENV_FILE" ]; then
    grep -v '^ELIA_AUTH_TOKEN=' "$ENV_FILE" > "$ENV_FILE.tmp" || true
    mv "$ENV_FILE.tmp" "$ENV_FILE"
    printf 'ELIA_AUTH_TOKEN=%s\n' "$TOKEN" >> "$ENV_FILE"
  else
    printf 'ELIA_AUTH_TOKEN=%s\n' "$TOKEN" > "$ENV_FILE"
  fi
  chmod 600 "$ENV_FILE"
  log "minted ELIA_AUTH_TOKEN into omp-server/.env (mode 600)."
fi

mkdir -p "$ELIA_DIR/data" "$ELIA_DIR/config" "$ELIA_DIR/extensions"
log "ensured omp-server/data + omp-server/config + omp-server/extensions exist."

PROXY_POOL="$ELIA_DIR/extensions/proxies.txt"
if [ ! -f "$PROXY_POOL" ] && [ -f "$ELIA_DIR/extensions/proxies.txt.example" ]; then
  cp "$ELIA_DIR/extensions/proxies.txt.example" "$PROXY_POOL"
  log "seeded omp-server/extensions/proxies.txt from the example pool (fill it or the model calls go direct)."
fi

log "natives: darwin .node resolves from bun cache; linux packs via \`bun --cwd=omp-server scripts/bazel-natives.ts host\`."

if [ "$WITH_DOCKER" -eq 1 ]; then
  command -v docker >/dev/null 2>&1 || die "docker CLI missing — re-run with --no-docker to skip the image build."
  log "building image: docker build -f omp-server/Dockerfile -t omp-server ."
  (cd "$ROOT" && docker build -f omp-server/Dockerfile -t omp-server .)
else
  log "skipping docker build (--no-docker)."
fi

cat <<'EOF'
[install] done. Next steps:
  1. Edit omp-server/config/subworkers.json (registry + models)
  2. Create ~/.omp/agent/models.yml (provider `zen-free`) and ~/.omp/agent/agents/<name>.md personas
  3. Fill omp-server/extensions/proxies.txt if you want per-run egress rotation
  4. Run ./start.sh        (or ./start.sh --docker)
  5. curl http://127.0.0.1:5677/health
EOF
