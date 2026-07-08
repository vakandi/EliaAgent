#!/bin/bash
# Bene2Luxe - Quick Video Generation Commands
# =========================================
# Quick reference for common generation commands

# === SETUP ===
# 1. Set credentials
export HF_CREDENTIALS="YOUR_KEY_ID:YOUR_KEY_SECRET"

# 2. Install dependencies (if needed)
pip3 install higgsfield-client requests pillow --break-system-packages

# === SINGLE VIDEO GENERATION ===
SCRIPT="python3 /Users/vakandi/EliaAI/docs/2026-03-26/higgfields-scripts/higgfields_master.py"

# From text prompt
$SCRIPT video --prompt "Luxury Chanel sneakers rotating on white background" --model kling-3 --duration 10

# From image
$SCRIPT video --image product.png --model kling-3 --duration 10

# === BATCH GENERATION ===
# From prompts file
$SCRIPT batch --type product --count 50 --model kling-3 --output-dir ./generated

# From specific category
$SCRIPT batch --type lifestyle --count 25 --model wan-2 --output-dir ./generated

# === MASCOOT EPISODES ===
# Single episode
$SCRIPT mascott --episode 1

# Episode range (requires loop)
for i in {1..25}; do
    $SCRIPT mascott --episode $i
done

# === IMAGE GENERATION ===
$SCRIPT image --prompt "Chanel sneakers on marble" --model nano-banano --aspect 9:16

# === MODELS REFERENCE ===

# IMAGE MODELS
# nano-banano     - Fast 4K (1 credit)
# flux-pro       - Best quality (2 credits)
# flux-dev       - Free tier

# VIDEO MODELS
# kling-3        - Primary (15s, 3 credits) ★ RECOMMENDED
# kling-standard - Faster (10s, 2 credits)
# wan-2          - Free tier
# minimax        - Free tier (5s)

# === EXAMPLE WORKFLOWS ===

# Workflow 1: Product Showcase (5 videos)
for product in "Chanel sneakers" "Dior sunglasses" "LV bag" "Gucci belt" "Premium cap"; do
    $SCRIPT video --prompt "Luxury $product rotating slowly, studio lighting" --model kling-3
    sleep 5
done

# Workflow 2: Mascoot Episode (1 episode = ~15s video)
$SCRIPT mascott --episode 1 --model kling-3

# Workflow 3: Free Tier Testing
$SCRIPT video --prompt "Fashion content lifestyle" --model wan-2 --duration 5

# Workflow 4: Image then Video
IMAGE=$($SCRIPT image --prompt "Product photo" --model nano-banano)
$SCRIPT video --image "$IMAGE" --model kling-3

# === CREDITS CHECK ===
# Run before batch to estimate cost

ESTIMATE=50  # videos
CREDITS_PER_VIDEO=3  # kling-3

echo "Estimated credits needed: $((ESTIMATE * CREDITS_PER_VIDEO))"

# === OUTPUT ===
# Videos saved to: ./generated/
# Images saved to: ./generated/
# Logs: Check terminal output

# === HELP ===
$SCRIPT --help
