#!/usr/bin/env python3
"""
Bulk wiki link generator for Elia Brain.
Analyzes top words from raw logs and applies wiki links to all brain pages.
"""

import re
import os
from pathlib import Path

# Mapping of keywords to wiki links (relative to brain/)
# Format: {"keyword": ("target_file", "display_name") or None for skip}
BRAIN_WIKI_LINKS = {
    # Businesses
    "Bene2Luxe": ("../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "B2LUXE BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "ZovaBoost": ("../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "OGBoujee": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "OGBoujee.com": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "netfluxe.com": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "CoBou Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "CoBou-Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "TikTok": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok/YouTube Auto"),
    "YouTube": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok/YouTube Auto"),
    # People
    "Wael": ("../../wiki/people/Wael", "Wael"),
    "Thomas": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Thomas-Cogne": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("../../wiki/people/Ali", "Ali"),
    "Rida": ("../../wiki/people/Rida", "Rida"),
    "Elia": ("../../wiki/people/Elia", "Elia"),
    # Channels
    "WhatsApp": ("../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Telegram": ("../../wiki/channels/Telegram", "Telegram"),
    "Discord": ("../../wiki/channels/Discord-EliaWorkSpace", "Discord"),
    # Systems & Tools
    "Docker": ("../../wiki/systems/Docker-Servers", "Docker"),
    "Stripe": ("../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    "SSL": ("../../wiki/topics/Infrastructure-Timeline#ssl", "SSL"),
    "Jira": ("../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../wiki/tools/MCP-Tools", "MCP"),
    # Topics
    "UGC": ("../../wiki/concepts/UGC", "UGC"),
    "Mascoot": ("../../wiki/skills/Higgsfield-Video", "Mascoot"),
    "Higgsfield": ("../../wiki/skills/Higgsfield-Video", "Higgsfield"),
    # Wiki sections
    "Wiki": ("../../wiki/HOME", "Wiki"),
    "Brain": ("../index", "Brain"),
}


def apply_wiki_links(content: str, skip_in_links: bool = False) -> tuple[str, int]:
    """Apply wiki links to content. Returns (new_content, link_count)."""
    if skip_in_links:
        # Split on wiki link sections to avoid double-linking
        parts = re.split(r"(>\s*\[\[|\]\])", content)
    else:
        parts = [content]

    link_count = 0
    result_parts = []

    for part in parts:
        if skip_in_links and ">[[.." in part:
            result_parts.append(part)
            continue

        for keyword, (target, display) in BRAIN_WIKI_LINKS.items():
            # Skip if already linked (look for [[...|keyword]] or [[target]])
            if f"[[{target}" in part or f"|{keyword}]]" in part:
                continue

            # Word boundary match, case insensitive
            pattern = re.compile(rf"\b{re.escape(keyword)}\b(?!\])", re.IGNORECASE)
            if pattern.search(part):
                # Replace only first occurrence per keyword per part
                new_part = pattern.sub(f"[[{target}|{display}]]", part, count=1)
                if new_part != part:
                    link_count += 1
                    part = new_part

        result_parts.append(part)

    return "".join(result_parts), link_count


def process_file(filepath: Path, dry_run: bool = False, verbose: bool = False) -> int:
    """Process a single file. Returns link count added."""
    try:
        content = filepath.read_text(encoding="utf-8")
        new_content, count = apply_wiki_links(content)

        if count > 0 and not dry_run:
            filepath.write_text(new_content, encoding="utf-8")

        if verbose and count > 0:
            print(f"  {filepath.name}: +{count} links")

        return count
    except Exception as e:
        print(f"  ERROR {filepath.name}: {e}")
        return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Bulk wiki link generator for Elia Brain"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--path", default=".", help="Path to brain directory")
    args = parser.parse_args()

    brain_dir = Path(args.path)
    pages_dir = brain_dir / "pages"

    total_links = 0
    files_processed = 0

    # Process all markdown files in brain
    for md_file in brain_dir.glob("*.md"):
        if md_file.name == "AGENTS.md":
            continue
        count = process_file(md_file, args.dry_run, args.verbose)
        if count > 0:
            total_links += count
            files_processed += 1

    # Process all pages
    for category_dir in pages_dir.glob("*"):
        if category_dir.is_dir():
            if args.verbose:
                print(f"\n{category_dir.name}/")
            for md_file in category_dir.glob("*.md"):
                count = process_file(md_file, args.dry_run, args.verbose)
                if count > 0:
                    total_links += count
                    files_processed += 1

    print(f"\n✅ Processed {files_processed} files, added {total_links} wiki links")
    if args.dry_run:
        print("   (dry-run: no files were modified)")


if __name__ == "__main__":
    main()
