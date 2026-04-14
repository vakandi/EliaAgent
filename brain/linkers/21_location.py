#!/usr/bin/env python3
"""
Linker 21: Locations
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""
import re
from pathlib import Path

LINKS = {
    "Paris": ("../../wiki/concepts/Location-Targeting#paris", "Paris"),
    "France": ("../../wiki/concepts/Location-Targeting#france", "France"),
    "European": ("../../wiki/concepts/Location-Targeting#europe", "European"),
}

def link_file(path):
    content = path.read_text(encoding='utf-8', errors='ignore')
    count = 0
    for word, (target, display) in LINKS.items():
        if f"[[{target}" not in content and f"|{word}]]" not in content:
            pattern = re.compile(rf'\b{re.escape(word)}\b')
            new, n = pattern.subn(f"[[{target}|{display}]]", content, count=1)
            if n:
                content = new
                count += n
    if count:
        path.write_text(content, encoding='utf-8')
    return count

if __name__ == "__main__":
    base = Path("/Users/vakandi/EliaAI/brain/raw")
    total = sum(link_file(f) for f in base.glob("**/*.md"))
    print(f"21-Location: {total} links added")
