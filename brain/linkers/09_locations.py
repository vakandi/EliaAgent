#!/usr/bin/env python3
"""
Linker 09: Locations
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Paris": ("wiki/concepts/Location-Targeting#paris", "Paris"),
    "France": ("wiki/concepts/Location-Targeting#france", "France"),
    "Switzerland": ("wiki/concepts/Location-Targeting#switzerland", "Switzerland"),
    "Haute Savoie": ("wiki/concepts/Location-Targeting#haute-savoie", "Haute Savoie"),
    "Valleiry": ("wiki/concepts/Location-Targeting#valleiry", "Valleiry"),
    "Geneva": ("wiki/concepts/Location-Targeting#geneva", "Geneva"),
    "Zurich": ("wiki/concepts/Location-Targeting#zurich", "Zurich"),
    "Lyon": ("wiki/concepts/Location-Targeting#lyon", "Lyon"),
    "Marseille": ("wiki/concepts/Location-Targeting#marseille", "Marseille"),
    "European": ("wiki/concepts/Location-Targeting#europe", "European"),
    "Europe": ("wiki/concepts/Location-Targeting#europe", "Europe"),
    "EU": ("wiki/concepts/Location-Targeting#europe", "EU"),
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
    print(f"09-Locations: {total} links added")
