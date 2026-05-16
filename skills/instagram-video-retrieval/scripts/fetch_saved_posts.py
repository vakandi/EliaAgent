#!/usr/bin/env python3
"""
Instagram Saved Posts Fetcher
Uses Instagram's private API to fetch saved posts with video URLs
"""

import json
import sys
import argparse
import requests
from pathlib import Path


DEFAULT_HEADERS = {
    "x-ig-app-id": "936619743392459",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
}


def fetch_saved_posts(cookies: str, max_id: str = None) -> dict:
    """
    Fetch saved posts from Instagram API

    Args:
        cookies: Cookie string (sessionid=xxx; csrftoken=yyy; ds_user_id=zzz)
        max_id: Pagination cursor (None for first page)

    Returns:
        API response JSON
    """
    headers = DEFAULT_HEADERS.copy()
    headers["cookie"] = cookies

    url = "https://www.instagram.com/api/v1/feed/saved/posts/"
    if max_id:
        url += f"?max_id={max_id}"

    print(f"Fetching: {url}")

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 429:
        print("⚠️  Rate limited. Wait 60+ seconds and retry.")
        return None
    elif response.status_code != 200:
        print(f"⚠️  Error {response.status_code}: {response.text[:200]}")
        return None

    return response.json()


def extract_video_posts(data: dict) -> list:
    """
    Extract video posts from API response

    Args:
        data: API response JSON

    Returns:
        List of video post objects
    """
    videos = []

    items = data.get("items", [])
    print(f"Found {len(items)} items in response")

    for item in items:
        media = item.get("media", {})
        media_type = media.get("media_type")

        # Only process videos (type 2)
        if media_type != 2:
            continue

        # Extract basic info
        video_info = {
            "post_id": media.get("pk"),
            "shortcode": media.get("code"),
            "url": f"https://www.instagram.com/p/{media.get('code')}/",
            "media_type": media_type,
            "username": media.get("user", {}).get("username"),
            "full_name": media.get("user", {}).get("full_name"),
            "profile_pic": media.get("user", {}).get("profile_pic_url"),
            "is_verified": media.get("user", {}).get("is_verified"),
        }

        # Extract caption
        caption = media.get("caption", {})
        video_info["caption"] = caption.get("text", "")
        video_info["caption_created_at"] = caption.get("created_at")

        # Extract hashtags and mentions
        video_info["hashtags"] = [
            tag["name"] for tag in media.get("usertags", {}).get("in", [])
        ]

        # Extract engagement
        video_info["like_count"] = media.get("like_count", 0)
        video_info["comment_count"] = media.get("comment_count", 0)

        # Extract video URLs
        video_versions = media.get("video_versions", [])
        if video_versions:
            # Sort by quality (width descending)
            video_versions.sort(key=lambda x: x.get("width", 0), reverse=True)
            video_info["video_url"] = video_versions[0].get("url")
            video_info["video_duration"] = media.get("video_duration", 0)

        # Extract thumbnail
        image_versions = media.get("image_versions2", {}).get("candidates", [])
        if image_versions:
            video_info["thumbnail_url"] = image_versions[0].get("url")

        # Extract timestamp
        video_info["taken_at"] = media.get("taken_at")

        videos.append(video_info)
        print(f"  📹 Video: @{video_info['username']} - {video_info['url']}")

    return videos


def save_results(videos: list, output_file: str):
    """Save results to JSON file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(videos)} videos to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Fetch Instagram saved posts via API")
    parser.add_argument(
        "--cookies", "-c", required=True, help="Cookie string from Instagram"
    )
    parser.add_argument("--max-id", "-m", help="Pagination cursor (optional)")
    parser.add_argument(
        "--output", "-o", default="saved_videos.json", help="Output file"
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only extract, no follow-up pagination",
    )

    args = parser.parse_args()

    all_videos = []
    max_id = args.max_id

    # Fetch first page
    data = fetch_saved_posts(args.cookies, max_id)
    if not data:
        print("❌ Failed to fetch posts")
        sys.exit(1)

    videos = extract_video_posts(data)
    all_videos.extend(videos)

    # Check for more pages
    if not args.extract_only:
        next_max_id = data.get("next_max_id")
        page_count = 1

        while next_max_id and page_count < 10:  # Limit to 10 pages
            print(f"\n📄 Fetching page {page_count + 1}...")
            import time

            time.sleep(2)  # Rate limit protection

            data = fetch_saved_posts(args.cookies, next_max_id)
            if not data:
                break

            videos = extract_video_posts(data)
            all_videos.extend(videos)

            next_max_id = data.get("next_max_id")
            page_count += 1

    save_results(all_videos, args.output)

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for i, v in enumerate(all_videos, 1):
        caption_preview = (
            v["caption"][:50] + "..." if len(v["caption"]) > 50 else v["caption"]
        )
        print(f"{i}. @{v['username']}")
        print(f"   {v['url']}")
        print(f"   📝 {caption_preview}")
        print(f"   ❤️ {v['like_count']} | 💬 {v['comment_count']}")
        print()


if __name__ == "__main__":
    main()
