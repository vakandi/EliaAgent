#!/usr/bin/env python3
"""
Linker 08: Coding & Development
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Python": ("../../wiki/skills/Python-Scripting", "Python"),
    "JSON": ("../../wiki/concepts/API-Integration", "JSON"),
    "API": ("../../wiki/concepts/API-Integration", "API"),
    "GitHub": ("../../wiki/skills/Git-Version-Control", "GitHub"),
    "Git": ("../../wiki/skills/Git-Version-Control", "Git"),
    "HTML": ("../../wiki/skills/Web-Development", "HTML"),
    "Markdown": ("../../wiki/concepts/Documentation", "Markdown"),
    "Figma": ("../../wiki/skills/Design-Tools", "Figma"),
    "Framework": ("../../wiki/skills/Web-Development", "Framework"),
    "Library": ("../../wiki/skills/Python-Scripting", "Library"),
    "File": ("../../wiki/concepts/File-Management", "File"),
    "URL": ("../../wiki/concepts/API-Integration", "URL"),
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
    print(f"08-Coding: {total} links added")
