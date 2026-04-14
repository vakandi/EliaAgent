#!/usr/bin/env python3
"""
Linker 16: Marketing & Growth
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Cascade": ("../../wiki/concepts/Cascade-Framework", "Cascade"),
    "CTA": ("../../wiki/concepts/Ads-Funnel#cta", "CTA"),
    "Hook": ("../../wiki/concepts/Ads-Funnel#hook", "Hook"),
    "Target": ("../../wiki/concepts/Ads-Funnel#targeting", "Target"),
    "Value": ("../../wiki/concepts/Pricing", "Value"),
    "Marketing": ("../../wiki/concepts/Marketing-Concepts", "Marketing"),
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
    print(f"16-Marketing: {total} links added")
