# 42-Check SEO Scorecard

Detailed scoring rubric for the SEO audit skill.

## Technical SEO (10 checks → 25% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 1 | robots.txt | Exists, allows CSS/JS, has Sitemap directive | Exists but missing Sitemap directive | 404 or blocks everything |
| 2 | XML sitemap | Found via robots.txt or /sitemap.xml, has URLs | Exists but no `<lastmod>` | Not found |
| 3 | Canonical tag | Self-referencing, matches URL | Present but points elsewhere | Missing |
| 4 | HTTPS | Full site HTTPS, no mixed content | Some mixed content warnings | HTTP only |
| 5 | Mobile viewport | `<meta name="viewport">` present with width=device-width | Present but misconfigured | Missing |
| 6 | Status code | 200 OK | 3xx redirect (expected) | 4xx or 5xx |
| 7 | Redirect chains | No chains (single-hop or none) | 2-hop chain | 3+ hop chain |
| 8 | No noindex on key page | No noindex directive | — | noindex found |
| 9 | Clean URLs | Readable, short paths | Has some parameters | Heavy query strings |
| 10 | HTTP/2+ | Server responds with h2/h3 | HTTP/1.1 | Unknown |

## Content Quality (7 checks → 20% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 11 | Title tag | 50-60 chars, keyword front-loaded | Present but wrong length or no keyword | Missing |
| 12 | Meta description | 120-160 chars, includes CTA | Present but too short/long | Missing |
| 13 | H1 tag | Exactly one, contains primary keyword | Multiple H1s or no keyword | Missing entirely |
| 14 | Heading hierarchy | H2>H3>H4, no skipped levels | Minor skip (H2>H4) | Major gaps |
| 15 | Content length | 300+ words body text | 100-299 words (thin) | <100 words |
| 16 | Unique content | Substantive, original | Mostly original, some boilerplate | Duplicate/thin |
| 17 | Freshness | Dates visible, recent content | Dates present but old | No dates, stale |

## On-Page SEO (5 checks → 15% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 18 | Internal links | 5+ internal links, descriptive text | 1-4 internal links | Zero internal links |
| 19 | External links | Links to authoritative sources | Some external links | Zero external links |
| 20 | OG tags | title, description, image, url all present | Partial (2-3 present) | Missing or <2 |
| 21 | Twitter tags | card, title, description present | Partial | Missing |
| 22 | Hreflang | Proper implementation if multi-language | Present but errors | N/A or missing |

## Schema / Structured Data (5 checks → 15% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 23 | JSON-LD present | 1+ valid JSON-LD blocks | Present but malformed | None |
| 24 | Valid schema type | Correct type for page (Org, Article, Product, etc.) | Generic WebPage | None |
| 25 | Required properties | All mandatory fields filled | Some missing | Many missing |
| 26 | No errors | Passes Google Rich Results Test rules | Minor issues | Major errors |
| 27 | Breadcrumbs | BreadcrumbList schema present | Breadcrumbs visible but no schema | Neither |

## Performance (5 checks → 10% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 28 | Page size | HTML <100KB | 100-200KB | >200KB |
| 29 | Script count | <10 scripts | 10-20 scripts | >20 scripts |
| 30 | Resource hints | preconnect for critical origins | preload only | None |
| 31 | Image dimensions | width/height on all images | Some missing | Most missing |
| 32 | Font loading | font-display: swap/optional | font-display: auto | No font-display |

## Image Optimization (5 checks → 10% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 33 | Alt text coverage | All images have descriptive alt | 50-90% have alt | <50% or all missing |
| 34 | Image format | WebP/AVIF throughout | Mixed (some WebP, some JPEG/PNG) | All large JPEG/PNG |
| 35 | Lazy loading | Below-fold images use loading="lazy" | Some lazy loaded | No lazy loading |
| 36 | File sizes | No images >200KB | 1-2 oversized | Multiple >200KB |
| 37 | Responsive images | srcset or picture element for key images | Fixed sizes only | No responsive strategy |

## AI Search Readiness (5 bonus checks → 5% weight)

| # | Check | PASS | WARN | FAIL |
|---|-------|------|------|------|
| 38 | llms.txt | Present with useful content | Present but empty/minimal | Not found |
| 39 | AI crawlers allowed | GPTBot, ClaudeBot, PerplexityBot all allowed | Some blocked | All blocked |
| 40 | Schema quality | Rich, citable structured data | Basic schema | No schema |
| 41 | Snippet-ready answers | H2s start with direct 40-60 word answers | Some H2s have preamble | No direct answers |
| 42 | Entity clarity | Organization schema, about page, brand mentions | Partial entity signals | No entity signals |

## Scoring Formula

```
For each category:
  category_score = (pass_count × 100 + warn_count × 50) / total_checks_in_category

Final score:
  Score = Σ(category_score × category_weight)

Where weights:
  Technical:   0.25
  Content:     0.20
  OnPage:      0.15
  Schema:      0.15
  Performance: 0.10
  Images:      0.10
  GEO:         0.05
```

## Priority Assignment

| Score Range | Priority | Action |
|-------------|----------|--------|
| FAIL on Critical checks (1-6, 11-13, 23-24, 38) | P0 | Fix immediately |
| FAIL on any check | P1 | Fix this week |
| WARN on any check | P2 | Fix this month |
| Minor optimizations | P3 | Nice to have |
