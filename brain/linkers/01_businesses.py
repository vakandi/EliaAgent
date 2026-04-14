#!/usr/bin/env python3
"""
Linker 01: Businesses
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Bene2Luxe": ("wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "B2LUXE BUSINESS": ("wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "B2LUXE-BUSINESS": ("wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "ZovaBoost": ("wiki/businesses/ZovaBoost", "ZovaBoost"),
    "OGBoujee": ("wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("wiki/businesses/Netfluxe", "Netfluxe"),
    "CoBou Agency": ("wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "CoBou-Agency": ("wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "TikTok": ("wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "SurfAI": ("wiki/businesses/SurfAI", "SurfAI"),
    "Account Verification": (
        "wiki/businesses/Account-Verification",
        "Account Verification",
    ),
}


def link_file(path):
    content = path.read_text()
    count = 0
    for word, (target, display) in LINKS.items():
        if f"[[{target}" not in content and f"|{word}]]" not in content:
            pattern = re.compile(rf"\b{re.escape(word)}\b")
            new, n = pattern.subn(f"[[{target}|{display}]]", content)
            if n:
                content = new
                count += n
    if count:
        path.write_text(content)
    return count


if __name__ == "__main__":
    base = Path("/Users/vakandi/EliaAI/docs")
    total = sum(link_file(f) for f in base.glob("**/*.md"))
    print(f"01-Businesses: {total} links added")
