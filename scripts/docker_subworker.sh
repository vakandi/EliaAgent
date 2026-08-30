#!/usr/bin/env bash
set -euo pipefail

cd ~/EliaAI/subworkers/server

echo "[Docker] Waiting for Docker daemon..."
for i in $(seq 1 15); do
    docker info >/dev/null 2>&1 && break
    echo "[Docker] Attempt $i/15..."
    sleep 2
done

if ! docker info >/dev/null 2>&1; then
    echo "[Docker] FATAL: Docker daemon not reachable after 30s"
    exit 1
fi

if ! docker-compose images -q 2>/dev/null | grep -q .; then
    echo "[Docker] Image not found — building..."
    docker-compose build
fi

docker-compose up -d

# ── Warm sessions DB (prevent 1-session-0-msg cold start) ────────────────
echo "[Docker] Warming sessions DB..."
for i in $(seq 1 10); do
  curl -sf --max-time 3 http://localhost:5656/health >/dev/null 2>&1 && break
  sleep 2
done
TOKEN_WARM=$(grep ELIA_AUTH_TOKEN ~/EliaAI/subworkers/server/.env 2>/dev/null | cut -d= -f2)
if [ -n "$TOKEN_WARM" ]; then
  echo "[Docker] Warming sessions list..."
  curl -s --max-time 15 "http://localhost:5656/sessions/example-agent/list" -H "Authorization: Bearer $TOKEN_WARM" >/dev/null 2>&1 || true
  curl -s --max-time 15 http://127.0.0.1:5655/session?limit=200 >/dev/null 2>&1 || true
  echo "[Docker] Warm done"
fi

# ── Cloudflare tunnel persistence ────────────────────────────────────────
# If a tunnel was configured (tunnel.json exists), make sure the connector
# comes back too. The server also self-heals it on boot; this is belt-and-braces.
TUNNEL_STATE="$HOME/EliaAI/subworkers/server/app/config/tunnel.json"
if [[ -f "$TUNNEL_STATE" ]]; then
    echo "[Docker] Cloudflare tunnel config detected — ensuring cloudflared..."
    for i in $(seq 1 20); do
        curl -sf --max-time 2 http://localhost:5656/health >/dev/null 2>&1 && break
        sleep 2
    done
    if docker ps --format '{{.Names}}' | grep -q '^elia-cloudflared$'; then
        echo "[Docker] cloudflared already running"
    elif docker start elia-cloudflared >/dev/null 2>&1; then
        echo "[Docker] cloudflared restarted (existing container)"
    else
        echo "[Docker] cloudflared not present — server autostart will recreate it"
    fi
fi

echo "[Docker] Container started. Tailing logs..."
docker logs -f elia-subworker-srv
