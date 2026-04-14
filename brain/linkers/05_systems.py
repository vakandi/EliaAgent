#!/usr/bin/env python3
"""
Linker 05: Systems & Infrastructure
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Docker": ("../../wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("../../wiki/systems/SSH-Servers", "SSH"),
    "Jira": ("../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../wiki/tools/MCP-Tools", "MCP"),
    "FastMCP": ("../../wiki/tools/MCP-Tools", "FastMCP"),
    "MCP-GO": ("../../wiki/tools/MCP-Tools", "MCP-GO"),
    "MultiSaasDeploy": ("../../wiki/systems/MultiSaasDeploy", "MultiSaasDeploy"),
    "IONOS": ("../../wiki/systems/IONOS", "IONOS"),
    "Host": ("../../wiki/systems/Docker-Servers", "Host"),
    "Server": ("../../wiki/systems/Docker-Servers", "Server"),
    "Cloud": ("../../wiki/systems/Docker-Servers", "Cloud"),
    "Chrome": ("../../wiki/skills/Chrome-Automation", "Chrome"),
    "Playwright": ("../../wiki/skills/Playwright", "Playwright"),
    "GPU": ("../../wiki/systems/Docker-Servers", "GPU"),
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
    print(f"05-Systems: {total} links added")
