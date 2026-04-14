#!/usr/bin/env python3
"""
Bulk Linker for .log files in brain/raw/logs/
Adds wiki links to keywords in OpenCode session logs
"""

import re
from pathlib import Path
from collections import defaultdict

# Same wiki links as master_bulk_linker
WIKI_LINKS = {
    # === PEOPLE ===
    "Wael": ("../../wiki/people/Wael", "Wael"),
    "Thomas": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("../../wiki/people/Ali", "Ali"),
    "Rida": ("../../wiki/people/Rida", "Rida"),
    "Elia": ("../../wiki/people/Elia", "Elia"),
    "Claude": ("../../wiki/people/Claude", "Claude"),
    "Anass": ("../../wiki/people/Anass", "Anass"),
    # === BUSINESSES ===
    "Bene2Luxe": ("../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "ZovaBoost": ("../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "CoBou": ("../../wiki/businesses/CoBou-Agency", "CoBou"),
    "MAYAVANTA": ("../../wiki/businesses/Mayavanta", "MAYAVANTA"),
    "OGBoujee": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "TikTok": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("../../wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    # === CHANNELS ===
    "Telegram": ("../../wiki/channels/Telegram", "Telegram"),
    "WhatsApp": ("../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Discord": ("../../wiki/channels/Discord-EliaWorkSpace", "Discord"),
    # === SYSTEMS ===
    "Docker": ("../../wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("../../wiki/systems/SSH-Servers", "SSH"),
    "Jira": ("../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../wiki/tools/MCP-Tools", "MCP"),
    "Stripe": ("../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    # === AI ===
    "AI": ("../../wiki/concepts/AI-Automation", "AI"),
    "OpenAI": ("../../wiki/people/OpenAI", "OpenAI"),
    "GPT": ("../../wiki/people/GPT", "GPT"),
    "Gemini": ("../../wiki/people/Gemini", "Gemini"),
    "Agent": ("../../wiki/concepts/AI-Automation", "Agent"),
    # === TOOLS ===
    "OpenCode": ("../../wiki/skills/OpenCode-CLI", "OpenCode"),
    "Python": ("../../wiki/skills/Python-Scripting", "Python"),
    "GitHub": ("../../wiki/skills/Git-Version-Control", "GitHub"),
    "Git": ("../../wiki/skills/Git-Version-Control", "Git"),
    # === WORKFLOW ===
    "Task": ("../../wiki/concepts/AI-Automation#tasks", "Task"),
    "Tasks": ("../../wiki/concepts/AI-Automation#tasks", "Tasks"),
    "Prompt": ("../../wiki/concepts/Prompt-Engineering", "Prompt"),
    "PROMPT": ("../../wiki/concepts/Prompt-Engineering", "PROMPT"),
    "Session": ("../../wiki/docs/Sessions", "Session"),
    "Docs": ("../../wiki/HOME", "Docs"),
    # === LUXURY BRANDS ===
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
    "Valentino": ("../../wiki/concepts/Luxury-Brands#valentino", "Valentino"),
    "Versace": ("../../wiki/concepts/Luxury-Brands#versace", "Versace"),
    "YSL": ("../../wiki/concepts/Luxury-Brands#ysl", "YSL"),
    "Saint Laurent": ("../../wiki/concepts/Luxury-Brands#ysl", "Saint Laurent"),
    "Fendi": ("../../wiki/concepts/Luxury-Brands#fendi", "Fendi"),
    "Burberry": ("../../wiki/concepts/Luxury-Brands#burberry", "Burberry"),
    "Canada Goose": ("../../wiki/concepts/Luxury-Brands#canada-goose", "Canada Goose"),
    "Moncler": ("../../wiki/concepts/Luxury-Brands#moncler", "Moncler"),
    "Off-White": ("../../wiki/concepts/Luxury-Brands#off-white", "Off-White"),
    # === ERROR TYPES ===
    "Error": ("../../wiki/topics/Infrastructure-Timeline#errors", "Error"),
    "ERROR": ("../../wiki/topics/Infrastructure-Timeline#errors", "ERROR"),
    "error": ("../../wiki/topics/Infrastructure-Timeline#errors", "error"),
    "Failed": ("../../wiki/topics/Infrastructure-Timeline#errors", "Failed"),
    "failed": ("../../wiki/topics/Infrastructure-Timeline#errors", "failed"),
    "Warning": ("../../wiki/topics/Infrastructure-Timeline#warnings", "Warning"),
    "warning": ("../../wiki/topics/Infrastructure-Timeline#warnings", "warning"),
}


def is_error_log(content: str) -> bool:
    """Check if file is primarily error logs"""
    lines = content.split("\n")
    error_lines = [l for l in lines if "ERROR" in l or "error" in l or "FAILED" in l]
    return len(error_lines) > len(lines) * 0.3


def link_file(filepath: Path, dry_run: bool = False) -> tuple[int, dict]:
    """Process a single .log file. Returns (link_count, stats_dict)."""
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
    base = Path("/Users/vakandi/EliaAI/brain/raw/logs")
    files = list(base.glob("*.log"))

    print(f"🔗 Log Bulk Linker")
    print(f"   Target: {base}")
    print(f"   Files: {len(files)}")
    print(f"   Keywords: {len(WIKI_LINKS)}")
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
    print(f"✅ Processed {total_files}/{len(files)} files")
    print(f"   Total links added: {total_links}")

    if all_stats:
        print()
        print("Top linked keywords:")
        for k, v in sorted(all_stats.items(), key=lambda x: -x[1])[:15]:
            print(f"   {k}: {v}")

    if dry_run:
        print("\n⚠️  Dry run - no files were modified")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(args.dry_run)
