#!/usr/bin/env python3
"""
Instagram Saved Posts Fetcher - Uses Private API
Extracts all saved posts with metadata
"""

import json
import time
import requests
import argparse
from pathlib import Path

# Default headers for Instagram API
HEADERS = {
    "x-ig-app-id": "936619743392459",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}


def fetch_saved_posts(cookies: str, max_id: str = None, cursor: str = None) -> dict:
    """Fetch saved posts from Instagram API"""
    headers = HEADERS.copy()
    headers["cookie"] = cookies

    url = "https://www.instagram.com/api/v1/feed/saved/posts/"
    params = {}
    if max_id:
        params["max_id"] = max_id
    if cursor:
        params["cursor"] = cursor

    print(f"Fetching: {url} (max_id={max_id}, cursor={cursor})")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 429:
            print("⚠️ Rate limited!")
            return None
        elif response.status_code != 200:
            print(f"⚠️ Error: {response.text[:200]}")
            return None

        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def extract_videos(posts: list) -> list:
    """Extract video posts with full metadata"""
    videos = []

    for post in posts:
        media = post.get("media", {})

        # Check if it's a video (media_type = 2)
        if media.get("media_type") != 2:
            continue

        video_data = {
            "post_id": media.get("pk"),
            "shortcode": media.get("code"),
            "url": f"https://www.instagram.com/p/{media.get('code')}/",
            "reel_url": f"https://www.instagram.com/reel/{media.get('code')}/",
            "username": media.get("user", {}).get("username"),
            "full_name": media.get("user", {}).get("full_name"),
            "profile_pic": media.get("user", {}).get("profile_pic_url"),
            "is_verified": media.get("user", {}).get("is_verified"),
            "caption": media.get("caption", {}).get("text", ""),
            "like_count": media.get("like_count", 0),
            "comment_count": media.get("comment_count", 0),
            "taken_at": media.get("taken_at"),
            "video_url": None,
            "video_duration": media.get("video_duration", 0),
            "thumbnail_url": None,
        }

        # Get video URL
        video_versions = media.get("video_versions", [])
        if video_versions:
            video_versions.sort(key=lambda x: x.get("width", 0), reverse=True)
            video_data["video_url"] = video_versions[0].get("url")

        # Get thumbnail
        images = media.get("image_versions2", {}).get("candidates", [])
        if images:
            video_data["thumbnail_url"] = images[0].get("url")

        videos.append(video_data)

    return videos


def save_results(videos: list, output_file: str):
    """Save results to JSON"""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(videos)} videos to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Fetch Instagram saved posts")
    parser.add_argument(
        "--cookies", "-c", required=True, help="Cookie string from Instagram"
    )
    parser.add_argument(
        "--output", "-o", default="saved_videos.json", help="Output file"
    )
    parser.add_argument(
        "--pages", "-p", type=int, default=50, help="Max pages to fetch"
    )

    args = parser.parse_args()

    all_videos = []
    max_id = None
    page = 0

    while page < args.pages:
        print(f"\n📄 Page {page + 1}...")

        data = fetch_saved_posts(args.cookies, max_id)
        if not data:
            break

        videos = extract_videos(data.get("items", []))
        all_videos.extend(videos)

        print(f"   Found {len(videos)} videos (total: {len(all_videos)})")

        # Pagination
        max_id = data.get("next_max_id")
        if not max_id:
            break

        page += 1
        time.sleep(2)  # Rate limit protection

    save_results(all_videos, args.output)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total videos: {len(all_videos)}")
    print(f"Last video: {all_videos[-1]['url'] if all_videos else 'N/A'}")


if __name__ == "__main__":
    main()
