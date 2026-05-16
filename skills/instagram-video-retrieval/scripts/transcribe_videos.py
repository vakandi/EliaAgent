#!/usr/bin/env python3
"""
Instagram Video Transcriber
Downloads videos and transcribes using Whisper
"""

import json
import sys
import argparse
import subprocess
import requests
from pathlib import Path


def download_video(video_url: str, output_path: str) -> bool:
    """Download video using yt-dlp"""
    cmd = ["yt-dlp", "-o", output_path, "--no-playlist", "--quiet", video_url]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def transcribe_video(
    video_path: str, model: str = "large-v3", language: str = "French"
) -> str:
    """Transcribe video using Whisper"""
    cmd = [
        "whisper",
        video_path,
        "--model",
        model,
        "--language",
        language,
        "--task",
        "transcribe",
        "--verbose",
        "False",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout + result.stderr
    else:
        print(f"Whisper error: {result.stderr}")
        return None


def process_videos(
    input_file: str, output_dir: str, model: str = "large-v3", language: str = "French"
):
    """Process videos from JSON file"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        videos = json.load(f)

    results = []

    for i, video in enumerate(videos, 1):
        print(f"\n{'=' * 50}")
        print(f"Processing {i}/{len(videos)}: {video['url']}")
        print(f"Username: @{video['username']}")
        print(f"Caption: {video['caption'][:100]}...")

        video_path = Path(output_dir) / f"{video['shortcode']}.mp4"
        transcript_path = Path(output_dir) / f"{video['shortcode']}.txt"

        # Check if already transcribed
        if transcript_path.exists():
            print("⏭️  Already transcribed, skipping")
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
        else:
            # Download video
            print("📥 Downloading video...")
            if download_video(video["video_url"], str(video_path)):
                print("✅ Downloaded")

                # Transcribe
                print("🎙️  Transcribing...")
                transcript = transcribe_video(str(video_path), model, language)

                if transcript:
                    print("✅ Transcribed")
                    # Save transcript
                    with open(transcript_path, "w", encoding="utf-8") as f:
                        f.write(transcript)
                else:
                    print("❌ Transcription failed")
                    transcript = "TRANSCRIPTION_FAILED"
            else:
                print("❌ Download failed")
                transcript = "DOWNLOAD_FAILED"

        # Build result
        result = video.copy()
        result["transcript"] = transcript
        result["transcript_file"] = str(transcript_path)
        results.append(result)

        # Save intermediate results
        with open(
            Path(output_dir) / "transcription_results.json", "w", encoding="utf-8"
        ) as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        import time

        time.sleep(1)  # Rate limit

    print(f"\n✅ Completed! Results saved to {output_dir}/transcription_results.json")
    return results


def main():
    parser = argparse.ArgumentParser(description="Transcribe Instagram videos")
    parser.add_argument(
        "--input", "-i", required=True, help="Input JSON from fetch_saved_posts.py"
    )
    parser.add_argument(
        "--output", "-o", default="./transcriptions", help="Output directory"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="large-v3",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size",
    )
    parser.add_argument("--language", "-l", default="French", help="Audio language")

    args = parser.parse_args()

    process_videos(args.input, args.output, args.model, args.language)


if __name__ == "__main__":
    main()
