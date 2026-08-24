FROM python:3.12-slim AS base

LABEL maintainer="EliaAI"
LABEL description="EliaAI Subworker Management Server"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

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
    && rm -rf /var/lib/apt/lists/*

# Install Node.js + npm + npx for MCP servers and parallel-browser-mcp
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:5656/health || exit 1

EXPOSE 5656

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5656"]
