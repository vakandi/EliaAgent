#!/bin/bash

echo "Installing Elia TTS to /usr/local/bin..."

cat > /usr/local/bin/elia-speak << 'EOF'
#!/bin/bash
python3 /Users/vakandi/EliaAI/setup/speak.py "$@"
EOF

cat > /usr/local/bin/elia-voxtral-speak << 'EOF'
#!/bin/bash
python3 /Users/vakandi/Documents/mcps_server/dia_voice/mistral-speak.py "$@"
EOF

chmod +x /usr/local/bin/elia-speak /usr/local/bin/elia-voxtral-speak

echo "✅ Done! Run:"
echo "  sudo bash /Users/vakandi/EliaAI/tools/install_elia_tts.sh"