#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-/data/logs}"
mkdir -p "$LOG_DIR"

echo "[entrypoint] clearing stale opencode models cache"
rm -f /root/.cache/opencode/models.json
rm -f /root/.cache/opencode/models.json.bak 2>/dev/null || true

echo "[entrypoint] starting opencode serve on 127.0.0.1:5655"
opencode serve --port 5655 --hostname 127.0.0.1 > "$LOG_DIR/opencode-serve.log" 2>&1 &
OPENCODE_PID=$!
echo "$OPENCODE_PID" > /tmp/opencode.pid
echo "[entrypoint] opencode pid=$OPENCODE_PID"

echo "[entrypoint] waiting for opencode to become healthy"
for i in $(seq 1 30); do
  echo "[entrypoint] health check attempt $i"
  if curl -sf http://127.0.0.1:5655/global/health >/dev/null 2>&1; then
    echo "[entrypoint] opencode healthy after ${i}s"
    break
  fi
  echo "[entrypoint] not healthy yet (curl exit $?)"
  if ! kill -0 "$OPENCODE_PID" 2>/dev/null; then
    echo "[entrypoint] opencode process died — log tail:"
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

echo "[entrypoint] starting FastAPI on 0.0.0.0:5656"
exec uvicorn app.main:app --host 0.0.0.0 --port 5656
