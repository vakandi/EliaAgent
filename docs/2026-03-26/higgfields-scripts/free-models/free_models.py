#!/usr/bin/env python3
"""
Bene2Luxe × Free Models - Video Generation Scripts
==================================================

Free tier video generation using:
  - Flux Dev (images)
  - Wan 2.2 (videos)
  - Minimax (videos)

Unlimited generation for high-volume content.

USAGE:
  python3 free_models.py --help
  python3 free_models.py image --prompt "luxury sneakers"
  python3 free_models.py video --image product.png
  python3 free_models.py batch --file prompts.txt

Author: Elia - Bene2Luxe Content System
Date: 26 Mars 2026
"""

import os
import time
import json
import argparse
import requests
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def generate_image_free(
    prompt: str, output_path: str, model: str = "flux-dev", aspect_ratio: str = "9:16"
) -> Optional[str]:
    """Generate image using free Flux Dev model."""
    try:
        import higgsfield_client

        result = higgsfield_client.subscribe(
            f"{model}/text-to-image",
            arguments={
                "input": prompt,
                "aspect_ratio": aspect_ratio,
            },
            with_polling=True,
            timeout=300,
        )

        if result and result.get("images"):
            image_url = result["images"][0]["url"]

            response = requests.get(image_url)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            return output_path

        return None
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None


def generate_video_free(
    image_path: str,
    output_path: str,
    model: str = "wan/wan-video/video-generation",
    duration: int = 5,
    prompt: str = "",
) -> Optional[str]:
    """Generate video using free Wan 2.2 or Minimax models."""
    try:
        import higgsfield_client

        print(f"📤 Uploading image...")
        image_url = higgsfield_client.upload_file(image_path)
        if not image_url:
            print("❌ Upload failed")
            return None

        print(f"🎬 Generating video ({model})...")

        args = {
            "input_image": image_url,
            "duration": duration,
            "aspect_ratio": "9:16",
        }

        if prompt:
            args["prompt"] = prompt

        result = higgsfield_client.subscribe(
            model,
            arguments=args,
            with_polling=True,
            timeout=600,
        )

        if result and result.get("videos"):
            video_url = result["videos"][0]["url"]

            response = requests.get(video_url)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            return output_path

        return None
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return None


def generate_video_from_prompt_free(
    prompt: str,
    output_path: str,
    model: str = "wan/wan-video/video-generation",
    duration: int = 10,
) -> Optional[str]:
    """Generate video directly from text prompt using free models."""
    try:
        import higgsfield_client

        result = higgsfield_client.subscribe(
            model,
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

            response = requests.get(video_url)
            with open(output_path, "wb") as f:
                f.write(response.content)

            return output_path

        return None
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return None


# ============================================================================
# BENE2LUXE TRENDING PROMPTS
# ============================================================================

BEN2LUXE_TRENDING_PROMPTS = {
    "french_dream": [
        "Parisian woman with luxury accessories, French Dream aesthetic, coffee at café, fashion editorial, golden hour lighting",
        "French lifestyle content creator with Chanel sneakers, vintage bookshop background, intellectual aesthetic, fashion magazine",
        "Elegant Parisian couple at luxury boutique, shopping bags from Chanel Dior, romantic date aesthetic, fashion editorial",
    ],
    "luxury_lifestyle": [
        "Luxury lifestyle content, designer sneakers and accessories, minimalist apartment interior, natural light, fashion influencer style",
        "Premium fashion showcase, multiple luxury brands displayed elegantly, lifestyle photography, European aesthetic",
        "Fashion blogger with designer collection, Instagram aesthetic, perfectly curated flat lay, luxury lifestyle content",
    ],
    "street_style": [
        "French street style, fashion-forward outfit with luxury sneakers, Parisian architecture background, editorial photography",
        "Urban luxury fashion, designer streetwear outfit, city street aesthetic, fashion magazine style",
        "Trendy French youth fashion, sneakers and designer pieces, street photography, candid style content",
    ],
    "seasonal_spring": [
        "Spring fashion content, luxury sneakers with floral dress, Parisian spring aesthetic, soft lighting, fashion editorial",
        "Easter weekend fashion, designer accessories with pastel outfit, European spring lifestyle, fashion magazine",
        "Spring luxury content, Chanel sneakers with light trench coat, Parisian streets, warm sunlight, fashion editorial",
    ],
    "viral_trends": [
        "Viral TikTok fashion content, trendy outfit with luxury sneakers, catchy visual style, Gen Z aesthetic",
        "Trending Reels content, designer fashion with urban backdrop, Instagram influencer aesthetic, viral style",
        "Snapchat Spotlight style content, luxury fashion, dynamic poses, Gen Z energy, trendy aesthetic",
    ],
}

# ============================================================================
# MASCOOT FREE PROMPTS
# ============================================================================

MASCOOT_FREE_PROMPTS = {
    "paris_adventure": [
        "Animated luxury mascott character in Paris, Eiffel Tower background, adventure animation, vibrant colors",
        "Animated mascot exploring Champs-Élysées, shopping bags, Parisian street scene, cartoon style",
        "Mascott character with Chanel sneakers, Louvre pyramid background, French flag, animated adventure",
    ],
    "swiss_adventure": [
        "Animated mascott in Swiss Alps, Matterhorn mountain, ski resort aesthetic, cartoon adventure style",
        "Cute mascot character with designer winter gear, Swiss snow landscape, playful animation",
        "Animated mascot at Swiss luxury hotel, mountain background, adventure cartoon, vibrant colors",
    ],
    "beach_luxury": [
        "Animated mascott on yacht, Mediterranean sea background, luxury lifestyle, summer vacation cartoon",
        "Cute mascot character at Saint-Tropez beach, designer sunglasses, beach fashion, playful animation",
        "Animated mascot with luxury accessories, French Riviera aesthetic, yacht lifestyle, cartoon style",
    ],
    "everyday_life": [
        "Animated mascott doing everyday activities, luxury sneakers, casual chic style, cartoon animation",
        "Cute mascot character at Parisian café, coffee and croissant, cozy aesthetic, cartoon illustration",
        "Animated mascot studying or working, designer accessories, intellectual vibe, cartoon style",
    ],
}

# ============================================================================
# CLI
# ============================================================================


def cmd_image(args):
    """Generate free image."""
    output = args.output or f"free_image_{datetime.now().strftime('%H%M%S')}.png"

    print(f"🎨 Generating image ({args.model})...")
    result = generate_image_free(
        args.prompt, output, model=args.model, aspect_ratio=args.aspect
    )

    if result:
        print(f"✅ Saved: {result}")
    else:
        print("❌ Generation failed")


def cmd_video(args):
    """Generate free video."""
    output = args.output or f"free_video_{datetime.now().strftime('%H%M%S')}.mp4"

    if args.prompt:
        print(f"🎬 Generating video from prompt ({args.model})...")
        result = generate_video_from_prompt_free(
            args.prompt, output, model=args.model, duration=args.duration
        )
    elif args.image:
        print(f"🎬 Generating video from image ({args.model})...")
        result = generate_video_free(
            args.image,
            output,
            model=args.model,
            duration=args.duration,
            prompt=args.motion_prompt,
        )
    else:
        print("❌ Provide --prompt or --image")
        return

    if result:
        print(f"✅ Saved: {result}")
    else:
        print("❌ Generation failed")


def cmd_batch(args):
    """Batch generate content."""
    prompts_file = Path(args.file)
    if not prompts_file.exists():
        print(f"❌ File not found: {args.file}")
        return

    prompts = prompts_file.read_text().strip().split("\n")
    prompts = [p.strip() for p in prompts if p.strip()]

    print(f"📦 Processing {len(prompts)} prompts...")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, prompt in enumerate(prompts):
        if args.type == "image":
            output = output_dir / f"image_{i + 1:03d}.png"
            result = generate_image_free(
                prompt, str(output), model=args.model, aspect_ratio=args.aspect
            )
            status = "success" if result else "failed"
        else:
            output = output_dir / f"video_{i + 1:03d}.mp4"
            result = generate_video_from_prompt_free(
                prompt, str(output), model=args.model, duration=args.duration
            )
            status = "success" if result else "failed"

        results.append(
            {
                "prompt": prompt,
                "status": status,
                "output": str(output) if result else None,
            }
        )

        if i < len(prompts) - 1:
            time.sleep(args.delay)

    results_file = output_dir / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(
        f"✅ Generated {len([r for r in results if r['status'] == 'success'])}/{len(results)} files"
    )


def cmd_prompts(args):
    """List available prompts."""
    all_prompts = {**BEN2LUXE_TRENDING_PROMPTS, **MASCOOT_FREE_PROMPTS}

    print("\n📦 Available Trending Prompts:")
    print("=" * 50)
    for category, prompts in all_prompts.items():
        print(f"\n🎯 {category}:")
        for p in prompts[:3]:
            print(f"   • {p[:70]}...")


def main():
    parser = argparse.ArgumentParser(description="Bene2Luxe × Free Models Generator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Image
    img = subparsers.add_parser("image", help="Generate image")
    img.add_argument("--prompt", "-p", required=True)
    img.add_argument("--output", "-o")
    img.add_argument(
        "--model",
        "-m",
        default="flux-dev",
        choices=["flux-dev/text-to-image", "flux-pro/kontext/max/text-to-image"],
    )
    img.add_argument("--aspect", "-a", default="9:16", choices=["1:1", "9:16", "16:9"])

    # Video
    vid = subparsers.add_parser("video", help="Generate video")
    vid.add_argument("--prompt", "-p", help="Text prompt")
    vid.add_argument("--image", "-i", help="Input image")
    vid.add_argument("--motion-prompt", help="Motion description")
    vid.add_argument("--output", "-o")
    vid.add_argument(
        "--model",
        "-m",
        default="wan/wan-video/video-generation",
        choices=["wan/wan-video/video-generation", "minimax/haibo/video-generation"],
    )
    vid.add_argument("--duration", "-d", type=int, default=5)

    # Batch
    batch = subparsers.add_parser("batch", help="Batch generate")
    batch.add_argument("--file", "-f", required=True)
    batch.add_argument("--type", "-t", default="image", choices=["image", "video"])
    batch.add_argument("--output-dir", "-o", default="./free_output")
    batch.add_argument("--model", "-m", default="flux-dev")
    batch.add_argument("--duration", "-d", type=int, default=5)
    batch.add_argument("--aspect", "-a", default="9:16")
    batch.add_argument("--delay", type=int, default=5)

    subparsers.add_parser("prompts", help="List prompts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "image":
        cmd_image(args)
    elif args.command == "video":
        cmd_video(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "prompts":
        cmd_prompts(args)


if __name__ == "__main__":
    main()
