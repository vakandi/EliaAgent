#!/usr/bin/env python3
"""
Linker 07: Jira Projects & Tracking
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "BEN": ("../../wiki/systems/Jira-Tickets-Index", "BEN"),
    "COBOUAGENC": ("../../wiki/systems/Jira-Tickets-Index", "COBOUAGENC"),
    "Issue": ("../../wiki/systems/Jira-Tickets-Index", "Issue"),
    "Issues": ("../../wiki/systems/Jira-Tickets-Index", "Issues"),
    "Project": ("../../wiki/systems/Jira-Tickets-Index", "Project"),
    "Board": ("../../wiki/systems/Jira-Tickets-Index", "Board"),
    "Sprint": ("../../wiki/systems/Jira-Tickets-Index", "Sprint"),
    "Epic": ("../../wiki/systems/Jira-Tickets-Index", "Epic"),
    "LabelText": ("../../wiki/systems/Jira-Tickets-Index", "Label"),
    "Create": ("../../wiki/systems/Jira-Tickets-Index", "Create"),
    "Update": ("../../wiki/systems/Jira-Tickets-Index", "Update"),
    "Delete": ("../../wiki/systems/Jira-Tickets-Index", "Delete"),
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
    print(f"07-Jira: {total} links added")
