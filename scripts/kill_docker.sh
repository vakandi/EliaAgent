#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# kill_docker.sh — Force-kill all Docker containers, then stop Colima.
# Frees RAM but keeps images on disk.

echo "[kill_docker] Force-killing all running containers..."
docker kill $(docker ps -q) 2>/dev/null || true

echo "[kill_docker] Removing all stopped containers..."
docker rm -f $(docker ps -aq) 2>/dev/null || true

echo "[kill_docker] Stopping docker-compose services..."
docker-compose -f ~/EliaAI/subworkers/server/docker-compose.yml down --remove-orphans 2>/dev/null || true

echo "[kill_docker] Stopping Colima VM..."
colima stop 2>/dev/null || true

echo "[kill_docker] Done. All containers killed and removed. Images kept on disk."
