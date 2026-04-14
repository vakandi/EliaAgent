#!/usr/bin/env python3
"""
Linker 06: AI & Models
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "AI": ("../../wiki/concepts/AI-Automation", "AI"),
    "Elia": ("../../wiki/people/Elia", "Elia"),
    "EliaAI": ("../../wiki/people/Elia", "Elia"),
    "Claude": ("../../wiki/people/Claude", "Claude"),
    "OpenAI": ("../../wiki/people/OpenAI", "OpenAI"),
    "GPT": ("../../wiki/people/GPT", "GPT"),
    "Gemini": ("../../wiki/people/Gemini", "Gemini"),
    "Anthropic": ("../../wiki/people/Anthropic", "Anthropic"),
    "Agent": ("../../wiki/concepts/AI-Automation", "Agent"),
    "Agents": ("../../wiki/concepts/AI-Automation", "Agents"),
    "IA": ("../../wiki/concepts/AI-Automation", "IA"),
    "Bot": ("../../wiki/concepts/AI-Automation", "Bot"),
    "WatsonHelper": ("../../wiki/skills/MCP-Tools", "WatsonHelper"),
    "AITeamHelper": ("../../wiki/concepts/AI-Automation", "AITeamHelper"),
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
    print(f"06-AI: {total} links added")
