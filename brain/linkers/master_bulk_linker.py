#!/usr/bin/env python3
"""
Master Bulk Linker for Elia Brain
Links all words in raw/ logs to wiki pages
Target: /Users/vakandi/EliaAI/brain/raw/**/*.md
"""

import re
from pathlib import Path
from collections import defaultdict

# All wiki link mappings - keyword: (target, display)
WIKI_LINKS = {
    # === PEOPLE (50+ keywords) ===
    "Wael": ("../../wiki/people/Wael", "Wael"),
    "Bousfira": ("../../wiki/people/Wael", "Bousfira"),
    "Thomas": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Thomas-Cogne": ("../../wiki/people/Thomas-Cogne", "Thomas"),
    "Ali": ("../../wiki/people/Ali", "Ali"),
    "Rida": ("../../wiki/people/Rida", "Rida"),
    "Elia": ("../../wiki/people/Elia", "Elia"),
    "Claude": ("../../wiki/people/Claude", "Claude"),
    "Opus": ("../../wiki/people/Claude", "Opus"),
    "Marco": ("../../wiki/people/Marco", "Marco"),
    "Ronen": ("../../wiki/people/Ronen", "Ronen"),
    "Anass": ("../../wiki/people/Anass", "Anass"),
    # === BUSINESSES (50+ keywords) ===
    "Bene2Luxe": ("../../wiki/businesses/Bene2Luxe", "Bene2Luxe"),
    "B2LUXE BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "B2LUXE-BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "B2LUXE BUSINESS"),
    "ZovaBoost": ("../../wiki/businesses/ZovaBoost", "ZovaBoost"),
    "CoBou": ("../../wiki/businesses/CoBou-Agency", "CoBou"),
    "CoBou Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "CoBou-Agency": ("../../wiki/businesses/CoBou-Agency", "CoBou Agency"),
    "MAYAVANTA": ("../../wiki/businesses/Mayavanta", "MAYAVANTA"),
    "OGBoujee": ("../../wiki/businesses/OGBoujee", "OGBoujee"),
    "Netfluxe": ("../../wiki/businesses/Netfluxe", "Netfluxe"),
    "TikTok": ("../../wiki/businesses/TikTok-YouTube-Auto", "TikTok"),
    "YouTube": ("../../wiki/businesses/TikTok-YouTube-Auto", "YouTube"),
    "SurfAI": ("../../wiki/businesses/SurfAI", "SurfAI"),
    "Account Verification": (
        "../../wiki/businesses/Account-Verification",
        "Account Verification",
    ),
    "AccForgeDev": ("../../wiki/businesses/AccForge", "AccForge"),
    "Swissquote": ("../../wiki/businesses/Swissquote", "Swissquote"),
    # === CHANNELS ===
    "Telegram": ("../../wiki/channels/Telegram", "Telegram"),
    "WhatsApp": ("../../wiki/channels/WhatsApp-B2LUXE", "WhatsApp"),
    "Discord": ("../../wiki/channels/Discord-EliaWorkSpace", "Discord"),
    "PowerRangers": ("../../wiki/channels/WhatsApp-B2LUXE", "PowerRangers"),
    "Confluence": ("../../wiki/systems/Confluence", "Confluence"),
    "Proton": ("../../wiki/channels/ProtonMail", "Proton"),
    "Gmail": ("../../wiki/channels/Gmail", "Gmail"),
    # === SYSTEMS & INFRASTRUCTURE ===
    "Docker": ("../../wiki/systems/Docker-Servers", "Docker"),
    "SSH": ("../../wiki/systems/SSH-Servers", "SSH"),
    "Jira": ("../../wiki/systems/Jira-Tickets-Index", "Jira"),
    "MCP": ("../../wiki/tools/MCP-Tools", "MCP"),
    "FastMCP": ("../../wiki/tools/MCP-Tools", "FastMCP"),
    "MCP-GO": ("../../wiki/tools/MCP-Tools", "MCP-GO"),
    "MultiSaasDeploy": ("../../wiki/systems/MultiSaasDeploy", "MultiSaasDeploy"),
    "IONOS": ("../../wiki/systems/IONOS", "IONOS"),
    "Chrome": ("../../wiki/skills/Chrome-Automation", "Chrome"),
    "Playwright": ("../../wiki/skills/Playwright", "Playwright"),
    "Certbot": ("../../wiki/systems/Docker-Servers", "Certbot"),
    "SSL": ("../../wiki/topics/Infrastructure-Timeline", "SSL"),
    "HTTPS": ("../../wiki/topics/Infrastructure-Timeline", "HTTPS"),
    "HTTP": ("../../wiki/systems/Docker-Servers", "HTTP"),
    # === AI & MODELS ===
    "AI": ("../../wiki/concepts/AI-Automation", "AI"),
    "EliaAI": ("../../wiki/people/Elia", "Elia"),
    "OpenAI": ("../../wiki/people/OpenAI", "OpenAI"),
    "GPT": ("../../wiki/people/GPT", "GPT"),
    "Gemini": ("../../wiki/people/Gemini", "Gemini"),
    "Anthropic": ("../../wiki/people/Anthropic", "Anthropic"),
    "Agent": ("../../wiki/concepts/AI-Automation", "Agent"),
    "Agents": ("../../wiki/concepts/AI-Automation", "Agents"),
    "IA": ("../../wiki/concepts/AI-Automation", "IA"),
    "Bot": ("../../wiki/concepts/AI-Automation", "Bot"),
    "WatsonHelper": ("../../wiki/skills/MCP-Tools", "WatsonHelper"),
    "AITeamHelper": ("../../wiki/concepts/AI-Automation", "AITeamHelper"),
    # === IDE & TOOLS ===
    "Cursor": ("../../wiki/skills/Cursor-IDE", "Cursor"),
    "Windsurf": ("../../wiki/skills/Windsurf-IDE", "Windsurf"),
    "OpenCode": ("../../wiki/skills/OpenCode-CLI", "OpenCode"),
    "IDE": ("../../wiki/skills/Cursor-IDE", "IDE"),
    "Plugin": ("../../wiki/skills/Cursor-IDE", "Plugin"),
    "Extension": ("../../wiki/skills/Cursor-IDE", "Extension"),
    "Electron": ("../../wiki/skills/Cursor-IDE", "Electron"),
    # === JIRA & PROJECT ===
    "BEN": ("../../wiki/systems/Jira-Tickets-Index", "BEN"),
    "COBOUAGENC": ("../../wiki/systems/Jira-Tickets-Index", "COBOUAGENC"),
    "PROJ": ("../../wiki/systems/Jira-Tickets-Index", "PROJ"),
    "Issue": ("../../wiki/systems/Jira-Tickets-Index", "Issue"),
    "Issues": ("../../wiki/systems/Jira-Tickets-Index", "Issues"),
    "Project": ("../../wiki/systems/Jira-Tickets-Index", "Project"),
    "Board": ("../../wiki/systems/Jira-Tickets-Index", "Board"),
    "Sprint": ("../../wiki/systems/Jira-Tickets-Index", "Sprint"),
    "Epic": ("../../wiki/systems/Jira-Tickets-Index", "Epic"),
    # === CODING ===
    "Python": ("../../wiki/skills/Python-Scripting", "Python"),
    "JSON": ("../../wiki/concepts/API-Integration", "JSON"),
    "API": ("../../wiki/concepts/API-Integration", "API"),
    "GitHub": ("../../wiki/skills/Git-Version-Control", "GitHub"),
    "Git": ("../../wiki/skills/Git-Version-Control", "Git"),
    "HTML": ("../../wiki/skills/Web-Development", "HTML"),
    "Markdown": ("../../wiki/concepts/Documentation", "Markdown"),
    "Figma": ("../../wiki/skills/Design-Tools", "Figma"),
    "Framework": ("../../wiki/skills/Web-Development", "Framework"),
    "Library": ("../../wiki/skills/Python-Scripting", "Library"),
    "File": ("../../wiki/concepts/File-Management", "File"),
    "URL": ("../../wiki/concepts/API-Integration", "URL"),
    "Polar": ("../../wiki/skills/Polar-SCM", "Polar"),
    # === BUSINESS ===
    "Stripe": ("../../wiki/businesses/Bene2Luxe#stripe", "Stripe"),
    "Shopify": ("../../wiki/businesses/Bene2Luxe#shopify", "Shopify"),
    "Business": ("../../wiki/businesses/B2LUXE-BUSINESS", "Business"),
    "BUSINESS": ("../../wiki/businesses/B2LUXE-BUSINESS", "BUSINESS"),
    "Agency": ("../../wiki/businesses/CoBou-Agency", "Agency"),
    "LLC": ("../../wiki/businesses/B2LUXE-BUSINESS", "LLC"),
    "Payment": ("../../wiki/businesses/Bene2Luxe#payments", "Payment"),
    "Invoice": ("../../wiki/businesses/CoBou-Agency#invoicing", "Invoice"),
    # === WORKFLOW ===
    "Workflow": ("../../wiki/concepts/AI-Automation", "Workflow"),
    "Task": ("../../wiki/concepts/AI-Automation#tasks", "Task"),
    "Tasks": ("../../wiki/concepts/AI-Automation#tasks", "Tasks"),
    "Cascade": ("../../wiki/concepts/Cascade-Framework", "Cascade"),
    "PROMPT": ("../../wiki/concepts/Prompt-Engineering", "PROMPT"),
    "Prompt": ("../../wiki/concepts/Prompt-Engineering", "Prompt"),
    "Run": ("../../wiki/docs/Sessions", "Run"),
    "History": ("../../wiki/docs/Sessions", "History"),
    "Report": ("../../wiki/docs/Sessions", "Report"),
    "Docs": ("../../wiki/HOME", "Docs"),
    "Documents": ("../../wiki/HOME", "Documents"),
    # === CONTENT & MARKETING ===
    "Video": ("../../wiki/skills/Higgsfield-Video", "Video"),
    "Content": ("../../wiki/concepts/Marketing-Concepts", "Content"),
    "Mascoot": ("../../wiki/skills/Higgsfield-Video", "Mascoot"),
    "UGC": ("../../wiki/concepts/UGC", "UGC"),
    "Ads": ("../../wiki/concepts/Ads-Funnel", "Ads"),
    "CTA": ("../../wiki/concepts/Ads-Funnel#cta", "CTA"),
    "Hook": ("../../wiki/concepts/Ads-Funnel#hook", "Hook"),
    "Target": ("../../wiki/concepts/Ads-Funnel#targeting", "Target"),
    "Value": ("../../wiki/concepts/Pricing", "Value"),
    "Marketing": ("../../wiki/concepts/Marketing-Concepts", "Marketing"),
    # === ACTIONS ===
    "Edit": ("../../wiki/concepts/File-Management", "Edit"),
    "Create": ("../../wiki/concepts/File-Management", "Create"),
    "Delete": ("../../wiki/concepts/File-Management", "Delete"),
    "Download": ("../../wiki/concepts/File-Management", "Download"),
    "Upload": ("../../wiki/concepts/File-Management", "Upload"),
    "Send": ("../../wiki/channels/Telegram", "Send"),
    "Read": ("../../wiki/concepts/File-Management", "Read"),
    "Find": ("../../wiki/concepts/Search", "Find"),
    "List": ("../../wiki/concepts/Search", "List"),
    "Add": ("../../wiki/concepts/File-Management", "Add"),
    "Remove": ("../../wiki/concepts/File-Management", "Remove"),
    "Update": ("../../wiki/concepts/File-Management", "Update"),
    "Validate": ("../../wiki/skills/TypeScript-Development", "Validate"),
    "Filter": ("../../wiki/concepts/Search", "Filter"),
    # === MISC ===
    "Google": ("../../wiki/channels/Google", "Google"),
    "Search": ("../../wiki/channels/Google", "Search"),
    "Frameworks": ("../../wiki/skills/Web-Development", "Frameworks"),
    "STDIO": ("../../wiki/tools/MCP-Tools", "STDIO"),
    "Request": ("../../wiki/concepts/API-Integration", "Request"),
    "Response": ("../../wiki/concepts/API-Integration", "Response"),
    "Object": ("../../wiki/skills/Python-Scripting", "Object"),
    "Service": ("../../wiki/concepts/AI-Automation", "Service"),
    "Manager": ("../../wiki/concepts/AI-Automation", "Manager"),
    "Helper": ("../../wiki/concepts/AI-Automation", "Helper"),
    "Helpers": ("../../wiki/concepts/AI-Automation", "Helpers"),
    "Remote": ("../../wiki/systems/SSH-Servers", "Remote"),
    "Local": ("../../wiki/systems/Docker-Servers", "Local"),
    "Cloud": ("../../wiki/systems/Docker-Servers", "Cloud"),
    "Host": ("../../wiki/systems/Docker-Servers", "Host"),
    "Server": ("../../wiki/systems/Docker-Servers", "Server"),
    "GPU": ("../../wiki/systems/Docker-Servers", "GPU"),
    # === EXTRA KEYWORDS ===
    "Framework": ("../../wiki/skills/Web-Development", "Framework"),
    "Report": ("../../wiki/docs/Sessions", "Report"),
    "Reports": ("../../wiki/docs/Sessions", "Reports"),
    "Summary": ("../../wiki/docs/Sessions", "Summary"),
    "List": ("../../wiki/concepts/Search", "List"),
    "History": ("../../wiki/docs/Sessions", "History"),
    "Filter": ("../../wiki/concepts/Search", "Filter"),
    "Content": ("../../wiki/concepts/Marketing-Concepts", "Content"),
    "Ads": ("../../wiki/concepts/Ads-Funnel", "Ads"),
    "Ads": ("../../wiki/concepts/Ads-Funnel", "Ads"),
    "Snapchat": ("../../wiki/channels/Snapchat", "Snapchat"),
    "Army": ("../../wiki/channels/Snapchat#army", "Army"),
    "Chat": ("../../wiki/channels/Telegram", "Chat"),
    "Message": ("../../wiki/channels/Telegram", "Message"),
    "Messages": ("../../wiki/channels/Telegram", "Messages"),
    "Activity": ("../../wiki/docs/Sessions", "Activity"),
    "Output": ("../../wiki/concepts/File-Management", "Output"),
    "Input": ("../../wiki/concepts/File-Management", "Input"),
    "Category": ("../../wiki/concepts/Marketing-Concepts", "Category"),
    "Script": ("../../wiki/concepts/Marketing-Concepts", "Script"),
    "Scripts": ("../../wiki/concepts/Marketing-Concepts", "Scripts"),
    "Episode": ("../../wiki/concepts/Marketing-Concepts", "Episode"),
    "Adventure": ("../../wiki/concepts/Marketing-Concepts", "Adventure"),
    "Plot": ("../../wiki/concepts/Marketing-Concepts", "Plot"),
    "Fashion": ("../../wiki/concepts/Luxury-Brands", "Fashion"),
    "Lifestyle": ("../../wiki/concepts/Marketing-Concepts", "Lifestyle"),
    "Premium": ("../../wiki/concepts/Pricing", "Premium"),
    "Mercury": ("../../wiki/businesses/CoBou-Agency", "Mercury"),
    "PayPal": ("../../wiki/businesses/Bene2Luxe#payments", "PayPal"),
    "Wise": ("../../wiki/businesses/Wise", "Wise"),
    "Switzerland": (
        "../../wiki/concepts/Location-Targeting#switzerland",
        "Switzerland",
    ),
    "Swissquote": ("../../wiki/businesses/Swissquote", "Swissquote"),
    "Script": ("../../wiki/concepts/Marketing-Concepts", "Script"),
    "Composer": ("../../wiki/skills/Web-Development", "Composer"),
    "Range": ("../../wiki/businesses/Bene2Luxe#sizing", "Range"),
    "Size": ("../../wiki/businesses/Bene2Luxe#sizing", "Size"),
    "Sizes": ("../../wiki/businesses/Bene2Luxe#sizing", "Sizes"),
    "Prix": ("../../wiki/concepts/Pricing", "Prix"),
    "Price": ("../../wiki/concepts/Pricing", "Price"),
    "Ticket": ("../../wiki/systems/Jira-Tickets-Index", "Ticket"),
    "Workspace": ("../../wiki/skills/Cursor-IDE", "Workspace"),
    "Path": ("../../wiki/concepts/File-Management", "Path"),
    "ID": ("../../wiki/systems/Jira-Tickets-Index", "ID"),
    "IDs": ("../../wiki/systems/Jira-Tickets-Index", "IDs"),
    "Date": ("../../wiki/topics/Infrastructure-Timeline", "Date"),
    "Time": ("../../wiki/topics/Infrastructure-Timeline", "Time"),
    "Quality": ("../../wiki/concepts/Marketing-Concepts", "Quality"),
    "Focus": ("../../wiki/concepts/Marketing-Concepts", "Focus"),
    "Digital": ("../../wiki/concepts/AI-Automation", "Digital"),
    "Parallel": ("../../wiki/concepts/AI-Automation", "Parallel"),
    "Creative": ("../../wiki/concepts/Marketing-Concepts", "Creative"),
    "Lookup": ("../../wiki/concepts/Search", "Lookup"),
    "Extra": ("../../wiki/concepts/Marketing-Concepts", "Extra"),
    "Pause": ("../../wiki/concepts/Marketing-Concepts", "Pause"),
    "Complete": ("../../wiki/docs/Sessions", "Complete"),
    "COMPLETE": ("../../wiki/docs/Sessions", "COMPLETE"),
    "Available": ("../../wiki/concepts/AI-Automation", "Available"),
    "Extract": ("../../wiki/concepts/File-Management", "Extract"),
    "Extracting": ("../../wiki/concepts/File-Management", "Extracting"),
    "Built": ("../../wiki/skills/Web-Development", "Built"),
    "Multiple": ("../../wiki/concepts/AI-Automation", "Multiple"),
    "Direct": ("../../wiki/concepts/AI-Automation", "Direct"),
    "Since": ("../../wiki/topics/Infrastructure-Timeline", "Since"),
    "IMPORTANT": ("../../wiki/concepts/Prompt-Engineering", "IMPORTANT"),
    "RECOMMENDED": ("../../wiki/concepts/Prompt-Engineering", "RECOMMENDED"),
    "VERIFY": ("../../wiki/concepts/Prompt-Engineering", "VERIFY"),
    "CONTEXT": ("../../wiki/concepts/Prompt-Engineering", "CONTEXT"),
    "DELIVERABLES": ("../../wiki/concepts/Prompt-Engineering", "DELIVERABLES"),
    "TODOs": ("../../wiki/concepts/AI-Automation", "TODOs"),
    "ALWAYS": ("../../wiki/concepts/Prompt-Engineering", "ALWAYS"),
    "NOT": ("../../wiki/concepts/Prompt-Engineering", "NOT"),
    "SKILLS": ("../../wiki/skills/Index", "SKILLS"),
    "TOOLS": ("../../wiki/tools/Index", "TOOLS"),
    "RULES": ("../../wiki/concepts/Prompt-Engineering", "RULES"),
    "EPISODE": ("../../wiki/concepts/Marketing-Concepts", "EPISODE"),
    "ADVENTURE": ("../../wiki/concepts/Marketing-Concepts", "ADVENTURE"),
    "UP": ("../../wiki/concepts/Prompt-Engineering", "UP"),
    # === MORE KEYWORDS ===
    "Mascoot": ("../../wiki/skills/Higgsfield-Video", "Mascoot"),
    "Activity": ("../../wiki/docs/Sessions", "Activity"),
    "Cursor": ("../../wiki/skills/Cursor-IDE", "Cursor"),
    "Git": ("../../wiki/skills/Git-Version-Control", "Git"),
    "Windsurf": ("../../wiki/skills/Windsurf-IDE", "Windsurf"),
    "Polar": ("../../wiki/skills/Polar-SCM", "Polar"),
    "Work": ("../../wiki/docs/Sessions", "Work"),
    "Result": ("../../wiki/docs/Sessions", "Result"),
    "Results": ("../../wiki/docs/Sessions", "Results"),
    "Format": ("../../wiki/concepts/File-Management", "Format"),
    "Markdown": ("../../wiki/concepts/Documentation", "Markdown"),
    "HTML": ("../../wiki/skills/Web-Development", "HTML"),
    "JSON": ("../../wiki/concepts/API-Integration", "JSON"),
    "URL": ("../../wiki/concepts/API-Integration", "URL"),
    "Keys": ("../../wiki/concepts/File-Management", "Keys"),
    "Key": ("../../wiki/concepts/File-Management", "Key"),
    "Length": ("../../wiki/concepts/File-Management", "Length"),
    "Version": ("../../wiki/skills/Git-Version-Control", "Version"),
    "Versions": ("../../wiki/skills/Git-Version-Control", "Versions"),
    "Check": ("../../wiki/topics/Infrastructure-Timeline", "Check"),
    "Checking": ("../../wiki/topics/Infrastructure-Timeline", "Checking"),
    "Error": ("../../wiki/topics/Infrastructure-Timeline", "Error"),
    "Status": ("../../wiki/topics/Infrastructure-Timeline", "Status"),
    "INFO": ("../../wiki/topics/Infrastructure-Timeline", "INFO"),
    "User": ("../../wiki/people/Elia", "User"),
    "Users": ("../../wiki/people/Elia", "Users"),
    "Assistant": ("../../wiki/people/Elia", "Assistant"),
    "Product": ("../../wiki/businesses/Bene2Luxe#products", "Product"),
    "Products": ("../../wiki/businesses/Bene2Luxe#products", "Products"),
    "Order": ("../../wiki/businesses/B2LUXE-BUSINESS#orders", "Order"),
    "Orders": ("../../wiki/businesses/B2LUXE-BUSINESS#orders", "Orders"),
    "Invoice": ("../../wiki/businesses/CoBou-Agency#invoicing", "Invoice"),
    "Ship": ("../../wiki/businesses/B2LUXE-BUSINESS#shipping", "Ship"),
    "Shipped": ("../../wiki/businesses/B2LUXE-BUSINESS#shipping", "Shipped"),
    "Shipping": ("../../wiki/businesses/B2LUXE-BUSINESS#shipping", "Shipping"),
    "Delivery": ("../../wiki/businesses/B2LUXE-BUSINESS#shipping", "Delivery"),
    "Account": ("../../wiki/businesses/Bene2Luxe#account", "Account"),
    "Accounts": ("../../wiki/businesses/Bene2Luxe#account", "Accounts"),
    "Campaign": ("../../wiki/concepts/Ads-Funnel", "Campaign"),
    "Revenue": ("../../wiki/businesses/Bene2Luxe#revenue", "Revenue"),
    "Sales": ("../../wiki/businesses/Bene2Luxe#revenue", "Sales"),
    "Traffic": ("../../wiki/concepts/Marketing-Concepts", "Traffic"),
    "Views": ("../../wiki/concepts/Marketing-Concepts", "Views"),
    "Video": ("../../wiki/skills/Higgsfield-Video", "Video"),
    "Images": ("../../wiki/skills/Higgsfield-Video", "Images"),
    "Thumbnail": ("../../wiki/skills/Higgsfield-Video", "Thumbnail"),
    "Thumbnails": ("../../wiki/skills/Higgsfield-Video", "Thumbnails"),
    "Brand": ("../../wiki/concepts/Luxury-Brands", "Brand"),
    "Brands": ("../../wiki/concepts/Luxury-Brands", "Brands"),
    "Chanel": ("../../wiki/concepts/Luxury-Brands#chanel", "Chanel"),
    "Dior": ("../../wiki/concepts/Luxury-Brands#dior", "Dior"),
    "Gucci": ("../../wiki/concepts/Luxury-Brands#gucci", "Gucci"),
    "Louis Vuitton": (
        "../../wiki/concepts/Luxury-Brands#louis-vuitton",
        "Louis Vuitton",
    ),
    "LV": ("../../wiki/concepts/Luxury-Brands#louis-vuitton", "LV"),
    "Vuitton": ("../../wiki/concepts/Luxury-Brands#louis-vuitton", "Vuitton"),
    "Balenciaga": ("../../wiki/concepts/Luxury-Brands#balenciaga", "Balenciaga"),
    "Hermès": ("../../wiki/concepts/Luxury-Brands#hermes", "Hermès"),
    "Prada": ("../../wiki/concepts/Luxury-Brands#prada", "Prada"),
    "YSL": ("../../wiki/concepts/Luxury-Brands#ysl", "YSL"),
    "Saint Laurent": ("../../wiki/concepts/Luxury-Brands#ysl", "Saint Laurent"),
    "Versace": ("../../wiki/concepts/Luxury-Brands#versace", "Versace"),
    "Burberry": ("../../wiki/concepts/Luxury-Brands#burberry", "Burberry"),
    "Celine": ("../../wiki/concepts/Luxury-Brands#celine", "Celine"),
    "Fendi": ("../../wiki/concepts/Luxury-Brands#fendi", "Fendi"),
    "Loewe": ("../../wiki/concepts/Luxury-Brands#loewe", "Loewe"),
    "Givenchy": ("../../wiki/concepts/Luxury-Brands#givenchy", "Givenchy"),
    "Valentino": ("../../wiki/concepts/Luxury-Brands#valentino", "Valentino"),
    "Bottega Veneta": (
        "../../wiki/concepts/Luxury-Brands#bottega-veneta",
        "Bottega Veneta",
    ),
    "Coach": ("../../wiki/concepts/Luxury-Brands#coach", "Coach"),
    "Michael Kors": ("../../wiki/concepts/Luxury-Brands#michael-kors", "Michael Kors"),
    "Kate Spade": ("../../wiki/concepts/Luxury-Brands#kate-spade", "Kate Spade"),
    "Tory Burch": ("../../wiki/concepts/Luxury-Brands#tory-burch", "Tory Burch"),
    "MCM": ("../../wiki/concepts/Luxury-Brands#mcm", "MCM"),
    "Longchamp": ("../../wiki/concepts/Luxury-Brands#longchamp", "Longchamp"),
    "Sandro": ("../../wiki/concepts/Luxury-Brands#sandro", "Sandro"),
    "Maje": ("../../wiki/concepts/Luxury-Brands#maje", "Maje"),
    "Claudie Pierlot": (
        "../../wiki/concepts/Luxury-Brands#claudie-pierlot",
        "Claudie Pierlot",
    ),
    "The North Face": (
        "../../wiki/concepts/Luxury-Brands#the-north-face",
        "The North Face",
    ),
    "Canada Goose": ("../../wiki/concepts/Luxury-Brands#canada-goose", "Canada Goose"),
    "Moncler": ("../../wiki/concepts/Luxury-Brands#moncler", "Moncler"),
    "Stone Island": ("../../wiki/concepts/Luxury-Brands#stone-island", "Stone Island"),
    "Palm Angels": ("../../wiki/concepts/Luxury-Brands#palm-angels", "Palm Angels"),
    "Off-White": ("../../wiki/concepts/Luxury-Brands#off-white", "Off-White"),
    "Fear of God": ("../../wiki/concepts/Luxury-Brands#fear-of-god", "Fear of God"),
    "Amiri": ("../../wiki/concepts/Luxury-Brands#amiri", "Amiri"),
    "Rhude": ("../../wiki/concepts/Luxury-Brands#rhude", "Rhude"),
    "Represent": ("../../wiki/concepts/Luxury-Brands#represent", "Represent"),
    "Etre Cecile": ("../../wiki/concepts/Luxury-Brands#etre-cecile", "Etre Cecile"),
    "Alyx": ("../../wiki/concepts/Luxury-Brands#alyx", "Alyx"),
    "1017 ALYX 9SM": ("../../wiki/concepts/Luxury-Brands#alyx", "1017 ALYX 9SM"),
    # === FINAL KEYWORDS ===
    "Tools": ("../../wiki/tools/Index", "Tools"),
    "Skills": ("../../wiki/skills/Index", "Skills"),
    "SKILLS": ("../../wiki/skills/Index", "SKILLS"),
    "TOOLS": ("../../wiki/tools/Index", "TOOLS"),
    "Video": ("../../wiki/skills/Higgsfield-Video", "Video"),
}


def link_file(filepath: Path, dry_run: bool = False) -> tuple[int, dict]:
    """Process a single file. Returns (link_count, stats_dict)."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except:
        return 0, {}

    stats = defaultdict(int)
    total = 0

    for keyword, (target, display) in WIKI_LINKS.items():
        # Skip if already linked
        if f"[[{target}" in content or f"|{keyword}]]" in content:
            continue

        # Case-insensitive word boundary match
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
    files = list(base.glob("**/*.md"))

    print(f"🔗 Master Bulk Linker")
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
            if not dry_run and count > 5:
                print(f"  [{i}/{len(files)}] {filepath.name}: +{count}")

    print()
    print(f"✅ Processed {total_files}/{len(files)} files")
    print(f"   Total links added: {total_links}")

    if all_stats:
        print()
        print("Top linked keywords:")
        for k, v in sorted(all_stats.items(), key=lambda x: -x[1])[:20]:
            print(f"   {k}: {v}")

    if dry_run:
        print("\n⚠️  Dry run - no files were modified")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(args.dry_run)
