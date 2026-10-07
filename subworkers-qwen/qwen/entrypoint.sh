#!/usr/bin/env bash
# qwen container entrypoint: container-local LRU forward proxy (:3128, same
# system as live Elia) + qwen serve. Mirrors the live entrypoint pattern.
set -euo pipefail
IFS=$'\n\t'

TAG="[qwen-entrypoint]"

echo "$TAG starting forward proxy 127.0.0.1:3128 + attest 127.0.0.1:3129"
# OpenCode-client attestation: OPENCODE_SESSION (qwen/.env, host install-id,
# never expires) → ATTEST_SESSION for forward-proxy.js. Empty → the proxy
# logs a warning and mints an ephemeral UUID (gateway accepts any UUID).
export ATTEST_SESSION="${OPENCODE_SESSION:-}"
export ATTEST_UA="${ATTEST_UA:-omp/18.2.6}"
export ATTEST_UPSTREAM_HOST="${ATTEST_UPSTREAM_HOST:-host.docker.internal}"
export ATTEST_UPSTREAM_PORT="${ATTEST_UPSTREAM_PORT:-18898}"
node /srv/forward-proxy.js &
PROXY_PID=$!
echo "$PROXY_PID" > /tmp/forward-proxy.pid
sleep 1
if ! kill -0 "$PROXY_PID" 2>/dev/null; then
  echo "$TAG forward proxy died on boot — aborting" >&2
  exit 1
fi

export HTTP_PROXY="http://127.0.0.1:3128"
export HTTPS_PROXY="http://127.0.0.1:3128"
export http_proxy="http://127.0.0.1:3128"
export https_proxy="http://127.0.0.1:3128"
# Gateway (host.docker.internal:18898) + daemon/shim loopback stay direct:
# a public residential proxy could never dial them.
export NO_PROXY="localhost,127.0.0.1,::1,host.docker.internal,qwen,shim"
export no_proxy="localhost,127.0.0.1,::1,host.docker.internal,qwen,shim"
echo "$TAG HTTP_PROXY=$HTTP_PROXY NO_PROXY=$NO_PROXY"

trap 'echo "$TAG stopping"; kill "$QWEN_PID" "$PROXY_PID" 2>/dev/null || true' TERM INT

echo "$TAG starting qwen serve on 0.0.0.0:4170 (via proxy)"
qwen serve --no-web --hostname 0.0.0.0 --port 4170 --workspace /srv/case &
QWEN_PID=$!
echo "$QWEN_PID" > /tmp/qwen.pid
wait "$QWEN_PID"
