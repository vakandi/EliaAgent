#!/bin/bash
set -e

PYTHON=/opt/homebrew/bin/python3.11
VENV="$HOME/.venvs/tts"

echo "→ Creating venv with $PYTHON..."
$PYTHON -m venv "$VENV"

echo "→ Activating venv..."
source "$VENV/bin/activate"

echo "→ Upgrading pip..."
pip install --upgrade pip --quiet

echo "→ Installing dependencies..."
# KEY FIX: Use phonemizer-fork instead of phonemizer
# phonemizer >= 3.4 removed set_data_path() which misaki needs
pip install espeakng_loader misaki num2words spacy phonemizer-fork --quiet

echo "→ Installing mlx-audio..."
pip install mlx-audio --quiet

echo "→ Done. Adding 'speak' alias to ~/.zshrc..."

ALIAS_LINE="alias speak='source $VENV/bin/activate && python -m mlx_audio.tts.generate --model mlx-community/Kokoro-82M-bf16 --voice ff_siwis --lang_code f --play --text'"

if grep -q "alias speak=" ~/.zshrc 2>/dev/null; then
  echo "  (alias already exists, skipping)"
else
  echo "" >> ~/.zshrc
  echo "# mlx-audio TTS French voice" >> ~/.zshrc
  echo "$ALIAS_LINE" >> ~/.zshrc
  echo "  alias added to ~/.zshrc"
fi

echo ""
echo "→ Testing voice..."
python -m mlx_audio.tts.generate \
  --model mlx-community/Kokoro-82M-bf16 \
  --text "Installation réussie. Je suis prêt." \
  --voice ff_siwis \
  --lang_code f \
  --play

echo ""
echo "✓ All done. Reload your shell then use: speak \"votre texte ici\""
echo "  Or run now: source ~/.zshrc"





