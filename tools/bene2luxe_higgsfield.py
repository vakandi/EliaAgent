#!/usr/bin/env python3
"""
Bene2Luxe × Higgsfield AI - Content Generation Script
Generates product images and videos using Higgsfield API.

Setup:
  pip install higgsfield-client pillow requests

Usage:
  python3 bene2luxe_higgsfield.py --help
  python3 bene2luxe_higgsfield.py image --prompt "Chanel sneakers on marble"
  python3 bene2luxe_higgsfield.py video --image product.png --duration 5
  python3 bene2luxe_higgsfield.py batch --dir ./products/
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, List
from PIL import Image
import time

# ============================================================
# CONFIGURATION
# ============================================================

# Get from environment or cloud.higgsfield.ai dashboard
HF_KEY = os.environ.get("HF_KEY", "")
HF_KEY_ID = os.environ.get("HF_KEY_ID", "")
HF_KEY_SECRET = os.environ.get("HF_KEY_SECRET", "")

# Credentials format: KEY_ID:KEY_SECRET (for v2 client)
HF_CREDENTIALS = os.environ.get("HF_CREDENTIALS", "")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# HIGGSFIELD PYTHON SDK (v2 style - synchronous)
# ============================================================

try:
    import higgsfield_client

    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    print("⚠️  higgsfield-client not installed. Run: pip install higgsfield-client")


def get_higgsfield_client():
    """Create Higgsfield API client."""
    if not HAS_SDK:
        print("❌ Higgsfield SDK not available. Install: pip install higgsfield-client")
        return None

    # Try different credential formats
    creds = HF_CREDENTIALS or f"{HF_KEY_ID}:{HF_KEY_SECRET}"

    if not creds or creds == ":":
        print("❌ No Higgsfield credentials found.")
        print("   Set HF_CREDENTIALS='KEY_ID:KEY_SECRET'")
        print("   Or set HF_KEY_ID and HF_KEY_SECRET")
        print("   Get credentials at: https://cloud.higgsfield.ai")
        return None

    # Using the synchronous client
    os.environ["HF_KEY"] = creds
    return higgsfield_client


def upload_image(image_path: str) -> Optional[str]:
    """Upload image to Higgsfield and return URL."""
    if not HAS_SDK:
        return None

    client = get_higgsfield_client()
    if not client:
        return None

    try:
        url = client.upload_file(image_path)
        print(f"✅ Image uploaded: {url}")
        return url
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


def generate_product_image(
    prompt: str,
    output_path: str,
    model: str = "flux-pro/kontext/max/text-to-image",
    aspect_ratio: str = "1:1",
) -> Optional[str]:
    """
    Generate a product image using Higgsfield.

    Models:
    - flux-pro/kontext/max/text-to-image (default - best quality)
    - nano-banana-pro/text-to-image (fast, 4K)
    - bytedance/seedream/v4/text-to-image (photo realistic)
    """
    if not HAS_SDK:
        return None

    client = get_higgsfield_client()
    if not client:
        return None

    print(f"🎨 Generating image: {prompt[:50]}...")

    try:
        result = client.subscribe(
            model,
            arguments={
                "input": prompt,
                "aspect_ratio": aspect_ratio,
            },
            with_polling=True,
            timeout=300,
        )

        if result and result.get("images"):
            image_url = result["images"][0]["url"]
            print(f"✅ Generated: {image_url}")

            # Download and save
            img_data = requests.get(image_url).content
            with open(output_path, "wb") as f:
                f.write(img_data)
            print(f"💾 Saved: {output_path}")
            return image_url
        else:
            print(f"❌ No images in result: {result}")
            return None

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return None


def generate_product_video(
    image_path: str,
    output_path: str,
    duration: int = 5,
    model: str = "kling-video/pro/video-generation",
) -> Optional[str]:
    """
    Generate a video from a product image.

    Models:
    - kling-video/pro/video-generation (Kling 3.0 - 15s videos, character consistent)
    - kling-video/standard/video-generation (standard Kling)
    - minimax/haibo/video-generation (fast, 5s)
    - wan/wan-video/video-generation (Wan 2.2)

    Duration: 5-15 seconds depending on model
    """
    if not HAS_SDK:
        return None

    client = get_higgsfield_client()
    if not client:
        return None

    # Upload image first
    image_url = upload_image(image_path)
    if not image_url:
        return None

    print(f"🎬 Generating video from: {image_path}...")

    try:
        result = client.subscribe(
            model,
            arguments={
                "input_image": image_url,
                "duration": duration,
                "aspect_ratio": "9:16",  # Vertical for TikTok/Reels
            },
            with_polling=True,
            timeout=600,  # 10 min for video
        )

        if result and result.get("videos"):
            video_url = result["videos"][0]["url"]
            print(f"✅ Generated: {video_url}")

            # Download and save
            video_data = requests.get(video_url).content
            with open(output_path, "wb") as f:
                f.write(video_data)
            print(f"💾 Saved: {output_path}")
            return video_url
        else:
            print(f"❌ No videos in result: {result}")
            return None

    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return None


def generate_video_from_prompt(
    prompt: str, output_path: str, duration: int = 10
) -> Optional[str]:
    """Generate a video directly from a text prompt."""
    if not HAS_SDK:
        return None

    client = get_higgsfield_client()
    if not client:
        return None

    print(f"🎬 Generating video: {prompt[:50]}...")

    try:
        # Text-to-video
        result = client.subscribe(
            "kling-video/pro/video-generation",
            arguments={
                "input": prompt,
                "duration": duration,
                "aspect_ratio": "9:16",
            },
            with_polling=True,
            timeout=600,
        )

        if result and result.get("videos"):
            video_url = result["videos"][0]["url"]
            print(f"✅ Generated: {video_url}")

            video_data = requests.get(video_url).content
            with open(output_path, "wb") as f:
                f.write(video_data)
            print(f"💾 Saved: {output_path}")
            return video_url
        else:
            print(f"❌ No videos in result: {result}")
            return None

    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return None


# ============================================================
# BENE2LUXE PRODUCT PROMPTS
# ============================================================

BEN2LUXE_PROMPTS = {
    "chanel_la_pause": [
        "Luxury Chanel La Pause sneakers in grey suede with green sole, on white marble floor, studio photography, soft lighting, high-end fashion editorial, 4K",
        "Close-up of Chanel grey suede sneakers with signature green sole, luxury product photography, clean white background, fashion magazine style, 4K",
        "Chanel sneakers displayed elegantly on designer pedestal, grey suede texture visible, green sole accent, luxury retail environment, professional product shot",
    ],
    "dior_b23": [
        "Dior B23 white canvas sneakers with transparent sole and black square logo, luxury sneaker photography, clean white background, fashion editorial, 4K",
        "Close-up Dior B23 white canvas sneakers, iconic transparent sole detail, black Dior square logo, luxury product photography, high-end fashion magazine, 4K",
        "Dior white sneakers on white marble surface, clean luxury aesthetic, fashion photography, soft shadows, premium product presentation, 4K",
    ],
    "dior_sunglasses": [
        "Dior D-BEJE 3 sunglasses with grey gradient lens, luxury eyewear photography, clean studio background, fashion editorial, premium quality, 4K",
        "Close-up of Dior sunglasses, grey gradient lens detail, premium frame quality, luxury eyewear catalog photography, fashion magazine style, 4K",
        "Dior designer sunglasses on velvet display, grey gradient lens reflecting light, luxury boutique aesthetic, premium product photography, 4K",
    ],
    "louis_vuitton": [
        "Louis Vuitton monogram bag on luxury display, iconic LV canvas visible, premium leather trim, luxury retail environment, fashion editorial photography, 4K",
        "Louis Vuitton accessories collection, monogram pattern, premium quality, luxury lifestyle photography, fashion magazine, 4K",
    ],
    "gucci": [
        "Gucci accessories with iconic double-G hardware, premium Italian leather, luxury brand aesthetic, fashion editorial photography, clean studio, 4K",
        "Close-up of Gucci GG buckle detail, premium leather texture, luxury craftsmanship, high-end fashion photography, 4K",
    ],
    "lifestyle_1": [
        "Luxury sneakers on designer coffee table, grey suede and white canvas, lifestyle home interior, warm lighting, fashion magazine spread, 4K",
        "Premium sneakers displayed in minimalist luxury apartment, natural light from window, fashion editorial, European interior, 4K",
    ],
    "lifestyle_2": [
        "Parisian woman wearing Chanel sneakers and Dior sunglasses, street style fashion, elegant casual outfit, Parisian café background, fashion editorial, 4K",
        "Elegant outfit featuring luxury sneakers and designer accessories, stylish woman in urban setting, fashion magazine, 4K",
    ],
}


# ============================================================
# BATCH PROCESSING
# ============================================================


def batch_generate_images(category: str = "chanel_la_pause", count: int = 5):
    """Generate multiple images for a category."""
    prompts = BEN2LUXE_PROMPTS.get(category, BEN2LUXE_PROMPTS["chanel_la_pause"])

    for i, prompt in enumerate(prompts[:count]):
        output = OUTPUT_DIR / f"{category}_image_{i + 1}.png"
        generate_product_image(prompt, str(output))
        time.sleep(2)  # Rate limiting


def batch_generate_videos_from_images(image_dir: str, count: int = 10):
    """Generate videos from product images in a directory."""
    image_dir = Path(image_dir)
    if not image_dir.exists():
        print(f"❌ Directory not found: {image_dir}")
        return

    images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))[:count]

    if not images:
        print(f"❌ No images found in: {image_dir}")
        return

    print(f"📁 Found {len(images)} images")

    for i, img_path in enumerate(images):
        output = OUTPUT_DIR / f"video_{img_path.stem}.mp4"
        print(f"\n🎬 [{i + 1}/{len(images)}] Processing: {img_path.name}")
        generate_product_video(str(img_path), str(output), duration=5)
        time.sleep(5)  # Rate limiting


# ============================================================
# MAIN CLI
# ============================================================


def main():
    parser = argparse.ArgumentParser(
        description="Bene2Luxe × Higgsfield AI Content Generator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Image generation
    img_parser = subparsers.add_parser("image", help="Generate product image")
    img_parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    img_parser.add_argument("--output", "-o", help="Output file path")
    img_parser.add_argument(
        "--aspect", "-a", default="1:1", help="Aspect ratio (1:1, 9:16, 16:9)"
    )
    img_parser.add_argument(
        "--model", "-m", default="flux-pro/kontext/max/text-to-image", help="Model"
    )

    # Video generation from image
    vid_parser = subparsers.add_parser("video", help="Generate video from image")
    vid_parser.add_argument("--image", "-i", required=True, help="Input image path")
    vid_parser.add_argument("--output", "-o", help="Output video path")
    vid_parser.add_argument(
        "--duration", "-d", type=int, default=5, help="Duration (5-15s)"
    )
    vid_parser.add_argument(
        "--model", "-m", default="kling-video/pro/video-generation", help="Model"
    )

    # Batch commands
    batch_parser = subparsers.add_parser("batch", help="Batch generate from directory")
    batch_parser.add_argument("--dir", "-d", required=True, help="Image directory")
    batch_parser.add_argument("--count", "-c", type=int, default=10, help="Max images")
    batch_parser.add_argument(
        "--type",
        "-t",
        choices=["image", "video"],
        default="video",
        help="Generation type",
    )

    # List prompts
    subparsers.add_parser("prompts", help="List available product prompts")

    args = parser.parse_args()

    if not args.command or args.command == "prompts":
        print("\n📦 Available Bene2Luxe Product Prompts:")
        print("=" * 50)
        for cat, prompts in BEN2LUXE_PROMPTS.items():
            print(f"\n🎯 {cat}:")
            for p in prompts:
                print(f"   • {p[:70]}...")
        print("\n✅ Use: python3 bene2luxe_higgsfield.py image --prompt 'YOUR PROMPT'")
        return

    if args.command == "image":
        output = args.output or str(OUTPUT_DIR / "generated_image.png")
        generate_product_image(
            args.prompt, output, aspect_ratio=args.aspect, model=args.model
        )

    elif args.command == "video":
        output = args.output or str(OUTPUT_DIR / "generated_video.mp4")
        generate_product_video(
            args.image, output, duration=args.duration, model=args.model
        )

    elif args.command == "batch":
        if args.type == "video":
            batch_generate_videos_from_images(args.dir, count=args.count)
        else:
            batch_generate_images(count=args.count)


if __name__ == "__main__":
    main()
