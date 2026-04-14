#!/usr/bin/env python3
"""
Linker 01: IDE & Development Tools
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Cursor": ("../../wiki/skills/Cursor-IDE", "Cursor"),
    "Windsurf": ("../../wiki/skills/Windsurf-IDE", "Windsurf"),
    "OpenCode": ("../../wiki/skills/OpenCode-CLI", "OpenCode"),
    "IDE": ("../../wiki/skills/Cursor-IDE", "IDE"),
    "Plugin": ("../../wiki/skills/Cursor-IDE", "Plugin"),
    "Extension": ("../../wiki/skills/Cursor-IDE", "Extension"),
    "MacOS": ("../../wiki/topics/Infrastructure-Timeline", "MacOS"),
    "Electron": ("../../wiki/skills/Cursor-IDE", "Electron"),
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
    print(f"01-IDE: {total} links added")
