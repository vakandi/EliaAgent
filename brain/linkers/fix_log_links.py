#!/usr/bin/env python3
"""Fix wiki links in .log files with correct Obsidian path"""

import re
from pathlib import Path

WIKI_LINKS = {
    "Wael": ("../../../wiki/people/Wael", "Wael"),
    "Bousfira": ("../../../wiki/people/Wael", "Bousfira"),
    "Thomas": ("../../../wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("../../../wiki/people/Ali", "Ali"),
    "Rida": ("../../../wiki/people/Rida", "Rida"),
    "Elia": ("../../../wiki/people/Elia", "Elia"),
    "Claude": ("../../../wiki/people/Claude", "Claude"),
    "Anass": ("../../../wiki/people/Anass", "Anass"),
    "Bene2Luxe": ("../../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "B2LUXE": ("../../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE"),
    "ZovaBoost": ("../../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "CoBou": ("../../../wiki/businesses/CoBou-Agency", "CoBou"),
    "MAYAVANTA": ("../../../wiki/businesses/Mayavanta", "MAYAVANTA"),
    "OGBoujee": ("../../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../../wiki/businesses/Netfluxe", "Netfluxe"),
    "TikTok": ("../../../wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("../../../wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "SurfAI": ("../../../wiki/businesses/SurfAI", "SurfAI"),
    "Telegram": ("../../../wiki/channels/Telegram", "Telegram"),
    "WhatsApp": ("../../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Discord": ("../../../wiki/channels/Discord-EliaWorkSpace", "Discord"),
    "Docker": ("../../../wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("../../../wiki/systems/SSH-Servers", "SSH"),
    "Jira": ("../../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../../wiki/tools/MCP-Tools", "MCP"),
    "Stripe": ("../../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    "AI": ("../../../wiki/concepts/AI-Automation", "AI"),
    "OpenAI": ("../../../wiki/people/OpenAI", "OpenAI"),
    "GPT": ("../../../wiki/people/GPT", "GPT"),
    "Gemini": ("../../../wiki/people/Gemini", "Gemini"),
    "Agent": ("../../../wiki/concepts/AI-Automation", "Agent"),
    "OpenCode": ("../../../wiki/skills/OpenCode-CLI", "OpenCode"),
    "Python": ("../../../wiki/skills/Python-Scripting", "Python"),
    "GitHub": ("../../../wiki/skills/Git-Version-Control", "GitHub"),
    "Git": ("../../../wiki/skills/Git-Version-Control", "Git"),
    "Playwright": ("../../../wiki/skills/Playwright", "Playwright"),
    "Chrome": ("../../../wiki/skills/Chrome-Automation", "Chrome"),
    "Task": ("../../../wiki/concepts/AI-Automation#tasks", "Task"),
    "Tasks": ("../../../wiki/concepts/AI-Automation#tasks", "Tasks"),
    "Prompt": ("../../../wiki/concepts/Prompt-Engineering", "Prompt"),
    "Session": ("../../../wiki/docs/Sessions", "Session"),
    "Docs": ("../../../wiki/HOME", "Docs"),
    "Documents": ("../../../wiki/HOME", "Documents"),
    "Chanel": ("../../../wiki/concepts/Luxury-Brands#chanel", "Chanel"),
    "Dior": ("../../../wiki/concepts/Luxury-Brands#dior", "Dior"),
    "Gucci": ("../../../wiki/concepts/Luxury-Brands#gucci", "Gucci"),
    "Louis Vuitton": (
        "../../../wiki/concepts/Luxury-Brands#louis-vuitton",
        "Louis Vuitton",
    ),
    "LV": ("../../../wiki/concepts/Luxury-Brands#louis-vuitton", "LV"),
    "Hermès": ("../../../wiki/concepts/Luxury-Brands#hermes", "Hermès"),
    "Prada": ("../../../wiki/concepts/Luxury-Brands#prada", "Prada"),
    "Balenciaga": ("../../../wiki/concepts/Luxury-Brands#balenciaga", "Balenciaga"),
    "Off-White": ("../../../wiki/concepts/Luxury-Brands#off-white", "Off-White"),
    "Moncler": ("../../../wiki/concepts/Luxury-Brands#moncler", "Moncler"),
}


def fix_links(filepath):
    content = filepath.read_text(encoding="utf-8", errors="ignore")

    # Remove broken nested links first
    content = re.sub(r"\[\[.*?\[\[", "[[", content)
    content = re.sub(r"\[\[.*?\|.*?\]\]", lambda m: m.group(0), content)

    # Remove old wrong paths and replace with correct ones
    content = content.replace("[[../../wiki/", "[[../../../wiki/")

    # Add new links only where not already linked
    for keyword, (target, display) in WIKI_LINKS.items():
        # Skip if already has this target
        if f"[[{target}|" in content or f"[[{target}]]" in content:
            continue

        # Word boundary replacement
        pattern = rf"(?<!\[\[)\b{re.escape(keyword)}\b(?!\])"
        content = re.sub(pattern, f"[[{target}|{display}]]", content)

    filepath.write_text(content, encoding="utf-8")


def main():
    base = Path("/Users/vakandi/EliaAI/brain/raw")
    files = list(base.glob("**/*.log"))

    print(f"Fixing wiki links in {len(files)} .log files...")

    for i, filepath in enumerate(files, 1):
        fix_links(filepath)
        if i % 100 == 0:
            print(f"  [{i}/{len(files)}]")

    print(f"Done!")


if __name__ == "__main__":
    main()
