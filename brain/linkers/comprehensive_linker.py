#!/usr/bin/env python3
"""
Comprehensive Bulk Linker for all files in brain/raw/
"""

import re
from pathlib import Path
from collections import defaultdict

WIKI_LINKS = {
    "Wael": ("../../wiki/people/Wael", "Wael"),
    "Thomas": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("../../wiki/people/Ali", "Ali"),
    "Rida": ("../../wiki/people/Rida", "Rida"),
    "Elia": ("../../wiki/people/Elia", "Elia"),
    "Claude": ("../../wiki/people/Claude", "Claude"),
    "Anass": ("../../wiki/people/Anass", "Anass"),
    "Bene2Luxe": ("../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "ZovaBoost": ("../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "CoBou": ("../../wiki/businesses/CoBou-Agency", "CoBou"),
    "MAYAVANTA": ("../../wiki/businesses/Mayavanta", "MAYAVANTA"),
    "OGBoujee": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "TikTok": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("../../wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "Telegram": ("../../wiki/channels/Telegram", "Telegram"),
    "WhatsApp": ("../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Discord": ("../../wiki/channels/Discord-EliaWorkSpace", "Discord"),
    "Docker": ("../../wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("../../wiki/systems/SSH-Servers", "SSH"),
    "Jira": ("../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../wiki/tools/MCP-Tools", "MCP"),
    "Stripe": ("../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    "AI": ("../../wiki/concepts/AI-Automation", "AI"),
    "OpenAI": ("../../wiki/people/OpenAI", "OpenAI"),
    "GPT": ("../../wiki/people/GPT", "GPT"),
    "Gemini": ("../../wiki/people/Gemini", "Gemini"),
    "Agent": ("../../wiki/concepts/AI-Automation", "Agent"),
    "OpenCode": ("../../wiki/skills/OpenCode-CLI", "OpenCode"),
    "Python": ("../../wiki/skills/Python-Scripting", "Python"),
    "GitHub": ("../../wiki/skills/Git-Version-Control", "GitHub"),
    "Git": ("../../wiki/skills/Git-Version-Control", "Git"),
    "Task": ("../../wiki/concepts/AI-Automation#tasks", "Task"),
    "Tasks": ("../../wiki/concepts/AI-Automation#tasks", "Tasks"),
    "Prompt": ("../../wiki/concepts/Prompt-Engineering", "Prompt"),
    "PROMPT": ("../../wiki/concepts/Prompt-Engineering", "PROMPT"),
    "Session": ("../../wiki/docs/Sessions", "Session"),
    "Docs": ("../../wiki/HOME", "Docs"),
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
    "Error": ("../../wiki/topics/Infrastructure-Timeline#errors", "Error"),
    "ERROR": ("../../wiki/topics/Infrastructure-Timeline#errors", "ERROR"),
    "Failed": ("../../wiki/topics/Infrastructure-Timeline#errors", "Failed"),
    "Zova": ("../../wiki/businesses/ZovaBoost", "Zova"),
    "Panel": ("../../wiki/businesses/ZovaBoost#panel", "Panel"),
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


def main(dry_run: bool = False):
    base = Path("/Users/vakandi/EliaAI/brain/raw")
    files = list(base.glob("**/*.log")) + list(base.glob("**/*.txt"))

    print(f"Comprehensive Linker")
    print(f"Target: {base}")
    print(f"Files: {len(files)}")
    print()

    total_links = 0
    total_files = 0
    all_stats = defaultdict(int)

    for i, filepath in enumerate(files, 1):
        count, stats = link_file(filepath, dry_run)
        if count > 0:
            total_links += count
            total_files += 1
            for k, v in stats.items():
                all_stats[k] += v
            if not dry_run and count > 0:
                print(f"  [{i}/{len(files)}] {filepath.name}: +{count}")

    print()
    print(f"Processed {total_files}/{len(files)} files")
    print(f"Links added: {total_links}")

    if all_stats:
        print("\nTop keywords:")
        for k, v in sorted(all_stats.items(), key=lambda x: -x[1])[:10]:
            print(f"  {k}: {v}")

    if dry_run:
        print("\nDry run - no changes made")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(args.dry_run)
