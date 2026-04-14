#!/usr/bin/env python3
"""
Linker 07: Luxury Brands
Target: All .md files in /Users/vakandi/EliaAI/docs
"""

import re
from pathlib import Path

LINKS = {
    "Chanel": ("wiki/concepts/Luxury-Brands#chanel", "Chanel"),
    "Dior": ("wiki/concepts/Luxury-Brands#dior", "Dior"),
    "Gucci": ("wiki/concepts/Luxury-Brands#gucci", "Gucci"),
    "Louis Vuitton": ("wiki/concepts/Luxury-Brands#louis-vuitton", "Louis Vuitton"),
    "Louis": ("wiki/concepts/Luxury-Brands#louis-vuitton", "Louis"),
    "Vuitton": ("wiki/concepts/Luxury-Brands#louis-vuitton", "Vuitton"),
    "LV": ("wiki/concepts/Luxury-Brands#louis-vuitton", "LV"),
    "Balenciaga": ("wiki/concepts/Luxury-Brands#balenciaga", "Balenciaga"),
    "Hermès": ("wiki/concepts/Luxury-Brands#hermes", "Hermès"),
    "Prada": ("wiki/concepts/Luxury-Brands#prada", "Prada"),
    "YSL": ("wiki/concepts/Luxury-Brands#ysl", "YSL"),
    "Saint Laurent": ("wiki/concepts/Luxury-Brands#ysl", "Saint Laurent"),
    "Versace": ("wiki/concepts/Luxury-Brands#versace", "Versace"),
    "Burberry": ("wiki/concepts/Luxury-Brands#burberry", "Burberry"),
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
    print(f"07-Luxury-Brands: {total} links added")
