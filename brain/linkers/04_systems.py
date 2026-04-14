#!/usr/bin/env python3
"""
Linker 04: Systems & Infrastructure
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Docker": ("wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("wiki/systems/SSH-Servers", "SSH"),
    "SSL": ("wiki/topics/Infrastructure-Timeline#ssl", "SSL"),
    "HTTPS": ("wiki/topics/Infrastructure-Timeline#ssl", "HTTPS"),
    "HTTP": ("wiki/systems/Docker-Servers", "HTTP"),
    "API": ("wiki/skills/MCP-Tools", "API"),
    "MCP": ("wiki/tools/MCP-Tools", "MCP"),
    "Jira": ("wiki/systems/Jira-Tickets-Index", "Jira"),
    "IONOS": ("wiki/systems/IONOS", "IONOS"),
    "Hosting": ("wiki/systems/IONOS", "Hosting"),
    "Certbot": ("wiki/systems/Docker-Servers#certbot", "Certbot"),
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
    print(f"04-Systems: {total} links added")
