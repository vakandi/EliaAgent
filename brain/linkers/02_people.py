#!/usr/bin/env python3
"""
Linker 02: People
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Wael": ("wiki/people/Wael", "Wael"),
    "Thomas": ("wiki/people/Thomas-Cogne", "Thomas"),
    "Thomas-Cogne": ("wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("wiki/people/Ali", "Ali"),
    "Rida": ("wiki/people/Rida", "Rida"),
    "Elia": ("wiki/people/Elia", "Elia"),
    "Bousfira": ("wiki/people/Wael", "Bousfira"),
    "Ronen": ("wiki/people/Ronen", "Ronen"),
    "Marco": ("wiki/people/Marco", "Marco"),
    "Anass": ("wiki/people/Anass", "Anass"),
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
    print(f"02-People: {total} links added")
