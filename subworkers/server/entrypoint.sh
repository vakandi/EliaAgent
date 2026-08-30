#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-/data/logs}"
mkdir -p "$LOG_DIR"

echo "[entrypoint] clearing stale opencode models cache"
rm -f /root/.cache/opencode/models.json
rm -f /root/.cache/opencode/models.json.bak 2>/dev/null || true

echo "[entrypoint] starting forward proxy 127.0.0.1:3128"
node /app/app/forward-proxy.js > "$LOG_DIR/forward-proxy.log" 2>&1 &
echo $! > /tmp/forward-proxy.pid
sleep 1
cat "$LOG_DIR/forward-proxy.log" 2>/dev/null | tail -3 || true

export HTTP_PROXY="http://127.0.0.1:3128"
export HTTPS_PROXY="http://127.0.0.1:3128"
export http_proxy="http://127.0.0.1:3128"
export https_proxy="http://127.0.0.1:3128"
export NO_PROXY="localhost,127.0.0.1,::1"
export no_proxy="localhost,127.0.0.1,::1"
echo "[entrypoint] HTTP_PROXY=$HTTP_PROXY"

# ── opencode serve with auto-restart ──────────────────────────────────────
# Runs in a supervisor loop so a crash / OOM-kill is recovered without a
# container restart. The shell stays alive (uvicorn runs in background +
# `wait`) so it reaps the supervisor — no zombies. tini (PID 1) reaps the
# shell itself and forwards signals to the whole process group (-g).
echo "[entrypoint] starting opencode serve on 127.0.0.1:5655 (binary via proxy)"
(
  while true; do
    opencode serve --port 5655 --hostname 127.0.0.1 >> "$LOG_DIR/opencode-serve.log" 2>&1 || true
    echo "[entrypoint] opencode exited — restarting in 2s"
    sleep 2
  done
) &
OPENCODE_PID=$!
echo "$OPENCODE_PID" > /tmp/opencode.pid
echo "[entrypoint] opencode supervisor pid=$OPENCODE_PID"

# Forward SIGTERM/SIGINT to the supervisor so `docker stop` shuts opencode
# down cleanly (tini -g also forwards to the process group as a backstop).
trap 'echo "[entrypoint] stopping opencode supervisor"; kill "$OPENCODE_PID" 2>/dev/null || true' TERM INT

echo "[entrypoint] waiting for opencode to become healthy"
set +e
for i in $(seq 1 30); do
  echo "[entrypoint] health check attempt $i"
  if curl --max-time 2 -sf http://127.0.0.1:5655/global/health >/dev/null 2>&1; then
    echo "[entrypoint] opencode healthy after ${i}s"
    break
  fi
  echo "[entrypoint] not healthy yet (curl exit $?)"
  if ! kill -0 "$OPENCODE_PID" 2>/dev/null; then
    echo "[entrypoint] opencode supervisor died — log tail:"
    cat "$LOG_DIR/opencode-serve.log" || true
    exit 1
  fi
  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "[entrypoint] opencode failed to become healthy in 30s"
    cat "$LOG_DIR/opencode-serve.log" || true
    exit 1
  fi
done
set -e

echo "[entrypoint] starting FastAPI on 0.0.0.0:5656"
# Run uvicorn in the background and `wait` on it instead of `exec`: the shell
# must stay alive to reap the opencode supervisor / forward-proxy children
# (bash reaps its own children on SIGCHLD — no zombies). tini reaps the shell.
uvicorn app.main:app --host 0.0.0.0 --port 5656 &
UVICORN_PID=$!
echo "[entrypoint] uvicorn pid=$UVICORN_PID"
wait "$UVICORN_PID"
