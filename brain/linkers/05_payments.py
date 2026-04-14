#!/usr/bin/env python3
"""
Linker 05: Payment & E-commerce
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Stripe": ("wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    "Point Relais": (
        "wiki/topics/Infrastructure-Timeline#point-relais",
        "Point Relais",
    ),
    "hostedemail": ("wiki/systems/IONOS#hostedemail", "hostedemail"),
    "Checkout": ("wiki/businesses/Bene2Luxe#checkout", "Checkout"),
    "Payment": ("wiki/businesses/Bene2Luxe#payments", "Payment"),
    "Orders": ("wiki/businesses/B2LUXE-BUSINESS#orders", "Orders"),
    "Invoice": ("wiki/businesses/CoBou-Agency#invoicing", "Invoice"),
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
    print(f"05-Payments: {total} links added")
