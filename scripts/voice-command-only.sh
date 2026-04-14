#!/bin/bash
set -uo pipefail

USER_MAC="$(whoami)"
export HOME="/Users/${USER_MAC}"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

export PATH="$HOME/.opencode/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

command -v rec >/dev/null 2>&1 || { echo "❌ 'rec' command not found (sox)"; exit 1; }
command -v sox >/dev/null 2>&1 || { echo "❌ sox not installed"; exit 1; }

AGENT_DIR="/Users/vakandi/EliaAI"
TRANSCRIPT_FILE="/tmp/transcript.txt"
echo -n "" > "$TRANSCRIPT_FILE"

echo "🎙️  Enregistrement vocal..."
echo "Appuyez sur ENTRÉE pour arrêter"
echo "----------------------------------------"

rec -r 16000 -c 1 -e signed -b 16 /tmp/dictation.wav &
REC_PID=$!
read -r
kill $REC_PID 2>/dev/null || true
wait $REC_PID 2>/dev/null || true

echo ""
echo "⏳ Transcription..."

TRANSCRIPT=$(/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -c "
import whisper
model = whisper.load_model('medium')
result = model.transcribe('/tmp/dictation.wav', language='fr', task='transcribe')
print(result['text'].strip())
")

echo "$TRANSCRIPT" > "$TRANSCRIPT_FILE"
echo "📝: $TRANSCRIPT"
echo "$TRANSCRIPT" | pbcopy

WORD_COUNT=$(echo "$TRANSCRIPT" | wc -w | tr -d ' ')
if [[ "$WORD_COUNT" -gt 1 ]]; then
    echo "✅ Exécution: $TRANSCRIPT"
    
    PROXY_FLAG=""
    if [[ -f "${AGENT_DIR}/.proxy_enabled" ]]; then
        PROXY_FLAG="--proxy"
    fi
    
    cd "$AGENT_DIR"
    /Users/vakandi/EliaAI/scripts/voice-command.sh --extra-prompt="$TRANSCRIPT" $PROXY_FLAG
else
    echo "⏭️  Trop court ($WORD_COUNT mots)"
fi

echo ""
read -p "Appuyez sur ENTRÉE pour fermer..."