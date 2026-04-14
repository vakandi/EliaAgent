#!/usr/bin/env python3
"""
Linker 12: Status & Monitoring
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Status": ("../../wiki/topics/Infrastructure-Timeline", "Status"),
    "INFO": ("../../wiki/topics/Infrastructure-Timeline", "INFO"),
    "Check": ("../../wiki/topics/Infrastructure-Timeline", "Check"),
    "Checking": ("../../wiki/topics/Infrastructure-Timeline", "Checking"),
    "Error": ("../../wiki/topics/Infrastructure-Timeline", "Error"),
    "ValueError": ("../../wiki/topics/Infrastructure-Timeline", "ValueError"),
    "Trace": ("../../wiki/topics/Infrastructure-Timeline", "Trace"),
    "OTLPExporterError": (
        "../../wiki/topics/Infrastructure-Timeline",
        "OTLPExporterError",
    ),
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
    print(f"12-Monitoring: {total} links added")
