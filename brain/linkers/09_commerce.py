#!/usr/bin/env python3
"""
Linker 09: Business & Commerce
Target: all .md files in /Users/vakandi/EliaAI/brain/raw
"""

import re
from pathlib import Path

LINKS = {
    "Stripe": ("../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    "Business": ("../../wiki/businesses/B2LUXE-BUSINESS", "Business"),
    "BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "BUSINESS"),
    "Agency": ("../../wiki/businesses/CoBou-Agency", "Agency"),
    "LLC": ("../../wiki/businesses/B2LUXE-BUSINESS", "LLC"),
    "Revenue": ("../../wiki/businesses/Bene2Luxe#revenue", "Revenue"),
    "Payment": ("../../wiki/businesses/Bene2Luxe#payments", "Payment"),
    "Invoice": ("../../wiki/businesses/CoBou-Agency#invoicing", "Invoice"),
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
    print(f"09-Commerce: {total} links added")
