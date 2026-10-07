# omp-server elia wrapper — Bun slim + Python (LinkedIn MCP browser scraping).
# Engine loopback-only inside the container; HTTP 5677:5677.
#
# Slimming strategy (source tree intact — every cut happens in this file):
# the install stage needs the FULL workspace (omp-server/package.json workspaces =
# `packages/*` + `python/robomp/web`, all package.jsons must exist for `bun
# install` to resolve), while the final stage carries only the server runtime
# graph: omp-server/*.ts + routes/ + config/ + node_modules + the SDK workspace closure.
#
# Dropped from final, with one-line proof each:
# - packages/browser-relay, collab-web, metaharness, typescript-edit-benchmark:
#   absent from every kept package's `dependencies` (coding-agent lists only
#   agent-core, ai, catalog, mnemopi, natives, tui, utils, wire, omptype,
#   snapcompact, omp-stats + otel/babel/puppeteer-core); `browser-relay`
#   appears in coding-agent/src only as the external `omp browser-relay` CLI
#   string, never as a module import.
# - python/: Bun-only runtime, no interpreter in this base image, so nothing
#   could execute it even if copied. Kept in the install stage: the
#   python/robomp/web workspace must exist for `bun install` to resolve.
# - patches/: consumed by bun at install time; the installed output is already
#   patched, nothing reads patches/ at runtime.
# - node_modules/sherpa-onnx-darwin-arm64: darwin-only binary pinned in root
#   `dependencies` for local dev; unloadable on this linux image.
# - node_modules/.bun/onnxruntime-node@{1.21.0,1.26.0} + onnxruntime-common
#   companions + fastembed: mnemopi DEV deps (production install excludes them;
#   the `|| bun install` fallback drags them in). Zero runtime imports in kept
#   sources (fastembed appears only as `import type`, erased at runtime).
#   transformers keeps its own onnxruntime-node@1.24.3 (untouched).
# - node_modules/.bun/{prettier,diff,gpt-tokenizer,@napi-rs+*}: dev-only, zero
#   kept-src imports (prettier is imported only by dropped
#   typescript-edit-benchmark).
# - node_modules/.bun/{framer-motion,motion,motion-dom,motion-utils,solid-js,
#   katex}: owned by dropped collab-web/metaharness/robomp-web; kept sources
#   mention them only in string lists / license txt, never as imports.
 # - dangling workspace links of the four dropped packages under
 #   node_modules/@oh-my-pi/ (nothing left to resolve them).
#
# Deliberately KEPT + why:
# - packages/{agent,ai,catalog,coding-agent,mnemopi,natives,omptype,
#   snapcompact,stats,tui,utils,wire}: SDK closure. omp-server/worker.ts +
#   omp-server/engine.ts import coding-agent/src/sdk.ts, which imports pi-agent-core,
#   pi-ai, pi-catalog, pi-tui, pi-utils, pi-wire and lazily imports
#   pi-mnemopi (memory.backend opt-in) and omp-stats (prod dep, lazy import in
#   modes/controllers/command-controller).
# - node_modules/@huggingface/transformers + onnxruntime-web (~360M) and
#   sherpa-onnx-node: FRONTIER, not cut. Optional deps wired into audio/tiny-ML
#   paths (coding-agent/src/utils/title-generator.ts, tiny/, commit/);
#   default elia runs (memory.backend off, no audio) never load them, but
#   pruning would break those opt-in paths — left for a follow-up with runtime
#   proof. Safe point stops here (~1.2GB needs these cuts).
# - mnemopi's fastembed/onnxruntime-node are DEV deps of packages/mnemopi, so
#   `bun install --production` already excludes them from the image.

FROM oven/bun:1-slim AS installer
WORKDIR /srv/omp-server

# workspace deps (SDK graph) — installed at build time
COPY omp-server/package.json omp-server/bun.lock* ./
COPY omp-server/packages ./packages
COPY omp-server/python ./python
COPY omp-server/patches ./patches
RUN bun install --production 2>/dev/null || bun install

# Prune dead weight HERE (install stage) so the final-stage COPY layers stay
# small — deleting after COPY would leave the bytes in the earlier layer.
# Each entry has import-level proof in the header above; the two rules are:
# (a) owning workspace dropped from final, or (b) dev-only dep with zero
# runtime imports in kept sources (verified by grep over packages/*/src).
RUN rm -rf \
  node_modules/sherpa-onnx-darwin-arm64 \
  node_modules/@oh-my-pi/browser-relay \
  node_modules/@oh-my-pi/collab-web \
  node_modules/@oh-my-pi/pi-metaharness \
  node_modules/@oh-my-pi/typescript-edit-benchmark \
  packages/browser-relay \
  packages/collab-web \
  packages/metaharness \
  packages/typescript-edit-benchmark \
  packages/*/test \
  packages/*/bench \
  packages/*/examples \
  node_modules/.bun/onnxruntime-node@1.21.0 \
  node_modules/.bun/onnxruntime-node@1.26.0 \
  node_modules/.bun/onnxruntime-common@1.21.0 \
  node_modules/.bun/onnxruntime-common@1.26.0 \
  node_modules/.bun/fastembed@2.1.0 \
  node_modules/.bun/prettier@3.9.6 \
  node_modules/.bun/framer-motion@* \
  node_modules/.bun/motion@* \
  node_modules/.bun/motion-dom@* \
  node_modules/.bun/motion-utils@* \
  node_modules/.bun/solid-js@* \
  node_modules/.bun/katex@* \
  node_modules/.bun/diff@* \
  node_modules/.bun/gpt-tokenizer@* \
  node_modules/.bun/@napi-rs+*@*

FROM oven/bun:1-slim AS base
WORKDIR /srv/omp-server

COPY omp-server/package.json omp-server/bun.lock* ./
COPY --from=installer /srv/omp-server/node_modules ./node_modules
COPY --from=installer /srv/omp-server/packages ./packages

# prebuilt natives for linux arm64/x64 are baked at pack time via:
#   bun --cwd=omp-server scripts/bazel-natives.ts host --dest packages/natives/native
# (darwin .node files are never copied into the image)

COPY omp-server/*.ts ./
COPY omp-server/routes ./routes
COPY omp-server/config ./config
COPY omp-server/extensions ./extensions
COPY omp-server/tunnelWatch.sh ./tunnelWatch.sh

# MCP parity with live: ffmpeg (media pipelines) + nodejs/npm/npx (MCP server
# hosting). mcp-cli is BAKED here from source (no linux/arm64 release asset
# exists — only linux-x64 — so bun builds it; the host ~/.local/bin/mcp-cli
# is a macOS Mach-O and must never be bind-mounted, see compose). Config
# mcp_servers.json arrives as read-only host mount — never baked, no secrets.
RUN bun install -g https://github.com/philschmid/mcp-cli \
  && mcp-cli --version
# Node comes from the official tarball, NOT Debian's npm package (which drags
# ~500MB of webpack/babel/jest into the layer). npm/npx ride along inside.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl xz-utils \
  && rm -rf /var/lib/apt/lists/* \
  && ARCH=$(uname -m | sed -e 's/x86_64/x64/' -e 's/aarch64/arm64/') \
  && curl -fsSL "https://nodejs.org/dist/v22.17.0/node-v22.17.0-linux-${ARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1 \
  && node --version && npm --version && npx --version

# uv + python3 + the shared libraries a headless Chromium needs, plus xvfb for a
# headed `--login` browser. uv installs to /root/.local/bin and joins PATH for MCP
# stdio servers.
RUN apt-get update && apt-get install -y --no-install-recommends python3 xvfb \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libcairo2 libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh \
    && /root/.local/bin/uv --version
ENV PATH="/root/.local/bin:${PATH}"

# Python deps for bind-mounted FastMCP servers. These MUST live in the image: the
# MCP source dir is mounted :ro and /root/.local is NOT a volume, so a runtime
# `uv pip install` is wiped by every container recreate and every stdio server then
# dies with ModuleNotFoundError on startup. Add your own server's deps here.
RUN uv pip install --python /usr/bin/python3 --break-system-packages \
  "fastmcp>=2.0" "python-dotenv>=1.0" "requests" \
  && python3 -c "import fastmcp, dotenv, requests"

# ── OPTIONAL: browser automation ────────────────────────────────────────────
# Uncomment if your agents drive a real browser. Keep the browser at a
# CONTAINER-LOCAL path on purpose: a host-mounted profile usually holds a
# different platform build (e.g. chrome-mac-arm64), which the linux runtime
# rejects with "Chromium browser is missing". Its PLAYWRIGHT_BROWSERS_PATH must
# then point at THIS path, not at the host's.
# ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw
# RUN mkdir -p /opt/pw \
#   && PLAYWRIGHT_BROWSERS_PATH=/opt/pw uvx patchright install chromium --with-deps \
#   && test -d /opt/pw/chromium-1243
#
# ── OPTIONAL: Google Workspace / OAuth MCP ─────────────────────────────────
# Any MCP whose interpreter deps live in a bind-mounted dir needs those deps baked
# here, or every import dies on ModuleNotFoundError at run time.
# RUN uv pip install --python /usr/bin/python3 --break-system-packages \
#   "google-auth" "google-auth-oauthlib" "google-api-python-client"
# ENV PATH="/srv/tools:${PATH}"

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD bun -e "fetch('http://localhost:5677/health').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"

EXPOSE 5677
CMD ["bun", "server.ts"]
