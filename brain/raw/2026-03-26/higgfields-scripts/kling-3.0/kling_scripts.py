#!/usr/bin/env python3
"""
Bene2Luxe × Kling 3.0 - Video Generation Scripts
=============================================

Kling 3.0 API integration for product videos and mascott adventures.
Primary model with ~200 credits available.

MODELS:
  kling-v3           - Latest Kling 3.0
  kling-v2.6-pro    - Professional quality
  kling-v2.6-std    - Standard quality, faster
  kling-v2.5-turbo  - Fastest generation

USAGE:
  python3 kling_scripts.py --help
  python3 kling_scripts.py t2v --prompt "luxury sneakers"
  python3 kling_scripts.py i2v --image product.png --prompt "sneaker rotating"
  python3 kling_scripts.py batch --file prompts.txt

Author: Elia - Bene2Luxe Content System
Date: 26 Mars 2026
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

API_KEY = os.environ.get("KLING_API_KEY", "")
BASE_URL = "https://api.klingapi.com/v1"


@dataclass
class VideoResult:
    task_id: str
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None


def create_text_to_video(
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "9:16",
    mode: str = "standard",
    model: str = "kling-v2.6-pro",
) -> str:
    """Generate video from text prompt."""
    response = requests.post(
        f"{BASE_URL}/videos/text2video",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
        },
    )
    response.raise_for_status()
    return response.json()["task_id"]


def create_image_to_video(
    image_url: str,
    prompt: str,
    duration: int = 5,
    mode: str = "standard",
    model: str = "kling-v2.6-pro",
) -> str:
    """Generate video from image."""
    response = requests.post(
        f"{BASE_URL}/videos/image2video",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
            "mode": mode,
        },
    )
    response.raise_for_status()
    return response.json()["task_id"]


def get_status(task_id: str) -> dict:
    """Check video generation status."""
    response = requests.get(
        f"{BASE_URL}/videos/{task_id}", headers={"Authorization": f"Bearer {API_KEY}"}
    )
    response.raise_for_status()
    return response.json()


def wait_for_completion(
    task_id: str, poll_interval: int = 5, timeout: int = 300
) -> dict:
    """Poll until video is ready."""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Video generation timed out for task {task_id}")

        status = get_status(task_id)
        state = status.get("status")

        if state == "completed":
            return status
        elif state == "failed":
            raise RuntimeError(f"Video generation failed: {status.get('error')}")

        print(f"  Status: {state} - Waiting {poll_interval}s...")
        time.sleep(poll_interval)


def download_video(url: str, output_path: str) -> str:
    """Download video to file."""
    response = requests.get(url)
    response.raise_for_status()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def generate_and_save(
    prompt: str,
    output_path: str,
    duration: int = 5,
    model: str = "kling-v2.6-pro",
    aspect: str = "9:16",
) -> VideoResult:
    """Full generation pipeline: create -> wait -> download."""
    print(f"🎬 Creating video: {prompt[:60]}...")

    task_id = create_text_to_video(
        prompt, duration=duration, aspect_ratio=aspect, model=model
    )
    print(f"  Task ID: {task_id}")

    result = wait_for_completion(task_id)
    video_url = result["output"]["video_url"]

    download_video(video_url, output_path)
    print(f"✅ Saved: {output_path}")

    return VideoResult(task_id=task_id, status="completed", video_url=video_url)


# ============================================================================
# BENE2LUXE PRODUCT PROMPTS
# ============================================================================

BEN2LUXE_PROMPTS = {
    "chanel_sneakers": [
        "Luxury Chanel La Pause sneakers in grey suede with green sole, professional product photography, soft studio lighting, fashion editorial",
        "Close-up of Chanel grey suede sneakers rotating slowly, green sole visible, luxury product showcase, white background",
        "Chanel sneakers on white marble surface, soft shadows, fashion magazine style, 4K quality",
    ],
    "dior_b23": [
        "Dior B23 white canvas sneakers with transparent sole, black square logo, luxury sneaker photography, clean background",
        "White Dior sneakers slowly rotating, iconic design, premium materials, fashion editorial lighting",
        "Dior B23 on designer display, transparent sole detail visible, luxury retail aesthetic",
    ],
    "dior_sunglasses": [
        "Dior D-BEJE 3 sunglasses with grey gradient lens, luxury eyewear photography, studio lighting",
        "Designer sunglasses rotating slowly, grey gradient lens reflecting light, premium quality showcase",
        "Dior sunglasses on velvet display, luxury boutique aesthetic, professional product photography",
    ],
    "louis_vuitton": [
        "Louis Vuitton monogram bag on luxury display, iconic canvas visible, premium leather trim",
        "LV accessories collection, monogram pattern, luxury lifestyle photography, fashion editorial",
        "Louis Vuitton bag rotating slowly, heritage craftsmanship visible, premium quality showcase",
    ],
    "gucci": [
        "Gucci accessories with iconic double-G hardware, premium Italian leather, luxury brand aesthetic",
        "Gucci GG buckle detail, leather texture visible, luxury craftsmanship, fashion photography",
        "Gucci belt rotating slowly, signature hardware, premium Italian quality showcase",
    ],
    "caps": [
        "Premium branded caps rotating slowly, quality embroidery visible, luxury accessory photography",
        "Designer caps on white background, premium materials, fashion accessory showcase",
        "Luxury caps displayed elegantly, quality construction visible, fashion editorial style",
    ],
    "lifestyle": [
        "Parisian woman wearing luxury sneakers and designer accessories, street style fashion, elegant casual outfit",
        "Luxury fashion lifestyle, European aesthetic, warm lighting, fashion magazine spread",
        "Premium sneakers and accessories in minimalist luxury setting, natural light, lifestyle photography",
    ],
    "mascott_paris": [
        "Animated luxury mascott character in Paris, Eiffel Tower background, adventure animation style",
        "Animated mascot exploring luxury boutique, shopping bags, Parisian street scene",
        "Mascott character with designer products, French flag background, vibrant animation",
    ],
    "mascott_swiss": [
        "Animated mascott in Swiss Alps, Matterhorn background, luxury ski resort aesthetic",
        "Animated character at Swiss ski lodge, designer winter gear, mountain lifestyle",
        "Mascott with luxury accessories in snowy Swiss landscape, adventure animation",
    ],
}


def get_bene2luxe_prompts(
    category: str = "chanel_sneakers", count: int = 3
) -> List[str]:
    """Get product prompts for Bene2Luxe."""
    prompts = BEN2LUXE_PROMPTS.get(category, BEN2LUXE_PROMPTS["chanel_sneakers"])
    return prompts[:count]


# ============================================================================
# CLI COMMANDS
# ============================================================================


def cmd_t2v(args):
    """Text-to-video generation."""
    output = args.output or f"kling_t2v_{datetime.now().strftime('%H%M%S')}.mp4"
    generate_and_save(
        args.prompt,
        output,
        duration=args.duration,
        model=args.model,
        aspect=args.aspect,
    )


def cmd_i2v(args):
    """Image-to-video generation."""
    if not os.path.exists(args.image):
        print(f"❌ Image not found: {args.image}")
        return

    print(f"📤 Uploading image...")
    import higgsfield_client

    image_url = higgsfield_client.upload_file(args.image)
    if not image_url:
        print("❌ Upload failed")
        return

    print(f"🎬 Creating video...")
    task_id = create_image_to_video(
        image_url, args.prompt, duration=args.duration, model=args.model
    )
    print(f"  Task ID: {task_id}")

    result = wait_for_completion(task_id)
    video_url = result["output"]["video_url"]

    output = args.output or f"kling_i2v_{datetime.now().strftime('%H%M%S')}.mp4"
    download_video(video_url, output)
    print(f"✅ Saved: {output}")


def cmd_batch(args):
    """Batch generation from file."""
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
        output = output_dir / f"video_{i + 1:03d}.mp4"
        try:
            result = generate_and_save(
                prompt,
                str(output),
                duration=args.duration,
                model=args.model,
                aspect=args.aspect,
            )
            results.append(
                {"prompt": prompt, "status": "success", "output": str(output)}
            )
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({"prompt": prompt, "status": "failed", "error": str(e)})

        if i < len(prompts) - 1:
            time.sleep(args.delay)

    # Save results
    results_file = output_dir / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📊 Results saved: {results_file}")


def cmd_prompts(args):
    """List available product prompts."""
    print("\n📦 Available Bene2Luxe Product Prompts:")
    print("=" * 50)
    for category, prompts in BEN2LUXE_PROMPTS.items():
        print(f"\n🎯 {category}:")
        for p in prompts:
            print(f"   • {p[:70]}...")


def cmd_generate_category(args):
    """Generate videos for a specific category."""
    prompts = get_bene2luxe_prompts(args.category, count=args.count)

    output_dir = Path(args.output_dir) / args.category
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Generating {len(prompts)} videos for {args.category}...")

    for i, prompt in enumerate(prompts):
        output = output_dir / f"{args.category}_{i + 1}.mp4"
        try:
            generate_and_save(
                prompt,
                str(output),
                duration=args.duration,
                model=args.model,
                aspect=args.aspect,
            )
        except Exception as e:
            print(f"❌ Failed: {e}")

        time.sleep(args.delay)


# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Bene2Luxe × Kling 3.0 Video Generator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Text-to-video
    t2v = subparsers.add_parser("t2v", help="Generate video from text")
    t2v.add_argument("--prompt", "-p", required=True, help="Video prompt")
    t2v.add_argument("--output", "-o", help="Output file")
    t2v.add_argument("--duration", "-d", type=int, default=5, help="Duration (1-10s)")
    t2v.add_argument(
        "--model",
        "-m",
        default="kling-v2.6-pro",
        choices=["kling-v3", "kling-v2.6-pro", "kling-v2.6-std", "kling-v2.5-turbo"],
    )
    t2v.add_argument("--aspect", "-a", default="9:16", choices=["9:16", "16:9", "1:1"])

    # Image-to-video
    i2v = subparsers.add_parser("i2v", help="Generate video from image")
    i2v.add_argument("--image", "-i", required=True, help="Input image")
    i2v.add_argument("--prompt", "-p", default="", help="Motion prompt")
    i2v.add_argument("--output", "-o", help="Output file")
    i2v.add_argument("--duration", "-d", type=int, default=5, help="Duration (1-10s)")
    i2v.add_argument("--model", "-m", default="kling-v2.6-pro")

    # Batch
    batch = subparsers.add_parser("batch", help="Batch generate from file")
    batch.add_argument(
        "--file", "-f", required=True, help="Prompts file (one per line)"
    )
    batch.add_argument(
        "--output-dir", "-o", default="./kling_output", help="Output directory"
    )
    batch.add_argument("--duration", "-d", type=int, default=5, help="Duration")
    batch.add_argument("--model", "-m", default="kling-v2.6-pro")
    batch.add_argument("--delay", type=int, default=10, help="Delay between requests")

    # Category generation
    cat = subparsers.add_parser("category", help="Generate for product category")
    cat.add_argument(
        "--category",
        "-c",
        required=True,
        choices=list(BEN2LUXE_PROMPTS.keys()),
        help="Product category",
    )
    cat.add_argument("--count", type=int, default=3, help="Number of videos")
    cat.add_argument(
        "--output-dir", "-o", default="./kling_output", help="Output directory"
    )
    cat.add_argument("--duration", "-d", type=int, default=5, help="Duration")
    cat.add_argument("--delay", type=int, default=10, help="Delay between requests")

    # List prompts
    subparsers.add_parser("prompts", help="List available prompts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "t2v":
        cmd_t2v(args)
    elif args.command == "i2v":
        cmd_i2v(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "category":
        cmd_generate_category(args)
    elif args.command == "prompts":
        cmd_prompts(args)


if __name__ == "__main__":
    main()
