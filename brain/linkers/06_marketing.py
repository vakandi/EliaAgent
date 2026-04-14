#!/usr/bin/env python3
"""
Linker 06: Content & Marketing
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "UGC": ("wiki/concepts/UGC", "UGC"),
    "Mascoot": ("wiki/skills/Higgsfield-Video", "Mascoot"),
    "Higgsfield": ("wiki/skills/Higgsfield-Video", "Higgsfield"),
    "TikTok": ("wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "Ads": ("wiki/concepts/Ads-Funnel", "Ads"),
    "Facebook": ("wiki/channels/Facebook", "Facebook"),
    "Instagram": ("wiki/channels/Instagram", "Instagram"),
    "Content": ("wiki/concepts/Marketing-Concepts", "Content"),
    "Marketing": ("wiki/concepts/Marketing-Concepts", "Marketing"),
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
    print(f"06-Marketing: {total} links added")
