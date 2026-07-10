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
parse_last() { 
    echo "$1" | grep '|' | sed 's/.*|last:\([^|]*\).*/\1/' | tr -d ' ' | sed 's/^\(....-..-..\)\(.*\)/\1 \2/'
}

time_ago() {
    local ts="$1"
    [ -z "$ts" ] && echo "never"
    le=$(date -j -f "%Y-%m-%d %H:%M:%S" "$ts" +%s 2>/dev/null)
    [ -z "$le" ] && echo "unknown"
    diff=$(($(date +%s) - le))
    [ $diff -lt 60 ] && echo "${diff}s ago"
    [ $diff -lt 3600 ] && echo "$((diff/60))m ago"
    [ $diff -lt 86400 ] && echo "$((diff/3600))h ago"
    echo "$((diff/86400))d ago"
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
        idx=$((i+1)); p=$(parse_proxy "${proxies[$i]}")
        last=$(parse_last "${proxies[$i]}")
        ago=$(time_ago "$last")
        echo "  [$idx] $p  🕐 $ago"
    done
    echo ""; echo -n "Select [1-${#proxies[@]}]: "; read sel
    [ "$sel" = "q" ] && exit 0
    [[ ! "$sel" =~ ^[0-9]+$ ]] || [ "$sel" -lt 1 ] || [ "$sel" -gt ${#proxies[@]} ] && echo "❌ Invalid" && exit 1
    idx=$((sel-1))
else
    oldest_idx=0
    oldest_ts=99999999999
    never_used_idx=-1
    
    for i in "${!proxies[@]}"; do
        last=$(parse_last "${proxies[$i]}")
        
        if [ -z "$last" ]; then
            never_used_idx=$i
            break
        fi
        
        ts=$(date -j -f "%Y-%m-%d %H:%M:%S" "$last" +%s 2>/dev/null)
        if [ -n "$ts" ] && [ "$ts" -lt "$oldest_ts" ]; then
            oldest_ts=$ts
            oldest_idx=$i
        fi
    done
    
    if [ $never_used_idx -ge 0 ]; then
        idx=$never_used_idx
    else
        idx=$oldest_idx
    fi
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

proxies[$idx]="$ip:$port:$user:$pass |last:$now |dur:0h 0m"
{ for p in "${proxies[@]}"; do echo "$p"; done; } > "$PROXY_FILE"
echo "$idx|$now" > "$CURRENT_FILE"

# Proxy is now handled by proxychains4 at library level (LD_PRELOAD)
# No need to export HTTPS_PROXY/HTTP_PROXY - proxychains4 uses ~/.proxychains.conf
# This prevents terminal pollution (git push, curl, etc. work without unset)

echo ""
echo "✅ $ip:$port"
echo "📅 Last used: $(time_ago "$now")"
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