#!/usr/bin/env python3
"""
SEO Audit — llms.txt Checker
Checks if llms.txt exists and analyzes its content.

Usage: python3 fetch_llms.py <DOMAIN>
Output: /tmp/seo-audit/llms_data.json
"""

import json
import sys
import urllib.request
import ssl
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_llms.py <DOMAIN>", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1]
    if domain.startswith("http"):
        domain = domain.split("//")[1].rstrip("/")

    urls_to_check = [
        f"https://{domain}/llms.txt",
        f"https://{domain}/llms-full.txt",
    ]

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    result = {
        "domain": domain,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "files": {},
        "summary": "",
    }

    for url in urls_to_check:
        filename = url.split("/")[-1]
        file_result = {"url": url, "exists": False, "content": "", "line_count": 0, "errors": []}

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)",
            })
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            content = resp.read(1048576).decode("utf-8", errors="replace")  # 1MB max
            file_result["exists"] = True
            file_result["content"] = content
            file_result["line_count"] = len(content.split("\n"))
            file_result["size_bytes"] = len(content.encode("utf-8"))
        except urllib.error.HTTPError as e:
            file_result["errors"].append(f"HTTP {e.code}")
        except Exception as e:
            file_result["errors"].append(str(e))

        result["files"][filename] = file_result

    # Summary
    llms_txt = result["files"].get("llms.txt", {})
    llms_full = result["files"].get("llms-full.txt", {})

    if llms_txt.get("exists") and llms_full.get("exists"):
        result["summary"] = "Both llms.txt and llms-full.txt present — excellent AI discoverability"
    elif llms_txt.get("exists"):
        result["summary"] = "llms.txt present (no llms-full.txt) — good, consider adding full version"
    elif llms_full.get("exists"):
        result["summary"] = "llms-full.txt present (no llms.txt) — add llms.txt as entry point"
    else:
        result["summary"] = "No llms.txt found — not critical but emerging standard for AI search"

    with open("/tmp/seo-audit/llms_data.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "status": "ok",
        "llms_txt_exists": llms_txt.get("exists", False),
        "llms_full_exists": llms_full.get("exists", False),
        "summary": result["summary"],
        "output": "/tmp/seo-audit/llms_data.json",
    }, indent=2))


if __name__ == "__main__":
    main()
