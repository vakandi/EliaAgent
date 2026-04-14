#!/usr/bin/env python3
"""
Linker 15: Content & Video
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Video": ("../../wiki/skills/Higgsfield-Video", "Video"),
    "Content": ("../../wiki/concepts/Marketing-Concepts", "Content"),
    "Mascoot": ("../../wiki/skills/Higgsfield-Video", "Mascoot"),
    "UGC": ("../../wiki/concepts/UGC", "UGC"),
    "Ads": ("../../wiki/concepts/Ads-Funnel", "Ads"),
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
    print(f"15-Content: {total} links added")
