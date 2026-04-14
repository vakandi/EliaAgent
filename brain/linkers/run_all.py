#!/usr/bin/env python3
"""
Master linker script - runs all 100 linker scripts
"""

import subprocess
from pathlib import Path

LINKERS_DIR = Path(__file__).parent


def main():
    linkers = sorted(LINKERS_DIR.glob("[0-9][0-9]_*.py"))
    total = 0
    for linker in linkers:
        print(f"Running {linker.name}...")
        result = subprocess.run(
            ["python3", str(linker)], capture_output=True, text=True
        )
        print(f"  {result.stdout.strip()}")
        if result.stderr:
            print(f"  ERR: {result.stderr[:100]}")
    print(f"\n✅ All {len(linkers)} linkers complete!")


if __name__ == "__main__":
    main()
