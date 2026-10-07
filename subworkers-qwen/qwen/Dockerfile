# Mirror of ~/omp-migration/qwen-case-study/Dockerfile (qwen-code 0.24.1),
# extended with tzdata + curl for TZ=Africa/Casablanca and HEALTHCHECK.
# Workspace root /srv/case; per-agent isolation via session workspaceCwd
# (/srv/case/<name>), bind-mounted in docker-compose.yml.
FROM node:22-slim

RUN npm install -g @qwen-code/qwen-code@0.24.1 && qwen --version

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

ENV TZ=Africa/Casablanca

WORKDIR /srv
EXPOSE 4170

# Container-local LRU forward proxy (same residential-rotation system as
# live Elia): pool mounted at /data/proxies.txt; the :3129 attest listener
# chains stamped inference through :3128 pool egress (forced). Daemon→:3129
# loopback stays direct (NO_PROXY).
COPY forward-proxy.js /srv/forward-proxy.js
COPY entrypoint.sh /srv/entrypoint.sh
# Elia admitted-turn survival patch (source: /tmp/qwen-code 0.24.1,
# packages/core/src/core/openaiContentGenerator/pipeline.ts — retryWithBackoff
# ladder 5 attempts ~3min on streaming turns; chunk mirror kept here because
# the image installs the prebuilt npm bundle, not the source tree). Pinned to
# chunk-JSKHW2K5.js = @qwen-code/qwen-code@0.24.1; bump the version = re-extract
# + re-apply. The grep fails the build if the marker ever goes missing.
COPY chunk-patches/chunk-JSKHW2K5.js /tmp/chunk-JSKHW2K5.js.patched
RUN chmod +x /srv/entrypoint.sh && node --check /srv/forward-proxy.js && bash -n /srv/entrypoint.sh \
    && cp /tmp/chunk-JSKHW2K5.js.patched "$(npm root -g)/@qwen-code/qwen-code/chunks/chunk-JSKHW2K5.js" \
    && node --check "$(npm root -g)/@qwen-code/qwen-code/chunks/chunk-JSKHW2K5.js" \
    && grep -q "provider-retry" "$(npm root -g)/@qwen-code/qwen-code/chunks/chunk-JSKHW2K5.js"

# Qwen daemon auth + zen-free provider wiring come from qwen/.env (never
# baked in here): QWEN_SERVER_TOKEN, OPENAI_BASE_URL, OPENAI_API_KEY=public,
# OPENAI_MODEL. Placeholder default keeps `docker compose config` valid.
ENV QWEN_SERVER_TOKEN=qwen-dev-token-placeholder

ENTRYPOINT ["/srv/entrypoint.sh"]

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -sf http://localhost:4170/health || exit 1
