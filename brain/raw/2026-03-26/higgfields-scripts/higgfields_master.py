#!/usr/bin/env python3
"""
Bene2Luxe × Higgfields AI - Complete Generation Scripts
=======================================================

This module provides automated scripts for generating:
1. Product images (Nano Banano Pro / Flux Pro)
2. Product videos (Kling 3.0)
3. Lifestyle content (Free models)
4. Mascott adventures (Video generation)

USAGE:
  python3 higgfields_master.py --help
  python3 higgfields_master.py image --prompt "Chanel sneakers luxury" --model nano-banano
  python3 higgfields_master.py video --image product.png --model kling-3
  python3 higgfields_master.py batch --type product --count 50
  python3 higgfields_master.py mascott --episode 1

MODELS AVAILABLE:
  IMAGE:
    - nano-banano-pro (4K fast, 1 credit)
    - flux-pro-kontext (Best quality, 2 credits)
    - flux-dev (Free, limited)

  VIDEO:
    - kling-3.0-pro (15s, 3 credits) ← PRIMARY
    - kling-3.0-standard (10s, 2 credits)
    - wan-2.2 (10s, free tier)
    - minimax-video (5s, free tier)

CREDITS:
  ~600 Nano Banano Pro
  ~200 Kling 3.0
  Unlimited free models (Flux Dev, Wan, Minimax)

Author: Elia - Bene2Luxe Content System
Date: 26 Mars 2026
"""

import os
import sys
import json
import argparse
import requests
import time
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================


@dataclass
class Config:
    """Configuration for Higgfields generation."""

    # Credentials
    HF_CREDENTIALS: str = os.environ.get("HF_CREDENTIALS", "")

    # Paths
    BASE_DIR: Path = Path(__file__).parent
    OUTPUT_DIR: Path = Path(__file__).parent / "generated"
    PRODUCTS_DIR: Path = Path(
        "/Users/vakandi/ComfyUI/bene2luxe_products_data/generated"
    )
    MASCOOT_DIR: Path = Path(__file__).parent / "mascott-assets"

    # Models
    IMAGE_MODELS = {
        "nano-banano": "nano-banana-pro/text-to-image",
        "flux-pro": "flux-pro/kontext/max/text-to-image",
        "flux-dev": "flux-dev/text-to-image",
    }

    VIDEO_MODELS = {
        "kling-3": "kling-video/pro/video-generation",
        "kling-standard": "kling-video/standard/video-generation",
        "wan-2": "wan/wan-video/video-generation",
        "minimax": "minimax/haibo/video-generation",
    }

    # Defaults
    DEFAULT_IMAGE_MODEL = "nano-banano"
    DEFAULT_VIDEO_MODEL = "kling-3"
    DEFAULT_ASPECT = "9:16"  # Vertical for TikTok/Reels
    DEFAULT_DURATION = 10  # seconds


config = Config()

# ============================================================
# HIGGSFIELD CLIENT
# ============================================================

try:
    import higgsfield_client

    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    print("⚠️  Installing higgsfield-client...")
    os.system("pip3 install higgsfield-client --break-system-packages")
    try:
        import higgsfield_client

        HAS_SDK = True
    except:
        HAS_SDK = False


def get_client():
    """Get Higgsfield client with credentials."""
    if not HAS_SDK:
        print("❌ Higgsfield SDK not available")
        return None

    creds = config.HF_CREDENTIALS
    if not creds or creds == ":":
        print("❌ Set HF_CREDENTIALS='KEY_ID:KEY_SECRET'")
        return None

    os.environ["HF_KEY"] = creds
    return higgsfield_client


def upload_file(file_path: str) -> Optional[str]:
    """Upload file and return URL."""
    client = get_client()
    if not client:
        return None

    try:
        url = client.upload_file(file_path)
        return url
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


# ============================================================
# IMAGE GENERATION
# ============================================================


def generate_image(
    prompt: str,
    output_path: str,
    model: str = "nano-banano",
    aspect_ratio: str = "9:16",
    style: str = "luxury_product",
) -> Optional[str]:
    """
    Generate product image.

    Models:
      - nano-banano: Fast 4K (1 credit) ← DEFAULT
      - flux-pro: Best quality (2 credits)
      - flux-dev: Free tier
    """
    client = get_client()
    if not client:
        return None

    model_id = config.IMAGE_MODELS.get(model, config.IMAGE_MODELS["nano-banano"])

    # Enhance prompt based on style
    enhanced_prompt = enhance_prompt(prompt, style)

    print(f"🎨 Generating image ({model})...")
    print(f"   Prompt: {enhanced_prompt[:80]}...")

    try:
        result = client.subscribe(
            model_id,
            arguments={
                "input": enhanced_prompt,
                "aspect_ratio": aspect_ratio,
            },
            with_polling=True,
            timeout=300,
        )

        if result and result.get("images"):
            image_url = result["images"][0]["url"]

            # Download
            img_data = requests.get(image_url).content
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_data)

            print(f"✅ Saved: {output_path}")
            return image_url

        print(f"❌ No images generated")
        return None

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return None


def enhance_prompt(prompt: str, style: str) -> str:
    """Enhance prompt based on style."""

    style_presets = {
        "luxury_product": ", luxury product photography, high-end fashion editorial, soft studio lighting, 4K ultra detailed, professional photography",
        "lifestyle": ", lifestyle photography, fashion editorial, European aesthetic, warm lighting, magazine quality",
        "mascott": ", animated character style, vibrant colors, dynamic pose, clean background, 2D illustration",
        "story": ", cinematic lighting, dramatic atmosphere, 4K, professional color grading",
    }

    return prompt + style_presets.get(style, "")


# ============================================================
# VIDEO GENERATION
# ============================================================


def generate_video(
    image_path: str,
    output_path: str,
    model: str = "kling-3",
    duration: int = 10,
    motion: str = "smooth",
    prompt: str = "",
) -> Optional[str]:
    """
    Generate video from image.

    Models:
      - kling-3: Kling 3.0 Pro (15s, 3 credits) ← PRIMARY
      - kling-standard: Standard Kling (10s, 2 credits)
      - wan-2: Wan 2.2 (Free tier)
      - minimax: Minimax (5s, Free tier)
    """
    client = get_client()
    if not client:
        return None

    # Upload image first
    print(f"📤 Uploading image...")
    image_url = upload_file(image_path)
    if not image_url:
        return None

    model_id = config.VIDEO_MODELS.get(model, config.VIDEO_MODELS["kling-3"])

    # Adjust duration based on model
    max_duration = {"kling-3": 15, "kling-standard": 10, "wan-2": 10, "minimax": 5}
    duration = min(duration, max_duration.get(model, 10))

    print(f"🎬 Generating video ({model}, {duration}s)...")
    print(f"   Motion: {motion}")

    try:
        args = {
            "input_image": image_url,
            "duration": duration,
            "aspect_ratio": config.DEFAULT_ASPECT,
        }

        # Add prompt if provided
        if prompt:
            args["prompt"] = prompt

        result = client.subscribe(
            model_id,
            arguments=args,
            with_polling=True,
            timeout=600,  # 10 min for video
        )

        if result and result.get("videos"):
            video_url = result["videos"][0]["url"]

            # Download
            video_data = requests.get(video_url).content
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(video_data)

            print(f"✅ Saved: {output_path}")
            return video_url

        print(f"❌ No videos generated")
        return None

    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return None


def generate_video_from_prompt(
    prompt: str, output_path: str, model: str = "kling-3", duration: int = 10
) -> Optional[str]:
    """Generate video directly from text prompt."""

    client = get_client()
    if not client:
        return None

    model_id = config.VIDEO_MODELS.get(model, config.VIDEO_MODELS["kling-3"])

    print(f"🎬 Generating video from prompt ({model}, {duration}s)...")

    try:
        result = client.subscribe(
            model_id,
            arguments={
                "input": prompt,
                "duration": duration,
                "aspect_ratio": config.DEFAULT_ASPECT,
            },
            with_polling=True,
            timeout=600,
        )

        if result and result.get("videos"):
            video_url = result["videos"][0]["url"]

            video_data = requests.get(video_url).content
            with open(output_path, "wb") as f:
                f.write(video_data)

            print(f"✅ Saved: {output_path}")
            return video_url

        return None

    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return None


# ============================================================
# MASCOOT GENERATION
# ============================================================

MASCOOT_PROMPTS = {
    # Paris Adventures (Episodes 1-25)
    "ep1_paris_arrival": "Animated luxury mascott character arriving at Paris Gare du Nord station, carrying Bene2Luxe shopping bag, Eiffel Tower visible through window, cinematic lighting, adventure animation style",
    "ep2_cafe_paris": "Animated mascott sitting at Parisian café terrace, wearing designer sneakers, holding coffee, reading fashion magazine, Paris street background, golden hour lighting",
    "ep3_louvre": "Animated mascott in front of Louvre pyramid, looking at luxury watch display, surrounded by fashion-conscious characters, Paris aesthetic",
    "ep4_champs_elysees": "Animated mascott walking down Champs-Élysées, shopping bags from Chanel Dior LV, iconic storefronts visible, bustling Paris energy",
    "ep5_luxury_store": "Animated mascott inside luxury boutique, trying on designer sneakers, amazed expression, gold and marble interior, premium shopping experience",
    # Swiss Alps (Episodes 6-15)
    "ep6_zermatt_arrival": "Animated mascott arriving in Zermatt Switzerland, Matterhorn in background, luxury ski resort aesthetic, snow falling gently",
    "ep7_ski_lodge": "Animated mascott at cozy Swiss ski lodge, wearing designer winter gear, hot chocolate, mountain view through window",
    "ep8_lausanne": "Animated mascott exploring Lausanne Olympic Museum, surrounded by sports luxury aesthetic, Swiss precision theme",
    # French Riviera (Episodes 16-25)
    "ep16_cannes": "Animated mascott walking Cannes Croisette, luxury yachts in background, Mediterranean blue water, glamour aesthetic",
    "ep17_monaco": "Animated mascott at Monaco casino square, sports car nearby, luxury lifestyle, Monte Carlo elegance",
    "ep18_saint_tropez": "Animated mascott at Saint-Tropez beach club, luxury yachts, Mediterranean lifestyle, summer fashion",
    # Shopping Episodes (26-50)
    "ep26_chanel_boutique": "Animated mascott entering Chanel boutique, greeted by stylish staff, luxury interior, personal shopping experience",
    "ep27_dior_showroom": "Animated mascott in Dior showroom, surrounded by latest collection, fashion week energy",
    "ep28_vintage_paris": "Animated mascott exploring vintage luxury shop in Le Marais, discovering rare pieces, treasure hunting excitement",
    # Lifestyle Episodes (51-75)
    "ep51_brunch_paris": "Animated mascott at stylish Parisian brunch spot, avocado toast and coffee, fashion blogger aesthetic, influencer vibes",
    "ep52_fashion_week": "Animated mascott at Paris Fashion Week, front row seat, celebrity spotting, runway show energy",
    "ep53_art_museum": "Animated mascott at Musée d'Orsay, artistic aesthetic, impressionist paintings, culture appreciation",
    "ep54_boat_party": "Animated mascott on Seine river cruise, city lights, luxury party, Parisian night scene",
    "ep55_football_match": "Animated mascott at PSG match, luxury lounge, sports and fashion combine, Parisian energy",
}


def generate_mascott_episode(
    episode: int, output_path: str, model: str = "kling-3"
) -> Optional[str]:
    """Generate mascott adventure episode video."""

    # Find prompt for episode
    episode_key = f"ep{episode:02d}"

    # Generate from closest match or create generic prompt
    prompt = MASCOOT_PROMPTS.get(
        episode_key,
        f"""
        Animated luxury mascott character in adventure scene,
        Bene2Luxe branding visible, French/European aesthetic,
        cinematic lighting, dynamic action, 4K animation
    """,
    )

    # Generate from prompt
    return generate_video_from_prompt(
        prompt=prompt,
        output_path=output_path,
        model=model,
        duration=15,  # Longer for story content
    )


# ============================================================
# BATCH PROCESSING
# ============================================================


def batch_generate(
    type: str = "product", count: int = 50, model: str = "kling-3"
) -> List[str]:
    """Batch generate content."""

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    batch_size = 10

    print(f"\n📦 Batch generating {count} {type} videos...")

    for i in range(count):
        timestamp = datetime.now().strftime("%H%M%S")
        output = config.OUTPUT_DIR / f"{type}_{i + 1:03d}_{timestamp}.mp4"

        # Use product images if available
        if type == "product":
            images = list(config.PRODUCTS_DIR.glob("*.png"))[:count]
            if images:
                img = images[i % len(images)]
                result = generate_video(
                    image_path=str(img),
                    output_path=str(output),
                    model=model,
                    duration=5,  # Short for product videos
                )
            else:
                # Generate from script
                result = generate_video_from_prompt(
                    prompt=f"Luxury product showcase, Bene2Luxe, professional lighting, fashion editorial, {i + 1}",
                    output_path=str(output),
                    model=model,
                    duration=5,
                )
        else:
            result = generate_video_from_prompt(
                prompt=f"Trending fashion content, French aesthetic, luxury lifestyle, 2026",
                output_path=str(output),
                model=model,
                duration=10,
            )

        if result:
            outputs.append(str(output))

        # Rate limiting
        time.sleep(3)

        # Progress
        if (i + 1) % batch_size == 0:
            print(f"   Progress: {i + 1}/{count}")

    print(f"\n✅ Generated {len(outputs)} videos")
    return outputs


# ============================================================
# CLI INTERFACE
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        description="Bene2Luxe × Higgfields AI - Content Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Generate single image
  python3 higgfields_master.py image --prompt "Chanel sneakers luxury"

  # Generate video from image
  python3 higgfields_master.py video --image product.png --model kling-3

  # Batch generate 50 videos
  python3 higgfields_master.py batch --type product --count 50

  # Generate mascott episode
  python3 higgfields_master.py mascott --episode 1

  # Free tier generation
  python3 higgfields_master.py image --prompt "fashion" --model flux-dev
  python3 higgfields_master.py video --image photo.png --model wan-2

CREDITS:
  ~600 Nano Banano Pro (image)
  ~200 Kling 3.0 (video)
  Unlimited free models
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # IMAGE COMMAND
    img_parser = subparsers.add_parser("image", help="Generate product image")
    img_parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    img_parser.add_argument("--output", "-o", help="Output path")
    img_parser.add_argument(
        "--model",
        "-m",
        default="nano-banano",
        choices=["nano-banano", "flux-pro", "flux-dev"],
    )
    img_parser.add_argument(
        "--aspect", "-a", default="9:16", choices=["1:1", "9:16", "16:9"]
    )
    img_parser.add_argument(
        "--style",
        "-s",
        default="luxury_product",
        choices=["luxury_product", "lifestyle", "mascott", "story"],
    )

    # VIDEO COMMAND
    vid_parser = subparsers.add_parser("video", help="Generate video from image")
    vid_parser.add_argument("--image", "-i", help="Input image path")
    vid_parser.add_argument("--prompt", "-p", help="Text prompt (for text-to-video)")
    vid_parser.add_argument("--output", "-o", help="Output path")
    vid_parser.add_argument(
        "--model",
        "-m",
        default="kling-3",
        choices=["kling-3", "kling-standard", "wan-2", "minimax"],
    )
    vid_parser.add_argument("--duration", "-d", type=int, default=10)

    # BATCH COMMAND
    batch_parser = subparsers.add_parser("batch", help="Batch generate content")
    batch_parser.add_argument(
        "--type", "-t", default="product", choices=["product", "lifestyle", "trends"]
    )
    batch_parser.add_argument("--count", "-c", type=int, default=50)
    batch_parser.add_argument(
        "--model",
        "-m",
        default="kling-3",
        choices=["kling-3", "kling-standard", "wan-2", "minimax"],
    )

    # MASCOOT COMMAND
    masc_parser = subparsers.add_parser("mascott", help="Generate mascott episode")
    masc_parser.add_argument(
        "--episode", "-e", type=int, required=True, help="Episode number (1-75)"
    )
    masc_parser.add_argument("--output", "-o", help="Output path")
    masc_parser.add_argument("--model", "-m", default="kling-3")

    # LIST COMMAND
    subparsers.add_parser("models", help="List available models")
    subparsers.add_parser("prompts", help="List mascott prompts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # LIST MODELS
    if args.command == "models":
        print("\n📸 IMAGE MODELS:")
        for name, model_id in config.IMAGE_MODELS.items():
            credits = "1" if "nano" in name else ("2" if "flux-pro" in name else "FREE")
            print(f"   {name}: {model_id} ({credits} credit)")

        print("\n🎬 VIDEO MODELS:")
        for name, model_id in config.VIDEO_MODELS.items():
            credits_map = {
                "kling-3": "3",
                "kling-standard": "2",
                "wan-2": "FREE",
                "minimax": "FREE",
            }
            print(f"   {name}: {model_id} ({credits_map.get(name, '?')} credits)")
        return

    # LIST PROMPTS
    if args.command == "prompts":
        print("\n🎭 MASCOOT EPISODE PROMPTS:")
        for key, prompt in MASCOOT_PROMPTS.items():
            print(f"   {key}: {prompt[:60]}...")
        return

    # IMAGE GENERATION
    if args.command == "image":
        output = args.output or str(
            config.OUTPUT_DIR / f"image_{datetime.now().strftime('%H%M%S')}.png"
        )
        generate_image(
            prompt=args.prompt,
            output_path=output,
            model=args.model,
            aspect_ratio=args.aspect,
            style=args.style,
        )

    # VIDEO GENERATION
    elif args.command == "video":
        if not args.image and not args.prompt:
            print("❌ Provide --image or --prompt")
            return

        output = args.output or str(
            config.OUTPUT_DIR / f"video_{datetime.now().strftime('%H%M%S')}.mp4"
        )

        if args.image:
            generate_video(
                image_path=args.image,
                output_path=output,
                model=args.model,
                duration=args.duration,
            )
        else:
            generate_video_from_prompt(
                prompt=args.prompt,
                output_path=output,
                model=args.model,
                duration=args.duration,
            )

    # BATCH GENERATION
    elif args.command == "batch":
        outputs = batch_generate(type=args.type, count=args.count, model=args.model)
        print(f"\n📁 Generated {len(outputs)} files")
        for o in outputs[:5]:
            print(f"   {o}")
        if len(outputs) > 5:
            print(f"   ... and {len(outputs) - 5} more")

    # MASCOOT EPISODE
    elif args.command == "mascott":
        output = args.output or str(
            config.OUTPUT_DIR / f"mascott_ep{args.episode:02d}.mp4"
        )
        generate_mascott_episode(
            episode=args.episode, output_path=output, model=args.model
        )


if __name__ == "__main__":
    main()
