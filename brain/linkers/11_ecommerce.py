#!/usr/bin/env python3
"""
Linker 11: E-commerce & Products
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Product": ("wiki/businesses/Bene2Luxe#products", "Product"),
    "Products": ("wiki/businesses/Bene2Luxe#products", "Products"),
    "Inventory": ("wiki/businesses/Bene2Luxe#inventory", "Inventory"),
    "Sizes": ("wiki/businesses/Bene2Luxe#sizing", "Sizes"),
    "Size": ("wiki/businesses/Bene2Luxe#sizing", "Size"),
    "Sizing": ("wiki/businesses/Bene2Luxe#sizing", "Sizing"),
    "Stock": ("wiki/businesses/Bene2Luxe#inventory", "Stock"),
    "Pricing": ("wiki/concepts/Pricing", "Pricing"),
    "Price": ("wiki/concepts/Pricing", "Price"),
    "Luxury": ("wiki/concepts/Luxury-Brands", "Luxury"),
    "Resale": ("wiki/businesses/Bene2Luxe", "Resale"),
    "Catalog": ("wiki/businesses/Bene2Luxe#catalog", "Catalog"),
    "SKU": ("wiki/businesses/Bene2Luxe#catalog", "SKU"),
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
    print(f"11-Ecommerce: {total} links added")
