#!/usr/bin/env python3
"""
Linker 14: Polar & Tools
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Polar": ("../../wiki/skills/Polar-SCM", "Polar"),
    "Versions": ("../../wiki/skills/Git-Version-Control", "Versions"),
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
    print(f"14-Polar: {total} links added")
