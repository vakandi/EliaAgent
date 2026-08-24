#!/usr/bin/env python3
"""
SEO Audit — Robots.txt Fetcher
Fetches and analyzes robots.txt for a domain.

Usage: python3 fetch_robots.py <DOMAIN>
Output: /tmp/seo-audit/robots_data.json
"""

import json
import re
import sys
import urllib.request
import ssl
from datetime import datetime


def parse_robots_txt(content):
    """Parse robots.txt and extract directives."""
    rules = {}
    sitemaps = []
    crawl_delays = {}

    current_agent = None
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()

            if key == "user-agent":
                current_agent = value
                if current_agent not in rules:
                    rules[current_agent] = {"allow": [], "disallow": []}
            elif key == "allow" and current_agent:
                rules[current_agent]["allow"].append(value)
            elif key == "disallow" and current_agent:
                rules[current_agent]["disallow"].append(value)
            elif key == "sitemap":
                sitemaps.append(value)
            elif key == "crawl-delay" and current_agent:
                crawl_delays[current_agent] = value

    # Check for common AI crawlers
    ai_crawlers = {
        "GPTBot": "OpenAI (training + retrieval)",
        "ChatGPT-User": "OpenAI (real-time browsing)",
        "OAI-SearchBot": "OpenAI (search features)",
        "ClaudeBot": "Anthropic (content retrieval)",
        "Anthropic-ai": "Anthropic (training)",
        "PerplexityBot": "Perplexity (search retrieval)",
        "Google-Extended": "Google (AI training)",
        "cohere-ai": "Cohere (training)",
        "Bytespider": "ByteDance (training)",
        "Amazonbot": "Amazon (Alexa/AI)",
        "Meta-ExternalAgent": "Meta (AI training)",
    }

    crawler_status = {}
    for crawler, desc in ai_crawlers.items():
        # Check rules (exact match, wildcard *, or case-insensitive)
        matched_rules = None
        for agent_pattern in rules:
            if agent_pattern.lower() == crawler.lower() or agent_pattern == "*":
                matched_rules = rules[agent_pattern]
                if agent_pattern.lower() == crawler.lower():
                    break  # Specific rule wins

        if matched_rules is None:
            crawler_status[crawler] = {
                "description": desc,
                "status": "no_rule",
                "verdict": "allowed (default)",
                "disallow_paths": [],
            }
        else:
            disallow_paths = matched_rules["disallow"]
            # If Disallow: / exists, it's blocked
            blocked = "/" in disallow_paths and len(disallow_paths) == 1
            crawler_status[crawler] = {
                "description": desc,
                "status": "blocked" if blocked else "custom_rules",
                "verdict": "blocked" if blocked else "has specific rules",
                "disallow_paths": disallow_paths,
                "allow_paths": matched_rules["allow"],
            }

    # Check if CSS/JS are blocked
    css_js_blocked = False
    for agent, agent_rules in rules.items():
        if agent == "*":
            for path in agent_rules["disallow"]:
                if any(ext in path.lower() for ext in [".js", ".css", "/static/", "/assets/"]):
                    css_js_blocked = True
                    break

    return {
        "rules": rules,
        "sitemaps": sitemaps,
        "crawl_delays": crawl_delays,
        "ai_crawler_status": crawler_status,
        "css_js_blocked": css_js_blocked,
        "has_sitemap_directive": len(sitemaps) > 0,
        "has_wildcard_rule": "*" in rules,
        "wildcard_disallows_all": "/" in rules.get("*", {}).get("disallow", []),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_robots.py <DOMAIN>", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1]
    if domain.startswith("http"):
        domain = domain.split("//")[1].rstrip("/")

    robots_url = f"https://{domain}/robots.txt"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    result = {
        "domain": domain,
        "robots_url": robots_url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status_code": None,
        "content": "",
        "parse": None,
        "errors": [],
    }

    try:
        req = urllib.request.Request(robots_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)",
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        result["status_code"] = resp.getcode()
        content = resp.read(524288).decode("utf-8", errors="replace")
        result["content"] = content
        result["parse"] = parse_robots_txt(content)
    except urllib.error.HTTPError as e:
        result["status_code"] = e.code
        result["errors"].append(f"HTTP {e.code}: {e.reason}")
        if e.code == 404:
            result["errors"].append("No robots.txt found — all crawlers allowed by default")
    except Exception as e:
        result["errors"].append(f"Error: {str(e)}")

    with open("/tmp/seo-audit/robots_data.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "status": "ok" if not result["errors"] else "errors",
        "status_code": result["status_code"],
        "sitemaps_found": result["parse"]["sitemaps"] if result["parse"] else [],
        "css_js_blocked": result["parse"]["css_js_blocked"] if result["parse"] else None,
        "ai_crawlers": {
            k: v["verdict"] for k, v in (result["parse"]["ai_crawler_status"].items() if result["parse"] else {})
        },
        "errors": result["errors"],
        "output": "/tmp/seo-audit/robots_data.json",
    }, indent=2))


if __name__ == "__main__":
    main()
