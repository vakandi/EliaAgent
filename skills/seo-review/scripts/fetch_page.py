#!/usr/bin/env python3
"""
SEO Audit — Page Fetcher
Fetches a URL and extracts all SEO-relevant data into a structured JSON file.

Usage: python3 fetch_page.py <URL>
Output: /tmp/seo-audit/page_data.json
"""

import json
import re
import sys
import urllib.request
import urllib.error
import ssl
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
from datetime import datetime


class SEOHTMLParser(HTMLParser):
    """Extract SEO-relevant elements from HTML."""

    def __init__(self):
        super().__init__()
        self.in_head = False
        self.head_html = ""
        self.head_raw_start = 0
        self.title = ""
        self.meta_tags = []
        self.canonical = None
        self.hreflangs = []
        self.jsonld_blocks = []
        self.headings = []
        self.images = []
        self.links = []
        self.og_tags = {}
        self.twitter_tags = {}
        self.meta_robots = None
        self.viewport = None
        self.body_text_parts = []
        self.in_script = False
        self.in_style = False
        self.script_count = 0
        self.style_count = 0
        self.current_tag_stack = []
        self.heading_levels = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag_stack.append(tag)

        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head = False
        elif tag == "script":
            self.in_script = True
            self.script_count += 1
            if attrs_dict.get("type") == "application/ld+json":
                # We'll capture content in handle_data
                pass
        elif tag == "style":
            self.in_style = True
            self.style_count += 1

        # Title
        if tag == "title" and self.in_head:
            pass  # captured in handle_data

        # Meta tags
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            http_equiv = attrs_dict.get("http-equiv", "").lower()

            self.meta_tags.append({
                "name": name,
                "property": prop,
                "content": content,
                "http_equiv": http_equiv,
            })

            if name == "robots":
                self.meta_robots = content
            if name == "viewport":
                self.viewport = content
            if prop.startswith("og:"):
                self.og_tags[prop] = content
            if prop.startswith("twitter:"):
                self.twitter_tags[prop] = content

        # Canonical
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            if rel == "canonical":
                self.canonical = href
            if rel == "alternate" and "hreflang" in attrs_dict:
                self.hreflangs.append({
                    "hreflang": attrs_dict.get("hreflang", ""),
                    "href": href,
                })

        # Headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.headings.append({"level": level, "tag": tag, "text": ""})
            self.heading_levels.append(level)

        # Images
        if tag == "img":
            self.images.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", ""),
                "width": attrs_dict.get("width", ""),
                "height": attrs_dict.get("height", ""),
                "loading": attrs_dict.get("loading", ""),
            })

        # Links (internal/external determined later)
        if tag == "a":
            href = attrs_dict.get("href", "")
            self.links.append({
                "href": href,
                "text": "",  # filled in handle_data
            })

    def handle_endtag(self, tag):
        if self.current_tag_stack and self.current_tag_stack[-1] == tag:
            self.current_tag_stack.pop()
        if tag == "head":
            self.in_head = False
        if tag == "script":
            self.in_script = False
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        # Title
        if self.in_head and self.current_tag_stack and self.current_tag_stack[-1] == "title":
            self.title += data

        # JSON-LD
        if self.current_tag_stack and self.current_tag_stack[-1] == "script":
            # Check if this is inside a JSON-LD script tag
            # We detect by checking if the accumulated content looks like JSON
            pass  # We'll collect JSON-LD in a second pass

        # Heading text
        if self.headings and self.current_tag_stack:
            last_heading = self.headings[-1]
            if self.current_tag_stack[-1] in ("h1", "h2", "h3", "h4", "h5", "h6"):
                last_heading["text"] += data

        # Link text
        if self.links and self.current_tag_stack and self.current_tag_stack[-1] == "a":
            self.links[-1]["text"] += data

        # Body text (skip script/style content)
        if not self.in_script and not self.in_style and not self.in_head:
            stripped = data.strip()
            if stripped:
                self.body_text_parts.append(stripped)


def extract_jsonld(html):
    """Extract all JSON-LD blocks from HTML."""
    blocks = []
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
        raw = match.group(1).strip()
        try:
            parsed = json.loads(raw)
            blocks.append(parsed)
        except json.JSONDecodeError:
            blocks.append({"_parse_error": True, "_raw": raw[:500]})
    return blocks


def extract_jsonld_from_parser(html):
    """Second pass to get JSON-LD after parser has run."""
    return extract_jsonld(html)


def count_words(text):
    """Count words in text."""
    return len(re.findall(r'\b\w+\b', text))


def check_heading_hierarchy(headings):
    """Check for heading hierarchy issues."""
    issues = []
    h1_count = sum(1 for h in headings if h["level"] == 1)

    if h1_count == 0:
        issues.append("No H1 tag found")
    elif h1_count > 1:
        issues.append(f"Multiple H1 tags found ({h1_count})")

    prev_level = 0
    for h in headings:
        if h["level"] > prev_level + 1 and prev_level > 0:
            issues.append(f"Skipped heading level: H{prev_level} → H{h['level']}")
        prev_level = h["level"]

    return issues


def fetch_sitemap(domain, ctx):
    sitemap_url = f"https://{domain}/sitemap.xml"
    try:
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": "SEO-Audit/1.0"})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = resp.read(5_000_000).decode("utf-8", errors="replace")
        urls = re.findall(r"<loc>(.*?)</loc>", body)
        lastmods = re.findall(r"<lastmod>(.*?)</lastmod>", body)
        return {
            "exists": True,
            "url_count": len(urls),
            "urls": urls[:50],
            "lastmods": lastmods[:50],
            "has_lastmod": len(lastmods) > 0,
        }
    except Exception:
        return {"exists": False, "url_count": 0, "urls": [], "lastmods": [], "has_lastmod": False}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_page.py <URL>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Create output directory
    import os
    os.makedirs("/tmp/seo-audit", exist_ok=True)

    # SSL context (permissive for audit purposes)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    result = {
        "url": url,
        "domain": domain,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fetch": {},
        "meta": {},
        "headings": [],
        "heading_issues": [],
        "images": [],
        "links": {"internal": [], "external": [], "total": 0, "internal_count": 0, "external_count": 0},
        "jsonld": [],
        "og_tags": {},
        "twitter_tags": {},
        "body_word_count": 0,
        "meta_robots": None,
        "meta_viewport": None,
        "canonical": None,
        "hreflangs": [],
        "script_count": 0,
        "style_count": 0,
        "html_size_bytes": 0,
        "render_blocking_scripts": 0,
        "preconnect_count": 0,
        "preload_count": 0,
        "is_csr_shell": False,
        "sitemap": {},
        "errors": [],
    }

    # Fetch the page
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        status_code = resp.getcode()
        headers = dict(resp.headers)
        html_bytes = resp.read(524288)  # 512KB max
        html = html_bytes.decode("utf-8", errors="replace")
        result["html_size_bytes"] = len(html_bytes)

        # Get final URL (after redirects)
        final_url = resp.url if hasattr(resp, 'url') else url
        if final_url != url:
            result["fetch"]["redirected_from"] = url
            url = final_url

        result["fetch"]["status_code"] = status_code
        result["fetch"]["final_url"] = final_url
        result["fetch"]["headers"] = headers
        result["fetch"]["content_type"] = headers.get("Content-Type", "")
        result["fetch"]["server"] = headers.get("Server", "")
        result["fetch"]["x_robots_tag"] = headers.get("X-Robots-Tag", None)
        result["fetch"]["cache_control"] = headers.get("Cache-Control", "")
        result["fetch"]["content_length"] = int(headers.get("Content-Length", 0))

        # Parse HTML
        parser = SEOHTMLParser()
        try:
            parser.feed(html)
        except Exception as e:
            result["errors"].append(f"HTML parse error: {str(e)}")

        # Title
        result["meta"]["title"] = parser.title.strip()
        result["meta"]["title_length"] = len(parser.title.strip())

        # Meta tags
        result["meta"]["tags"] = parser.meta_tags

        # Canonical
        result["canonical"] = parser.canonical

        # Hreflangs
        result["hreflangs"] = parser.hreflangs

        # JSON-LD (second pass)
        result["jsonld"] = extract_jsonld(html)

        # Headings
        result["headings"] = parser.headings
        result["heading_issues"] = check_heading_hierarchy(parser.headings)

        # H1 text
        h1s = [h["text"].strip() for h in parser.headings if h["level"] == 1]
        result["meta"]["h1"] = h1s

        # Images
        result["images"] = parser.images
        result["meta"]["image_count"] = len(parser.images)
        result["meta"]["images_without_alt"] = sum(1 for img in parser.images if not img["alt"].strip())

        # Links
        for link in parser.links:
            href = link["href"]
            if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                continue
            full_url = urljoin(url, href)
            link["resolved_url"] = full_url
            link_parsed = urlparse(full_url)
            if link_parsed.netloc == domain or link_parsed.netloc == "":
                result["links"]["internal"].append(link)
            else:
                result["links"]["external"].append(link)

        result["links"]["internal_count"] = len(result["links"]["internal"])
        result["links"]["external_count"] = len(result["links"]["external"])
        result["links"]["total"] = result["links"]["internal_count"] + result["links"]["external_count"]

        # OG / Twitter
        result["og_tags"] = parser.og_tags
        result["twitter_tags"] = parser.twitter_tags

        # Meta robots / viewport
        result["meta_robots"] = parser.meta_robots
        result["meta_viewport"] = parser.viewport

        # Word count
        body_text = " ".join(parser.body_text_parts)
        result["body_word_count"] = count_words(body_text)

        # Script/style count
        result["script_count"] = parser.script_count
        result["style_count"] = parser.style_count

        # Detect CSR shell (empty body = JS-dependent)
        result["is_csr_shell"] = (
            result["body_word_count"] < 50
            and result["script_count"] > 2
        )

        # Detect if there are render-blocking scripts in head
        head_html = html[:html.find("</head>") + 7] if "</head>" in html.lower() else html[:5000]
        blocking_scripts = re.findall(r'<script(?![^>]*\b(async|defer|type=["\']module))[^>]*src=["\'][^"\']+["\']', head_html, re.I)
        result["render_blocking_scripts"] = len(blocking_scripts)

        # Check for preconnect/preload hints
        preconnects = re.findall(r'rel=["\']preconnect["\']', html, re.I)
        preloads = re.findall(r'rel=["\']preload["\']', html, re.I)
        result["preconnect_count"] = len(preconnects)
        result["preload_count"] = len(preloads)

        # Fetch and parse sitemap
        result["sitemap"] = fetch_sitemap(domain, ctx)

    except urllib.error.HTTPError as e:
        result["fetch"]["status_code"] = e.code
        result["fetch"]["error"] = str(e)
        result["errors"].append(f"HTTP {e.code}: {e.reason}")
    except Exception as e:
        result["fetch"]["error"] = str(e)
        result["errors"].append(f"Fetch error: {str(e)}")

    # Save
    with open("/tmp/seo-audit/page_data.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "status": "ok" if not result["errors"] else "errors",
        "url": url,
        "status_code": result["fetch"].get("status_code"),
        "title": result["meta"].get("title", ""),
        "h1": result["meta"].get("h1", []),
        "word_count": result["body_word_count"],
        "links": result["links"]["total"],
        "images": result["meta"].get("image_count", 0),
        "jsonld_blocks": len(result["jsonld"]),
        "is_csr_shell": result["is_csr_shell"],
        "errors": result["errors"],
        "output": "/tmp/seo-audit/page_data.json",
    }, indent=2))


if __name__ == "__main__":
    main()
