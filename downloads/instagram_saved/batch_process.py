#!/usr/bin/env python3
import json
import subprocess
import time
import os
from pathlib import Path

BASE_DIR = Path("/Users/vakandi/EliaAI/instagram_saved")
VIDEOS_DIR = BASE_DIR / "videos"
METADATA_DIR = BASE_DIR / "metadata"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

VIDEOS_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

with open(BASE_DIR / "all_post_ids.json") as f:
    post_ids = json.load(f)

FOOD_KEYWORDS = [
    "recipe",
    "food",
    "cooking",
    "meal",
    "dinner",
    "lunch",
    "breakfast",
    "cuisine",
    "ingredient",
    "chef",
    "baking",
    "cook",
    "tasty",
    "yummy",
    "nouilles",
    "salad",
    "chocolate",
    "dessert",
    "cake",
    "poulet",
    "riz",
]

BUSINESS_KEYWORDS = [
    "sales",
    "marketing",
    "business",
    "startup",
    "ai",
    "tech",
    "coding",
    "entrepreneurship",
    "saas",
    "app",
    "developer",
    "github",
    "automation",
    "productivity",
    "growth",
    "strategy",
    "negotiation",
    "investment",
]


def get_metadata(post_id):
    output_file = METADATA_DIR / f"{post_id}.json"
    if output_file.exists():
        with open(output_file) as f:
            return json.load(f)

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                f"https://www.instagram.com/p/{post_id}/",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            metadata = {
                "post_id": post_id,
                "url": f"https://www.instagram.com/p/{post_id}/",
                "username": data.get("uploader") or data.get("uploader_id", "unknown"),
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "duration": data.get("duration", 0),
                "like_count": "N/A",
                "comment_count": "N/A",
                "is_video": data.get("duration", 0) > 0
                if data.get("duration")
                else False,
            }
            with open(output_file, "w") as f:
                json.dump(metadata, f)
            return metadata
    except Exception as e:
        print(f"Error getting metadata for {post_id}: {e}")
    return None


def is_business(metadata):
    if not metadata or not metadata.get("is_video"):
        return False
    desc = (metadata.get("description", "") + " " + metadata.get("title", "")).lower()
    for kw in FOOD_KEYWORDS:
        if kw.lower() in desc:
            return False
    for kw in BUSINESS_KEYWORDS:
        if kw.lower() in desc:
            return True
    return len(desc) > 50


def download_video(post_id):
    output_file = VIDEOS_DIR / f"{post_id}.mp4"
    if output_file.exists():
        return True
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "-o",
                str(output_file),
                f"https://www.instagram.com/p/{post_id}/",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return output_file.exists()
    except Exception as e:
        print(f"Error downloading {post_id}: {e}")
        return False


def transcribe_video(post_id):
    video_file = VIDEOS_DIR / f"{post_id}.mp4"
    transcript_file = TRANSCRIPTS_DIR / f"{post_id}.txt"
    if transcript_file.exists():
        return True
    if not video_file.exists():
        return False
    try:
        result = subprocess.run(
            [
                "whisper",
                str(video_file),
                "--model",
                "large-v3",
                "--task",
                "transcribe",
                "--output_dir",
                str(TRANSCRIPTS_DIR),
                "--verbose",
                "False",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        return transcript_file.exists()
    except Exception as e:
        print(f"Error transcribing {post_id}: {e}")
        return False


def main():
    print(f"Total posts: {len(post_ids)}")
    business_videos = []

    print("\n=== Phase 1: Getting metadata ===")
    for i, post_id in enumerate(post_ids):
        if i % 20 == 0:
            print(f"Progress: {i}/{len(post_ids)}")
        metadata = get_metadata(post_id)
        if metadata and is_business(metadata):
            business_videos.append(metadata)
            print(f"  ✅ BUSINESS: {post_id} - @{metadata['username']}")
        time.sleep(0.3)

    print(f"\n=== Found {len(business_videos)} business videos ===")

    with open(BASE_DIR / "business_videos.json", "w") as f:
        json.dump(business_videos, f, indent=2)

    print("\n=== Phase 2: Downloading videos ===")
    for i, video in enumerate(business_videos):
        post_id = video["post_id"]
        print(f"Downloading {i + 1}/{len(business_videos)}: {post_id}")
        if download_video(post_id):
            print(f"  ✅ Downloaded: {post_id}")
        else:
            print(f"  ❌ Failed: {post_id}")
        time.sleep(1)

    print("\n=== Phase 3: Transcribing ===")
    for i, video in enumerate(business_videos):
        post_id = video["post_id"]
        print(f"Transcribing {i + 1}/{len(business_videos)}: {post_id}")
        if transcribe_video(post_id):
            print(f"  ✅ Transcribed: {post_id}")
        else:
            print(f"  ❌ Failed: {post_id}")
        time.sleep(1)

    print("\n=== Done! ===")
    print(f"Business videos: {len(business_videos)}")


if __name__ == "__main__":
    main()
