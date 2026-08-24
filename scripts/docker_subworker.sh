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
echo "[Docker] Container started. Tailing logs..."
docker logs -f elia-subworker-srv
