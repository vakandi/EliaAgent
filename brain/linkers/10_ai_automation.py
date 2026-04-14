#!/usr/bin/env python3
"""
Linker 10: AI & Automation
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "AI": ("wiki/concepts/AI-Automation", "AI"),
    "Elia": ("wiki/people/Elia", "Elia"),
    "EliaAI": ("wiki/people/Elia", "Elia"),
    "Automation": ("wiki/concepts/AI-Automation", "Automation"),
    "Agent": ("wiki/concepts/AI-Automation#agents", "Agent"),
    "Agents": ("wiki/concepts/AI-Automation#agents", "Agents"),
    "Workflow": ("wiki/concepts/AI-Automation#workflows", "Workflow"),
    "Pipeline": ("wiki/concepts/AI-Automation#pipelines", "Pipeline"),
    "Task": ("wiki/concepts/AI-Automation#tasks", "Task"),
    "Tasks": ("wiki/concepts/AI-Automation#tasks", "Tasks"),
    "Session": ("wiki/docs/Sessions", "Session"),
    "Sessions": ("wiki/docs/Sessions", "Sessions"),
    "Cron": ("wiki/skills/Cron-Scheduling", "Cron"),
    "Scheduled": ("wiki/skills/Cron-Scheduling", "Scheduled"),
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
    print(f"10-AI-Automation: {total} links added")
