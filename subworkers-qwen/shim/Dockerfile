FROM python:3.12-slim

LABEL maintainer="EliaAI"
LABEL description="EliaAI Subworker Qwen Shim — Elia routes over Qwen serve protocol"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Africa/Casablanca

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates tzdata procps gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /root/EliaAI/setup && \
    printf '#!/bin/sh\n# Container stub: rotation lives in the qwen forward-proxy,\n# not in host switch scripts. Always succeeds so host plugins never crash runs.\nexit 0\n' > /root/EliaAI/setup/switch-proxy.sh && \
    chmod +x /root/EliaAI/setup/switch-proxy.sh && \
    node --version && npm --version

# Engine swap 2026-09-19: opencode binary via the official installer, linked
# onto PATH; the trailing --version both proves the install and lands in the
# build log. Qwen daemon stays as a dormant sidecar (compose untouched).
RUN curl -fsSL https://opencode.ai/install | bash && \
    ln -sf /root/.opencode/bin/opencode /usr/local/bin/opencode && \
    opencode --version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# zen-free provider (proxy-local gateway; key public by design) for
# `opencode run -m zen-free/<model>` turns. Default config path, no env needed.
COPY opencode.json /root/.config/opencode/opencode.json

EXPOSE 5676

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -sf http://localhost:5676/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5676"]
