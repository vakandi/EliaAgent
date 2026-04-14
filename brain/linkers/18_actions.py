#!/usr/bin/env python3
"""
Linker 18: Actions & Operations
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Edit": ("../../wiki/concepts/File-Management", "Edit"),
    "Create": ("../../wiki/concepts/File-Management", "Create"),
    "Delete": ("../../wiki/concepts/File-Management", "Delete"),
    "Download": ("../../wiki/concepts/File-Management", "Download"),
    "Upload": ("../../wiki/concepts/File-Management", "Upload"),
    "Send": ("../../wiki/channels/Telegram", "Send"),
    "Read": ("../../wiki/concepts/File-Management", "Read"),
    "Find": ("../../wiki/concepts/Search", "Find"),
    "List": ("../../wiki/concepts/Search", "List"),
    "Add": ("../../wiki/concepts/File-Management", "Add"),
    "Remove": ("../../wiki/concepts/File-Management", "Remove"),
    "Update": ("../../wiki/concepts/File-Management", "Update"),
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
    print(f"18-Actions: {total} links added")
