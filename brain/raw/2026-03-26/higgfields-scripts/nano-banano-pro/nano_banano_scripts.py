#!/usr/bin/env python3
"""
Bene2Luxe × Nano Banano Pro - Image & Video Generation
=====================================================

Nano Banano Pro API integration for product images and videos.
Primary image model with ~600 credits available.

MODELS:
  nano-banana-pro    - Best 4K image quality
  nano-banana-2      - Standard quality, faster

USAGE:
  python3 nano_banano_scripts.py --help
  python3 nano_banano_scripts.py image --prompt "luxury sneakers"
  python3 nano_banano_scripts.py video --image product.png
  python3 nano_banano_scripts.py batch --file prompts.txt

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

API_KEY = os.environ.get("NANO_BANANO_API_KEY", "")
BASE_URL = "https://nanobananavideo.com/api/v1/"


@dataclass
class GenerationResult:
    success: bool
    video_id: Optional[str] = None
    output_url: Optional[str] = None
    error: Optional[str] = None


def generate_image(
    prompt: str,
    resolution: str = "4K",
    aspect_ratio: str = "9:16",
    style: str = "luxury_product",
) -> Optional[str]:
    """Generate product image using Flux Pro (image generation)."""
    try:
        import higgsfield_client

        enhanced_prompt = enhance_prompt(prompt, style)

        result = higgsfield_client.subscribe(
            "flux-pro/kontext/max/text-to-image",
            arguments={
                "input": enhanced_prompt,
                "aspect_ratio": aspect_ratio,
            },
            with_polling=True,
            timeout=300,
        )

        if result and result.get("images"):
            image_url = result["images"][0]["url"]

            output_path = f"nano_image_{datetime.now().strftime('%H%M%S')}.png"
            response = requests.get(image_url)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)

            return output_path

        return None
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None


def text_to_video(
    prompt: str,
    resolution: str = "1080p",
    duration: int = 5,
    aspect_ratio: str = "16:9",
) -> dict:
    """Generate video from text prompt."""
    response = requests.post(
        f"{BASE_URL}/text-to-video.php",
        headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
        json={
            "prompt": prompt[:500],
            "resolution": resolution,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        },
    )
    response.raise_for_status()
    return response.json()


def image_to_video(
    image_url: str, prompt: str, resolution: str = "1080p", duration: int = 5
) -> dict:
    """Generate video from image."""
    response = requests.post(
        f"{BASE_URL}/image-to-video.php",
        headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
        json={
            "image_urls": [image_url],
            "prompt": prompt[:500],
            "resolution": resolution,
            "duration": duration,
        },
    )
    response.raise_for_status()
    return response.json()


def check_status(video_id: str) -> dict:
    """Check video generation status."""
    response = requests.get(
        f"{BASE_URL}/video-status.php",
        params={"video_id": video_id},
        headers={"X-API-Key": API_KEY},
    )
    response.raise_for_status()
    return response.json()


def wait_for_video(video_id: str, poll_interval: int = 10, timeout: int = 600) -> dict:
    """Poll until video is ready."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        status = check_status(video_id)
        state = status.get("status")

        if state == "completed":
            return status
        elif state == "failed":
            raise RuntimeError(f"Generation failed: {status.get('error')}")

        print(f"  Status: {state} - Waiting {poll_interval}s...")
        time.sleep(poll_interval)

    raise TimeoutError(f"Timeout waiting for video {video_id}")


def download_video(url: str, output_path: str) -> str:
    """Download video to file."""
    response = requests.get(url)
    response.raise_for_status()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def enhance_prompt(prompt: str, style: str) -> str:
    """Enhance prompt based on style."""
    style_presets = {
        "luxury_product": ", luxury product photography, high-end fashion editorial, soft studio lighting, 4K ultra detailed",
        "lifestyle": ", lifestyle photography, fashion editorial, European aesthetic, warm lighting, magazine quality",
        "mascott": ", animated character style, vibrant colors, dynamic pose, clean background, 2D illustration",
    }
    return prompt + style_presets.get(style, "")


# ============================================================================
# BENE2LUXE PRODUCT PROMPTS (Images)
# ============================================================================

BEN2LUXE_IMAGE_PROMPTS = {
    "chanel_la_pause": [
        "Luxury Chanel La Pause sneakers in grey suede with signature green sole, white marble floor, studio photography, soft lighting, high-end fashion editorial, 4K",
        "Close-up of Chanel grey suede sneakers, green sole accent visible, luxury product photography, clean white background, fashion magazine style, 4K",
        "Chanel sneakers on designer pedestal, grey suede texture detailed, green sole signature, luxury retail environment, professional product shot, 4K",
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
        "LV bag rotating slowly, heritage craftsmanship visible, premium quality showcase, luxury product photography, 4K",
    ],
    "gucci": [
        "Gucci accessories with iconic double-G hardware, premium Italian leather, luxury brand aesthetic, fashion editorial photography, clean studio, 4K",
        "Close-up of Gucci GG buckle detail, premium leather texture, luxury craftsmanship, high-end fashion photography, 4K",
        "Gucci belt on luxury display, signature hardware, Italian leather quality visible, fashion magazine style, 4K",
    ],
    "caps": [
        "Premium branded luxury caps, quality embroidery visible, designer accessory photography, clean white background, fashion editorial, 4K",
        "Designer caps rotating slowly, premium materials, fine stitching detail, luxury accessory showcase, 4K",
        "Multiple luxury caps displayed elegantly, brand logos visible, premium construction quality, fashion catalog style, 4K",
    ],
    "lifestyle": [
        "Luxury sneakers on designer coffee table, grey suede and white canvas, lifestyle home interior, warm lighting, fashion magazine spread, 4K",
        "Premium sneakers displayed in minimalist luxury apartment, natural light from window, fashion editorial, European interior, 4K",
        "Parisian woman wearing Chanel sneakers and Dior sunglasses, street style fashion, elegant casual outfit, Parisian café background, fashion editorial, 4K",
    ],
}

# ============================================================================
# CLI COMMANDS
# ============================================================================


def cmd_image(args):
    """Generate product image."""
    print(f"🎨 Generating image: {args.prompt[:60]}...")

    output = generate_image(
        prompt=args.prompt,
        resolution=args.resolution,
        aspect_ratio=args.aspect,
        style=args.style,
    )

    if output:
        print(f"✅ Saved: {output}")
    else:
        print("❌ Generation failed")


def cmd_video(args):
    """Generate video from image or prompt."""
    if args.prompt:
        print(f"🎬 Generating video from prompt...")
        result = text_to_video(
            args.prompt,
            resolution=args.resolution,
            duration=args.duration,
            aspect_ratio=args.aspect,
        )
    elif args.image:
        print(f"📤 Uploading image...")
        import higgsfield_client

        image_url = higgsfield_client.upload_file(args.image)
        if not image_url:
            print("❌ Upload failed")
            return

        print(f"🎬 Generating video...")
        result = image_to_video(
            image_url,
            args.motion_prompt or "",
            resolution=args.resolution,
            duration=args.duration,
        )
    else:
        print("❌ Provide --prompt or --image")
        return

    if result.get("success"):
        video_id = result["video_id"]
        print(f"  Video ID: {video_id}")
        print(f"  Credits: {result.get('credits_used', 'N/A')}")

        status = wait_for_video(video_id)
        output = args.output or f"nano_video_{datetime.now().strftime('%H%M%S')}.mp4"
        download_video(status["video_url"], output)
        print(f"✅ Saved: {output}")
    else:
        print(f"❌ Error: {result.get('error')}")


def cmd_batch(args):
    """Batch generate images or videos."""
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
            try:
                result = generate_image(
                    prompt,
                    resolution=args.resolution,
                    aspect_ratio=args.aspect,
                    style=args.style,
                )
                if result:
                    results.append(
                        {"prompt": prompt, "status": "success", "output": result}
                    )
                else:
                    results.append({"prompt": prompt, "status": "failed"})
            except Exception as e:
                results.append({"prompt": prompt, "status": "failed", "error": str(e)})
        else:
            output = output_dir / f"video_{i + 1:03d}.mp4"
            try:
                result = text_to_video(
                    prompt,
                    resolution=args.resolution,
                    duration=args.duration,
                    aspect_ratio=args.aspect,
                )
                if result.get("success"):
                    video_id = result["video_id"]
                    status = wait_for_video(video_id)
                    download_video(status["video_url"], str(output))
                    results.append(
                        {"prompt": prompt, "status": "success", "output": str(output)}
                    )
                else:
                    results.append(
                        {
                            "prompt": prompt,
                            "status": "failed",
                            "error": result.get("error"),
                        }
                    )
            except Exception as e:
                results.append({"prompt": prompt, "status": "failed", "error": str(e)})

        if i < len(prompts) - 1:
            time.sleep(args.delay)

    results_file = output_dir / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📊 Results saved: {results_file}")


def cmd_generate_category(args):
    """Generate images for a specific category."""
    prompts = BEN2LUXE_IMAGE_PROMPTS.get(args.category, [])
    if not prompts:
        print(f"❌ Unknown category: {args.category}")
        return

    output_dir = Path(args.output_dir) / args.category
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Generating {len(prompts)} images for {args.category}...")

    results = []
    for i, prompt in enumerate(prompts[: args.count]):
        output = output_dir / f"{args.category}_{i + 1}.png"
        try:
            result = generate_image(
                prompt,
                resolution=args.resolution,
                aspect_ratio=args.aspect,
                style=args.style,
            )
            if result:
                results.append({"prompt": prompt, "status": "success"})
            else:
                results.append({"prompt": prompt, "status": "failed"})
        except Exception as e:
            results.append({"prompt": prompt, "status": "failed", "error": str(e)})

    print(
        f"✅ Generated {len([r for r in results if r['status'] == 'success'])} images"
    )


def cmd_prompts(args):
    """List available product prompts."""
    print("\n📦 Available Bene2Luxe Product Prompts:")
    print("=" * 50)
    for category, prompts in BEN2LUXE_IMAGE_PROMPTS.items():
        print(f"\n🎯 {category}:")
        for p in prompts:
            print(f"   • {p[:70]}...")


# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Bene2Luxe × Nano Banano Pro Generator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Image
    img = subparsers.add_parser("image", help="Generate product image")
    img.add_argument("--prompt", "-p", required=True, help="Image prompt")
    img.add_argument("--output", "-o", help="Output file")
    img.add_argument("--resolution", "-r", default="4K", choices=["1K", "2K", "4K"])
    img.add_argument("--aspect", "-a", default="9:16", choices=["1:1", "9:16", "16:9"])
    img.add_argument(
        "--style",
        "-s",
        default="luxury_product",
        choices=["luxury_product", "lifestyle", "mascott"],
    )

    # Video
    vid = subparsers.add_parser("video", help="Generate video")
    vid.add_argument("--prompt", "-p", help="Text prompt")
    vid.add_argument("--image", "-i", help="Input image")
    vid.add_argument(
        "--motion-prompt", "-m", default="", help="Motion description for i2v"
    )
    vid.add_argument("--output", "-o", help="Output file")
    vid.add_argument(
        "--resolution", "-r", default="1080p", choices=["480p", "720p", "1080p"]
    )
    vid.add_argument("--duration", "-d", type=int, default=5, help="Duration (3-12s)")

    # Batch
    batch = subparsers.add_parser("batch", help="Batch generate")
    batch.add_argument("--file", "-f", required=True, help="Prompts file")
    batch.add_argument("--type", "-t", default="image", choices=["image", "video"])
    batch.add_argument(
        "--output-dir", "-o", default="./nano_output", help="Output directory"
    )
    batch.add_argument("--resolution", "-r", default="4K" if "image" else "1080p")
    batch.add_argument(
        "--duration", "-d", type=int, default=5, help="Duration (video only)"
    )
    batch.add_argument("--aspect", "-a", default="9:16")
    batch.add_argument("--style", "-s", default="luxury_product")
    batch.add_argument("--delay", type=int, default=35, help="Delay between requests")

    # Category
    cat = subparsers.add_parser("category", help="Generate for category")
    cat.add_argument(
        "--category", "-c", required=True, choices=list(BEN2LUXE_IMAGE_PROMPTS.keys())
    )
    cat.add_argument("--count", type=int, default=3)
    cat.add_argument("--output-dir", "-o", default="./nano_output")
    cat.add_argument("--resolution", "-r", default="4K")
    cat.add_argument("--aspect", "-a", default="9:16")

    # List prompts
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
    elif args.command == "category":
        cmd_generate_category(args)
    elif args.command == "prompts":
        cmd_prompts(args)


if __name__ == "__main__":
    main()
