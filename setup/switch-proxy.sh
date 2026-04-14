#!/bin/bash
PROXY_FILE="$HOME/EliaAI/setup/proxies.txt"
CONFIG_FILE="$HOME/.proxychains.conf"
CURRENT_FILE="$HOME/.proxychains.current"

AUTO_MODE=true
[ "$1" = "--manual" ] && AUTO_MODE=false

proxies=()
while IFS= read -r line; do
    [ -n "$line" ] && proxies+=("$line")
done < "$PROXY_FILE"

[ ${#proxies[@]} -eq 0 ] && echo "❌ No proxies" && exit 1

parse_proxy() { echo "$1" | cut -d'|' -f1 | sed 's/[[:space:]]*$//'; }
parse_last() { echo "$1" | grep '|' | sed 's/.*|last:\([^|]*\).*/\1/' | tr -d ' '; }
get_hours() {
    if [ -z "$1" ]; then echo "999"; else
        le=$(date -j -f "%Y-%m-%d %H:%M:%S" "$1" +%s 2>/dev/null)
        [ -z "$le" ] && echo "999" || echo "scale=1; ($(date +%s) - $le) / 3600" | bc
    fi
}

check_proxy() {
    local ip=$1 port=$2 user=$3 pass=$4
    wget -q -O - --no-check-certificate -e "https_proxy=http://$user:$pass@$ip:$port" https://api.ipify.org --timeout=5 2>/dev/null
}

echo "🔄 Proxy Switcher"
echo "================="

if [ "$AUTO_MODE" = "false" ]; then
    echo ""
    echo "Manual mode:"
    for i in "${!proxies[@]}"; do
        idx=$((i+1)); p=$(parse_proxy "${proxies[$i]}"); IFS=':' read -r ip port _ _ <<< "$p"
        last=$(parse_last "${proxies[$i]}"); h=$(get_hours "$last")
        [ -z "$last" ] && echo "  [$idx] $ip:$port  ❌" || echo "  [$idx] $ip:$port  🕐 ${h}h"
    done
    echo ""; echo -n "Select [1-${#proxies[@]}]: "; read sel
    [ "$sel" = "q" ] && exit 0
    [[ ! "$sel" =~ ^[0-9]+$ ]] || [ "$sel" -lt 1 ] || [ "$sel" -gt ${#proxies[@]} ] && echo "❌ Invalid" && exit 1
    idx=$((sel-1))
else
    echo "🤖 Auto mode..."
    idx=0; max_h=0
    for i in "${!proxies[@]}"; do
        h=$(get_hours "$(parse_last "${proxies[$i]}")")
        (( $(echo "$h > $max_h" | bc -l) )) && max_h=$h && idx=$i
    done
fi

p=$(parse_proxy "${proxies[$idx]}"); IFS=':' read -r ip port user pass <<< "$p"
now=$(date "+%Y-%m-%d %H:%M:%S")


echo "🔍 Testing $ip:$port..."
result=$(check_proxy "$ip" "$port" "$user" "$pass")

if [ -z "$result" ]; then
    echo "⚠️ Dead, trying next..."
    tried=1
    while [ -z "$result" ] && [ $tried -lt ${#proxies[@]} ]; do
        idx=$(( (idx + 1) % ${#proxies[@]} ))
        p=$(parse_proxy "${proxies[$idx]}"); IFS=':' read -r ip port user pass <<< "$p"
        echo "🔍 Testing $ip:$port..."
        result=$(check_proxy "$ip" "$port" "$user" "$pass")
        tried=$((tried + 1))
    done
fi

[ -z "$result" ] && echo "❌ All proxies dead" && exit 1


if [ -f "$CURRENT_FILE" ]; then
    prev=$(cat "$CURRENT_FILE")
    prev_idx=$(echo "$prev" | cut -d'|' -f1)
    prev_ts=$(echo "$prev" | cut -d'|' -f2)
    if [ -n "$prev_ts" ] && [ "$prev_ts" != "start" ]; then
        pe=$(date -j -f "%Y-%m-%d %H:%M:%S" "$prev_ts" +%s 2>/dev/null)
        [ -n "$pe" ] && {
            diff=$(( $(date +%s) - pe )); h=$((diff / 3600)); m=$(((diff % 3600) / 60))
            proxies[$prev_idx]="$(parse_proxy "${proxies[$prev_idx]}") |last:$prev_ts |dur:${h}h ${m}m"
        }
    fi
fi

proxies[$idx]="$(parse_proxy "${proxies[$idx]}") |last:$now |dur:0h 0m"
{ for p in "${proxies[@]}"; do echo "$p"; done; } > "$PROXY_FILE"
echo "$idx|$now" > "$CURRENT_FILE"

echo ""
echo "✅ $ip:$port"
echo "🌐 Your IP: $result"

cat > "$CONFIG_FILE" << EOF
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
http $ip $port $user $pass
EOF

echo "✅ Config written"
echo "Run: proxychains4 -f $CONFIG_FILE <cmd>"
