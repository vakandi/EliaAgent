FROM python:3.12-slim AS base

LABEL maintainer="EliaAI"
LABEL description="EliaAI Subworker Management Server"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Africa/Casablanca

WORKDIR /app

# Install system packages:
# - curl, ca-certificates: HTTP client, TLS
# - git: repo operations, version control
# - ffmpeg: video/audio processing (video-analyzer MCP, whisper)
# - ffmpeg deps: libsm6, libxext6, libxrender for opencv
# - build-essential + libffi-dev: Python C extensions (cryptography, etc.)
# - sqlite3: database operations
# - jq: JSON processing in shell scripts
# - tzdata: timezone support
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
        ffmpeg \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgl1 \
        build-essential \
        libffi-dev \
        sqlite3 \
        jq \
        tzdata \
        procps \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js + npm + npx for MCP servers and parallel-browser-mcp
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install opencode from latest GitHub release (pinned, not main) — https://github.com/anomalyco/opencode/releases
RUN latest_tag=$(curl -s https://api.github.com/repos/anomalyco/opencode/releases/latest | jq -r .tag_name) && \
    echo "Using opencode $latest_tag from https://github.com/anomalyco/opencode/releases" && \
    arch=$(dpkg --print-architecture) && \
    if [ "$arch" = "arm64" ]; then asset="opencode-linux-arm64.tar.gz"; else asset="opencode-linux-x64.tar.gz"; fi && \
    curl -fsSL -o /tmp/opencode.tar.gz "https://github.com/anomalyco/opencode/releases/download/${latest_tag}/${asset}" && \
    tar -xzf /tmp/opencode.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/opencode && \
    opencode --version

# Docker CLI + compose plugin — lets the app manage the cloudflared container
# on the HOST daemon (via the mounted /var/run/docker.sock).
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" \
    > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5656 5655

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -sf http://localhost:5656/health && curl -sf http://localhost:5655/global/health || exit 1

CMD ["/app/entrypoint.sh"]
