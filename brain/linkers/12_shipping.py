#!/usr/bin/env python3
"""
Linker 12: Shipping & Logistics
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Shipping": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Shipping"),
    "Ship": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Ship"),
    "Shipped": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Shipped"),
    "Express": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Express"),
    "Standard": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Standard"),
    "Delivery": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Delivery"),
    "Carrier": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Carrier"),
    "Tracking": ("wiki/businesses/B2LUXE-BUSINESS#shipping", "Tracking"),
    "Supplier": ("wiki/businesses/B2LUXE-BUSINESS#suppliers", "Supplier"),
    "Suppliers": ("wiki/businesses/B2LUXE-BUSINESS#suppliers", "Suppliers"),
    "Logistics": ("wiki/businesses/B2LUXE-BUSINESS#logistics", "Logistics"),
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
    print(f"12-Shipping: {total} links added")
