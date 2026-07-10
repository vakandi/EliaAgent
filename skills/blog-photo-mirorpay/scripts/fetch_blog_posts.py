#!/usr/bin/env python3
"""Fetch YourApp blog posts from Directus.

Usage:
    python3 scripts/fetch_blog_posts.py                            # list posts without images
    python3 scripts/fetch_blog_posts.py --all                      # list ALL published posts
    python3 scripts/fetch_blog_posts.py --slug my-post-slug        # get a specific post (basic)
    python3 scripts/fetch_blog_posts.py --slug my-post-slug --full # get post WITH full content
    python3 scripts/fetch_blog_posts.py --full                     # list ALL posts with full content

Output: JSON array with fields: id, title, slug, description, published_at, has_image
Use --full to also include the full rich-text 'content' field.
"""

import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

DIRECTUS_URL = os.environ.get("DIRECTUS_URL", "https://dash.[your-app].com")
ADMIN_TOKEN = os.environ.get(
    "DIRECTUS_ADMIN_TOKEN",
    "sp-admin-token-2026-190c1875aec049db",
)


def api_get(path: str) -> dict:
    url = f"{DIRECTUS_URL}/items/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ADMIN_TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code} for {url}: {body}", file=sys.stderr)
        sys.exit(1)


def main():
    show_all = "--all" in sys.argv
    with_full = "--full" in sys.argv
    specific_slug = None
    for arg in sys.argv[1:]:
        if arg.startswith("--slug="):
            specific_slug = arg.split("=", 1)[1]
        elif arg.startswith("--slug"):
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                specific_slug = sys.argv[idx + 1]

    # Build filter
    filter_parts = ['{"status":{"_eq":"published"}}']
    if not show_all and not specific_slug:
        filter_parts.append('{"image":{"_null":true}}')

    if specific_slug:
        filter_parts.append(f'{{"slug":{{"_eq":"{specific_slug}"}}}}')

    filter_json = (
        '{"_and":['
        + ",".join(filter_parts)
        + "]}"
    )

    fields = "id,title,slug,description,published_at,image"
    if with_full:
        fields += ",content"

    params = (
        f"filter={urllib.parse.quote(filter_json)}"
        f"&sort=-published_at"
        f"&fields={urllib.parse.quote(fields)}"
        f"&limit=50"
    )

    data = api_get(f"posts?{params}")
    posts = data.get("data", [])

    if not posts:
        print("No blog posts found matching the criteria.")
        sys.exit(0)

    # Extract relevant info
    result = []
    for p in posts:
        has_image = p.get("image") is not None and p.get("image") != ""
        entry = {
            "id": p["id"],
            "title": p.get("title", ""),
            "slug": p.get("slug", ""),
            "description": p.get("description", ""),
            "published_at": p.get("published_at", ""),
            "has_image": has_image,
        }
        if with_full:
            entry["content"] = p.get("content", "")
        result.append(entry)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
