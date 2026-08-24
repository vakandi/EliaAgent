#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# nuke_docker.sh — Kill everything, delete all images, volumes, build cache.
# Frees CPU, RAM, and disk. Next EliaUI launch rebuilds from scratch.

echo "[nuke_docker] Force-killing all running containers..."
docker kill $(docker ps -q) 2>/dev/null || true

echo "[nuke_docker] Removing all containers..."
docker rm -f $(docker ps -aq) 2>/dev/null || true

echo "[nuke_docker] Stopping docker-compose services..."
docker-compose -f ~/EliaAI/subworkers/server/docker-compose.yml down --rmi all --remove-orphans 2>/dev/null || true

echo "[nuke_docker] Removing ALL images..."
docker image prune -af 2>/dev/null || true
docker rmi $(docker images -q) 2>/dev/null || true

echo "[nuke_docker] Removing all volumes..."
docker volume prune -f 2>/dev/null || true

echo "[nuke_docker] Removing build cache..."
docker builder prune -af 2>/dev/null || true

echo "[nuke_docker] Stopping Colima VM..."
colima stop 2>/dev/null || true

echo "[nuke_docker] Done. Everything nuked. Next EliaUI launch rebuilds from scratch."
