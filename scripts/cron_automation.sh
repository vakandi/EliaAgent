#!/bin/zsh
AGENT_DIR="$(cd "$(dirname "$0")" && pwd)"
/usr/bin/osascript -e "do shell script \"cd ${AGENT_DIR} && /bin/zsh ${AGENT_DIR}/scripts/cron_wrapper.sh\""