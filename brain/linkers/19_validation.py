#!/usr/bin/env python3
"""
Linker 19: Validation & Types
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""
import re
from pathlib import Path

LINKS = {
    "Validate": ("../../wiki/skills/TypeScript-Development", "Validate"),
    "Filter": ("../../wiki/concepts/Search", "Filter"),
    "SELECT": ("../../wiki/concepts/Database", "SELECT"),
    "Optional": ("../../wiki/skills/TypeScript-Development", "Optional"),
    "Returns": ("../../wiki/concepts/API-Integration", "Returns"),
    "Exact": ("../../wiki/concepts/Search", "Exact"),
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
    print(f"19-Validation: {total} links added")
