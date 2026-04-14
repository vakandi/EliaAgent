#!/usr/bin/env python3
"""
Linker 08: Tools & Software
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Cursor": ("wiki/skills/Cursor-IDE", "Cursor"),
    "OpenCode": ("wiki/skills/OpenCode-CLI", "OpenCode"),
    "Windsurf": ("wiki/skills/Windsurf-IDE", "Windsurf"),
    "Claude": ("wiki/people/Claude", "Claude"),
    "ChatGPT": ("wiki/people/ChatGPT", "ChatGPT"),
    "GPT": ("wiki/people/GPT", "GPT"),
    "Python": ("wiki/skills/Python-Scripting", "Python"),
    "Bash": ("wiki/skills/Bash-Scripting", "Bash"),
    "Shell": ("wiki/skills/Bash-Scripting", "Shell"),
    "Git": ("wiki/skills/Git-Version-Control", "Git"),
    "GitHub": ("wiki/skills/Git-Version-Control", "GitHub"),
    "Dockerfile": ("wiki/systems/Docker-Servers", "Dockerfile"),
    "FastAPI": ("wiki/skills/FastAPI-Development", "FastAPI"),
    "React": ("wiki/skills/React-Development", "React"),
    "TypeScript": ("wiki/skills/TypeScript-Development", "TypeScript"),
    "Node.js": ("wiki/skills/NodeJS-Development", "Node.js"),
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
    print(f"08-Tools: {total} links added")
