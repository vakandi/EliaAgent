# RELINK_BRAIN - Brain Wiki Linking System

This document explains how the Elia Brain wiki linking system works, including all scripts, paths, and usage.

## Overview

The Elia Brain uses Obsidian wiki-style links (`[[...]]`) to connect raw session data files to wiki pages. This enables:
- Graph view navigation between related sessions
- Cross-referencing content across dates
- Finding related work by topic/keyword

## Directory Structure

```
/Users/vakandi/EliaAI/
├── brain/                    # Main brain vault
│   ├── raw/                 # Raw session data
│   │   ├── logs/           # .log files (OpenCode sessions)
│   │   ├── 2026-03-xx/    # Daily session folders
│   │   └── **/*.log, *.txt # All raw files
│   ├── wiki/               # (symlink or reference to root wiki)
│   ├── linkers/            # Linking scripts
│   │   ├── master_bulk_linker.py
│   │   ├── log_linker.py
│   │   ├── fix_log_links.py
│   │   └── comprehensive_linker.py
│   └── pages/             # Analysis pages
├── wiki/                    # Main wiki directory
│   ├── people/            # Person pages
│   ├── businesses/         # Business pages
│   ├── channels/          # Communication channels
│   ├── concepts/           # Concept pages
│   ├── systems/           # System/infrastructure pages
│   └── skills/            # Skill pages
└── docs/                   # Documentation
```

## Wiki Link Format

### Standard Path from raw/ files

Files in `brain/raw/**` use this path pattern:
```
[[../../../wiki/<path>|<display>]]
```

Example:
```
[[../../../wiki/people/Wael|Wael]]
[[../../../wiki/businesses/Bene2Luxe|Bene2Luxe]]
```

### Why ../../../wiki/ ?

| File Location | Relative Path to wiki/ |
|--------------|----------------------|
| `brain/raw/logs/file.log` | `../../../wiki/` |
| `brain/raw/2026-03-15/file.log` | `../../../../wiki/` |
| `brain/raw/2026-03-15/docs/file.txt` | `../../../../../wiki/` |

## Linking Scripts

### 1. master_bulk_linker.py

Links all `.md` files in `brain/raw/`.

**Location:** `brain/linkers/master_bulk_linker.py`

**Usage:**
```bash
cd /Users/vakandi/EliaAI/brain/linkers
python3 master_bulk_linker.py           # Run
python3 master_bulk_linker.py --dry-run   # Preview
```

**Features:**
- Processes all `.md` files in `brain/raw/`
- Uses 300+ keyword mappings
- Tracks statistics per keyword

### 2. log_linker.py

Links all `.log` files in `brain/raw/`.

**Location:** `brain/linkers/log_linker.py`

**Usage:**
```bash
cd /Users/vakandi/EliaAI/brain/linkers
python3 log_linker.py
```

**Features:**
- Processes all `.log` files recursively
- Uses 50+ keyword mappings
- Path format: `../../../wiki/...`

### 3. fix_log_links.py

Fixes broken/nested links and corrects paths.

**Location:** `brain/linkers/fix_log_links.py`

**Usage:**
```bash
python3 fix_log_links.py
```

**Features:**
- Removes broken nested links
- Corrects path prefixes
- Adds missing links

### 4. comprehensive_linker.py

Links ALL files (`.log`, `.txt`, `.md`) in `brain/raw/`.

**Location:** `brain/linkers/comprehensive_linker.py`

**Usage:**
```bash
python3 comprehensive_linker.py --dry-run
python3 comprehensive_linker.py
```

## Keyword Mappings

### People
```python
"Wael": ("../../../wiki/people/Wael", "Wael")
"Thomas": ("../../../wiki/people/Thomas-Cogne", "Thomas")
"Ali": ("../../../wiki/people/Ali", "Ali")
"Rida": ("../../../wiki/people/Rida", "Rida")
"Elia": ("../../../wiki/people/Elia", "Elia")
"Claude": ("../../../wiki/people/Claude", "Claude")
```

### Businesses
```python
"Bene2Luxe": ("../../../wiki/businesses/Bene2Luxe", "Bene2Luxe")
"B2LUXE": ("../../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE")
"ZovaBoost": ("../../../wiki/businesses/ZovaBoost", "ZovaBoost")
"CoBou": ("../../../wiki/businesses/CoBou-Agency", "CoBou")
"MAYAVANTA": ("../../../wiki/businesses/Mayavanta", "MAYAVANTA")
"OGBoujee": ("../../../wiki/businesses/OGBoujee", "OGBoujee")
"Netfluxe": ("../../../wiki/businesses/Netfluxe", "Netfluxe")
```

### Channels
```python
"Telegram": ("../../../wiki/channels/Telegram", "Telegram")
"WhatsApp": ("../../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp")
"Discord": ("../../../wiki/channels/Discord-EliaWorkSpace", "Discord")
```

### Systems
```python
"Docker": ("../../../wiki/systems/Docker-Servers", "Docker")
"SSH": ("../../../wiki/systems/SSH-Servers", "SSH")
"Jira": ("../../../wiki/systems/Jira-Tickets-Index", "Jira")
"MCP": ("../../../wiki/tools/MCP-Tools", "MCP")
"Stripe": ("../../../wiki/businesses/Bene2Luxe#stripe", "Stripe")
"Shopify": ("../../../wiki/businesses/Bene2Luxe#shopify", "Shopify")
```

### AI & Tools
```python
"AI": ("../../../wiki/concepts/AI-Automation", "AI")
"OpenAI": ("../../../wiki/people/OpenAI", "OpenAI")
"GPT": ("../../../wiki/people/GPT", "GPT")
"Gemini": ("../../../wiki/people/Gemini", "Gemini")
"OpenCode": ("../../../wiki/skills/OpenCode-CLI", "OpenCode")
"Python": ("../../../wiki/skills/Python-Scripting", "Python")
"GitHub": ("../../../wiki/skills/Git-Version-Control", "GitHub")
"Playwright": ("../../../wiki/skills/Playwright", "Playwright")
```

### Luxury Brands
```python
"Chanel": ("../../../wiki/concepts/Luxury-Brands#chanel", "Chanel")
"Dior": ("../../../wiki/concepts/Luxury-Brands#dior", "Dior")
"Gucci": ("../../../wiki/concepts/Luxury-Brands#gucci", "Gucci")
"Louis Vuitton": ("../../../wiki/concepts/Luxury-Brands#louis-vuitton", "Louis Vuitton")
"Louis Vuitton": ("../../../wiki/concepts/Luxury-Brands#louis-vuitton", "LV")
"Hermès": ("../../../wiki/concepts/Luxury-Brands#hermes", "Hermès")
"Prada": ("../../../wiki/concepts/Luxury-Brands#prada", "Prada")
"Balenciaga": ("../../../wiki/concepts/Luxury-Brands#balenciaga", "Balenciaga")
"Off-White": ("../../../wiki/concepts/Luxury-Brands#off-white", "Off-White")
"Moncler": ("../../../wiki/concepts/Luxury-Brands#moncler", "Moncler")
```

## File Statistics

### As of 2026-04-12

| Metric | Count |
|--------|-------|
| Total .log files | 1,163 |
| Files with links | ~1,055 |
| Total wiki links | ~560,000+ |
| Linkable keywords | 50+ |

## Common Issues & Fixes

### Issue: Nested Links
**Problem:** Links like `[[text [[more]] text]]`
**Fix:** Run `fix_log_links.py`

### Issue: Wrong Path
**Problem:** Links using `../../wiki/` instead of `../../../wiki/`
**Fix:** Run `fix_log_links.py`

### Issue: Links Not Clickable in Obsidian
**Solution:** 
1. Ensure `wiki/` folder is in the vault
2. Check path is correct relative to file location
3. Run `fix_log_links.py` to correct

## Verification Commands

### Check link count in a file
```bash
grep -o '\[\[../../../wiki/[^]]*\]\]' file.log | wc -l
```

### Find unlinked files
```python
from pathlib import Path
base = Path('/Users/vakandi/EliaAI/brain/raw')
unlinked = [f for f in base.glob('**/*.log') 
            if f.read_text(errors='ignore').count('../../../wiki/') == 0 
            and len(f.read_text(errors='ignore').split()) > 50]
print(f'Unlinked: {len(unlinked)}')
```

### Verify path format
```bash
grep -o '\[\[../../../wiki/' brain/raw/logs/*.log | wc -l
```

## Adding New Keywords

To add a new keyword:

1. Edit the linker script (e.g., `log_linker.py`)
2. Add entry to `WIKI_LINKS` dict:
```python
"NewKeyword": ("../../../wiki/path/to/page", "Display Name"),
```
3. Run the linker again:
```bash
python3 log_linker.py
```

## Cron Job for Auto-Linking

Add to crontab for automatic linking:
```bash
# Run every day at 3am
0 3 * * * cd /Users/vakandi/EliaAI/brain/linkers && python3 comprehensive_linker.py >> /Users/vakandi/EliaAI/brain/raw/logs/linker_cron.log 2>&1
```

## Summary

The linking system transforms raw session data into a navigable knowledge graph:

- **Input:** Raw `.log`, `.txt`, `.md` files in `brain/raw/`
- **Process:** Python scripts replace keywords with wiki links
- **Output:** Clickable `[[../../../wiki/...]]` links in Obsidian
- **Result:** Graph view shows connections between sessions, people, businesses, etc.

---
*Generated: 2026-04-12*
*Scripts: `/Users/vakandi/EliaAI/brain/linkers/`*
