#!/usr/bin/env python3
"""
Linker 03: Channels
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "WhatsApp": ("wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Telegram": ("wiki/channels/Telegram", "Telegram"),
    "Discord": ("wiki/channels/Discord-EliaWorkSpace", "Discord"),
    "WhatsApp-B2LUXE": ("wiki/channels/WhatsApp-B2LUXE", "WhatsApp B2LUXE"),
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
    print(f"03-Channels: {total} links added")
