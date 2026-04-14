#!/usr/bin/env python3
"""
Dedicated .log file linker for Elia Brain
Links all .log files with wiki keywords
"""

import re
from pathlib import Path
from collections import defaultdict

WIKI_LINKS = {
    # PEOPLE
    "Wael": ("../../wiki/people/Wael", "Wael"),
    "Bousfira": ("../../wiki/people/Wael", "Bousfira"),
    "Thomas": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("../../wiki/people/Ali", "Ali"),
    "Rida": ("../../wiki/people/Rida", "Rida"),
    "Elia": ("../../wiki/people/Elia", "Elia"),
    "Claude": ("../../wiki/people/Claude", "Claude"),
    "Anass": ("../../wiki/people/Anass", "Anass"),
    # BUSINESSES
    "Bene2Luxe": ("../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "B2LUXE": ("../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE"),
    "ZovaBoost": ("../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "CoBou": ("../../wiki/businesses/CoBou-Agency", "CoBou"),
    "CoBou Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "MAYAVANTA": ("../../wiki/businesses/Mayavanta", "MAYAVANTA"),
    "OGBoujee": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "TikTok": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("../../wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "SurfAI": ("../../wiki/businesses/SurfAI", "SurfAI"),
    # CHANNELS
    "Telegram": ("../../wiki/channels/Telegram", "Telegram"),
    "WhatsApp": ("../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Discord": ("../../wiki/channels/Discord-EliaWorkSpace", "Discord"),
    "PowerRangers": ("../../wiki/channels/WhatsApp-B2LUXE", "PowerRangers"),
    # SYSTEMS
    "Docker": ("../../wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("../../wiki/systems/SSH-Servers", "SSH"),
    "Jira": ("../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../wiki/tools/MCP-Tools", "MCP"),
    "IONOS": ("../../wiki/systems/IONOS", "IONOS"),
    "Stripe": ("../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    # AI
    "AI": ("../../wiki/concepts/AI-Automation", "AI"),
    "OpenAI": ("../../wiki/people/OpenAI", "OpenAI"),
    "GPT": ("../../wiki/people/GPT", "GPT"),
    "Gemini": ("../../wiki/people/Gemini", "Gemini"),
    "Agent": ("../../wiki/concepts/AI-Automation", "Agent"),
    # TOOLS
    "OpenCode": ("../../wiki/skills/OpenCode-CLI", "OpenCode"),
    "Python": ("../../wiki/skills/Python-Scripting", "Python"),
    "GitHub": ("../../wiki/skills/Git-Version-Control", "GitHub"),
    "Git": ("../../wiki/skills/Git-Version-Control", "Git"),
    "Playwright": ("../../wiki/skills/Playwright", "Playwright"),
    "Chrome": ("../../wiki/skills/Chrome-Automation", "Chrome"),
    # WORKFLOW
    "Task": ("../../wiki/concepts/AI-Automation#tasks", "Task"),
    "Tasks": ("../../wiki/concepts/AI-Automation#tasks", "Tasks"),
    "Prompt": ("../../wiki/concepts/Prompt-Engineering", "Prompt"),
    "PROMPT": ("../../wiki/concepts/Prompt-Engineering", "PROMPT"),
    "Session": ("../../wiki/docs/Sessions", "Session"),
    "Docs": ("../../wiki/HOME", "Docs"),
    "Documents": ("../../wiki/HOME", "Documents"),
    # LUXURY BRANDS
    "Chanel": ("../../wiki/concepts/Luxury-Brands#chanel", "Chanel"),
    "Dior": ("../../wiki/concepts/Luxury-Brands#dior", "Dior"),
    "Gucci": ("../../wiki/concepts/Luxury-Brands#gucci", "Gucci"),
    "Louis Vuitton": (
        "../../wiki/concepts/Luxury-Brands#louis-vuitton",
        "Louis Vuitton",
    ),
    "LV": ("../../wiki/concepts/Luxury-Brands#louis-vuitton", "LV"),
    "Hermès": ("../../wiki/concepts/Luxury-Brands#hermes", "Hermès"),
    "Prada": ("../../wiki/concepts/Luxury-Brands#prada", "Prada"),
    "Balenciaga": ("../../wiki/concepts/Luxury-Brands#balenciaga", "Balenciaga"),
    "Off-White": ("../../wiki/concepts/Luxury-Brands#off-white", "Off-White"),
    "Moncler": ("../../wiki/concepts/Luxury-Brands#moncler", "Moncler"),
}


def link_file(filepath: Path, dry_run: bool = False) -> tuple:
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except:
        return 0, {}

    stats = defaultdict(int)
    total = 0

    for keyword, (target, display) in WIKI_LINKS.items():
        if f"[[{target}" in content:
            continue

        pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
        new, n = pattern.subn(f"[[{target}|{display}]]", content)

        if n:
            content = new
            total += n
            stats[keyword] = n

    if total > 0 and not dry_run:
        filepath.write_text(content, encoding="utf-8")

    return total, dict(stats)


def main():
    base = Path("/Users/vakandi/EliaAI/brain/raw")
    files = list(base.glob("**/*.log"))

    print(f"LOG FILE LINKER")
    print(f"Target: {base}")
    print(f"Total .log files: {len(files)}")
    print()

    total_links = 0
    total_files = 0
    all_stats = defaultdict(int)

    for i, filepath in enumerate(files, 1):
        count, stats = link_file(filepath)
        if count > 0:
            total_links += count
            total_files += 1
            for k, v in stats.items():
                all_stats[k] += v
            print(f"  [{i}/{len(files)}] {filepath}: +{count}")

    print()
    print(f"Processed {total_files}/{len(files)} files")
    print(f"Links added: {total_links:,}")

    if all_stats:
        print("\nTop keywords:")
        for k, v in sorted(all_stats.items(), key=lambda x: -x[1])[:15]:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
