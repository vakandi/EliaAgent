---
name: seo-review
description: >
  Full SEO, AEO, and GEO audit for any website URL. Crawl the page, check robots.txt, 
  sitemaps, meta tags, structured data, Core Web Vitals signals, heading hierarchy, 
  internal links, AI search readiness, and produce a scored audit report with prioritized 
  fixes. Use this skill whenever the user provides a URL and asks for an SEO review, 
  site audit, SEO check, SEO score, website analysis, search optimization review, 
  technical SEO audit, or wants to know "how is my site doing SEO-wise." Even if they 
  just paste a URL and say "review this" or "check this site" — trigger this skill. 
  Also trigger on requests like "is my site optimized for AI search", "how does my site 
  look to Google", "what's wrong with my SEO", or "audit my website."
---

# SEO Review — Full Site Audit Skill

You are an SEO auditor. Given a URL, you perform a comprehensive technical + content + 
AI-readiness audit and produce a scored report with actionable fixes.

**Reference doc:** `docs/SEO_BEST_PRACTICES_2026.md` (root of your-saas workspace) — 
the authoritative best practices guide. Read relevant sections as needed during the audit.

---

## Audit Workflow

### Phase 1: Fetch & Discover (automated via script)

Run the fetch script to collect raw data:

```bash
python3 <skill-dir>/scripts/fetch_page.py <URL>
```

This produces a JSON file at `/tmp/seo-audit/page_data.json` containing:
- HTTP status, headers, redirect chain
- Full HTML (truncated to 500KB)
- `<head>` meta tags extracted
- Heading hierarchy
- All internal/external links
- Images with src, alt, width, height
- Structured data (JSON-LD) blocks
- Open Graph and Twitter Card tags
- robots.txt content (fetched separately)
- Sitemap data (URL count, lastmod dates — included in fetch_page.py output)
- `<meta name="robots">` and `X-Robots-Tag` header

Then fetch and parse robots.txt:

```bash
python3 <skill-dir>/scripts/fetch_robots.py <DOMAIN>
```

And check for llms.txt:

```bash
python3 <skill-dir>/scripts/fetch_llms.py <DOMAIN>
```

### Phase 2: Analyze (you do this manually using the data)

Read `/tmp/seo-audit/page_data.json` and evaluate against the **40-Check SEO Scorecard** 
(35 base checks + 5 AI/GEO bonus checks — see `references/scorecard.md` for the full list). For each check, assign:
- **PASS** — meets the standard
- **WARN** — exists but suboptimal
- **FAIL** — missing or broken
- **N/A** — not applicable (e.g., no images = image checks N/A)

Use these analysis rules:

#### Technical SEO (10 checks, 25% weight)
1. **robots.txt** — allows CSS/JS, has Sitemap directive, no blanket Disallow
2. **XML sitemap** — exists, has `<lastmod>`, submitted in robots.txt
3. **Canonical tag** — self-referencing, present, matches URL
4. **HTTPS** — full site HTTPS, no mixed content
5. **Mobile viewport** — `<meta name="viewport">` present
6. **Status code** — 200 (not 4xx/5xx)
7. **No redirect chains** — single-hop or none
8. **No noindex on key pages** — check meta robots and X-Robots-Tag
9. **Clean URL structure** — no excessive parameters, readable paths
10. **HTTP/2 or HTTP/3** — check server header

#### Content Quality (7 checks, 20% weight)
11. **Title tag** — present, 50-60 chars, keyword front-loaded
12. **Meta description** — present, 120-160 chars, includes CTA
13. **H1 tag** — exactly one, contains primary keyword
14. **Heading hierarchy** — H2>H3>H4, no skipped levels
15. **Content length** — minimum 300 words body text
16. **Unique content** — not thin, not duplicate
17. **Freshness indicators** — dates visible, lastmod in sitemap recent

#### On-Page SEO (5 checks, 15% weight)
18. **Internal links** — at least 5, descriptive anchor text
19. **External links** — to authoritative sources where relevant
20. **Open Graph tags** — title, description, image, url present
21. **Twitter Card tags** — card, title, description present
22. **Hreflang** — if multi-language, properly implemented

#### Schema / Structured Data (5 checks, 15% weight)
23. **JSON-LD present** — at least one block
24. **Valid schema type** — Organization, WebSite, Article, Product, FAQPage as appropriate
25. **Required properties** — all mandatory fields for the type are filled
26. **No errors** — validate against Google Rich Results Test rules
27. **Breadcrumbs** — BreadcrumbList schema if applicable

#### Performance (5 checks, 10% weight)
28. **Page size** — HTML under 100KB, total under 3MB
29. **Script count** — reasonable number, no render-blocking
30. **Preconnect/preload hints** — resource hints for critical origins
31. **Image dimensions** — width/height attributes on all images (CLS prevention)
32. **Font loading** — font-display: swap or optional

#### Image Optimization (5 checks, 10% weight)
33. **Alt text coverage** — all images have descriptive alt
34. **Image format** — WebP/AVIF preferred, no oversized images
35. **Lazy loading** — below-fold images use loading="lazy"
36. **File sizes** — no images over 200KB
37. **Responsive images** — srcset or picture element for key images

#### AI Search Readiness (GEO) (5 bonus checks, 5% weight)
38. **llms.txt** — present at /llms.txt
39. **AI crawler access** — GPTBot, ClaudeBot, PerplexityBot allowed in robots.txt
40. **Structured data quality** — enough for AI citation extraction
41. **Snippet-ready answers** — H2 sections start with direct 40-60 word answers
42. **Entity clarity** — clear entity signals (Organization schema, about page, brand mentions)

### Phase 3: Score

Calculate the SEO Health Score:

```
Score = (Technical × 0.25) + (Content × 0.20) + (OnPage × 0.15) + 
        (Schema × 0.15) + (Performance × 0.10) + (Images × 0.10) + 
        (GEO × 0.05)

Each category scored 0-100 based on pass/warn/fail ratio, then weighted.
```

Score interpretation:
- **90-100** — Excellent, minor optimizations only
- **70-89** — Good, specific improvements identified
- **50-69** — Needs work, several high-priority issues
- **30-49** — Poor, significant technical or content problems
- **0-29** — Critical, major blocking issues

### Phase 4: Report

Use this exact report structure:

```markdown
# SEO Audit Report: [URL]
**Date:** [today]
**Score:** [XX/100] — [rating]

## Executive Summary
[2-3 sentence overview: what's working, what's broken, biggest opportunity]

## Score Breakdown

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Technical SEO | XX/100 | 25% | XX |
| Content Quality | XX/100 | 20% | XX |
| On-Page SEO | XX/100 | 15% | XX |
| Schema/Structured Data | XX/100 | 15% | XX |
| Performance | XX/100 | 10% | XX |
| AI Search Readiness | XX/100 | 5% | XX |
| **TOTAL** | | | **XX/100** |

## Findings

### P0 — Critical (must fix now)
[Issue/Impact/Evidence/Fix format for each]

### P1 — High Priority (fix this week)
[Issue/Impact/Evidence/Fix format for each]

### P2 — Medium Priority (fix this month)
[Issue/Impact/Evidence/Fix format for each]

### P3 — Low Priority (nice to have)
[Issue/Impact/Evidence/Fix format for each]

## What's Working
[Top 5 things the site does well]

## AI Search Readiness
[GEO-specific assessment: llms.txt, AI crawler access, citation potential]

## Quick Wins (top 5 fixes by impact/effort ratio)
[Ranked list with estimated impact]
```

Each finding must follow this format:
```
Issue:    <what is wrong, one line>
Impact:   High | Medium | Low
Evidence: <the live read — what was observed>
Fix:      <specific, actionable recommendation>
Priority: P0-P3
```

### Phase 5: Save

Save the report to `seo-audit-[domain]-[date].md` in the workspace root.

---

## Edge Cases

- **If the URL returns 4xx/5xx:** Report it as P0, still check what you can (headers, 
  robots.txt), note the error prominently.
- **If the site is CSR-only (React SPA shell):** Flag as P0 — invisible to crawlers. 
  Note "No SSR content detected — all content depends on JavaScript execution."
- **If robots.txt blocks everything:** Report as P0, check what's accessible via headers.
- **If the site has multiple subdomains:** Focus on the given URL's domain only unless 
  told otherwise.
- **If no sitemap exists:** P1 finding, suggest creating one.
- **If no structured data:** P1 finding, recommend adding appropriate schema.
- **If no llms.txt:** P2 finding (emerging standard, not yet critical).

---

## Tools Available

| Tool | What to use it for |
|------|-------------------|
| `bash` + curl | Fetch page, headers, robots.txt, sitemap |
| `python3` | Parse HTML, extract meta, calculate scores |
| `webfetch` | Alternative fetch if curl fails |
| `websearch` | Research competitor SEO if needed |
| `parallel-browser-mcp` | Render page visually if needed (JS-heavy sites) |

The scripts in `scripts/` handle the automated fetching. You handle the analysis 
and reporting.
