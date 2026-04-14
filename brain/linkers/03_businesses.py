#!/usr/bin/env python3
"""
Linker 03: Businesses
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Bene2Luxe": ("../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "B2LUXE BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "B2LUXE-BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "ZovaBoost": ("../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "CoBou": ("../../wiki/businesses/CoBou-Agency", "CoBou"),
    "CoBou Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "CoBou-Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "MAYAVANTA": ("../../wiki/businesses/Mayavanta", "MAYAVANTA"),
    "OGBoujee": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "TikTok": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("../../wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "Account Verification": (
        "../../wiki/businesses/Account-Verification",
        "Account Verification",
    ),
    "AccForgeDev": ("../../wiki/businesses/AccForge", "AccForge"),
    "Swissquote": ("../../wiki/businesses/Swissquote", "Swissquote"),
    "LLC": ("../../wiki/businesses/B2LUXE-BUSINESS", "LLC"),
}


def link_file(path):
    content = path.read_text(encoding="utf-8", errors="ignore")
    count = 0
    for word, (target, display) in LINKS.items():
        if f"[[{target}" not in content and f"|{word}]]" not in content:
            pattern = re.compile(rf"\b{re.escape(word)}\b")
            new, n = pattern.subn(f"[[{target}|{display}]]", content, count=1)
            if n:
                content = new
                count += n
    if count:
        path.write_text(content, encoding="utf-8")
    return count


if __name__ == "__main__":
    base = Path("/Users/vakandi/EliaAI/brain/raw")
    total = sum(link_file(f) for f in base.glob("**/*.md"))
    print(f"03-Businesses: {total} links added")
