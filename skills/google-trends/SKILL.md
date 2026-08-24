# Google Trends MCP Skill

Access real-time Google Trends data via the `google-trends` MCP server for SEO research, keyword analysis, content strategy, and trend monitoring.

**MCP name:** `google-trends`
**Location:** `~/mcps_server/GoogleTrendsMCP/`
**Rate limits:** Unofficial — max ~10-15 queries/session. Wait 60s on 429 errors. Batch with `full_keyword_research`.

---

## When to Use

- Keyword research before writing blog posts or SEO content
- Comparing search interest between competing terms
- Discovering rising/related queries for long-tail opportunities
- Checking trending searches by country for timely content
- Regional interest analysis for geo-targeted campaigns
- Content gap analysis (what people search vs what you cover)

---

## Tools (11 total — 9 API + 2 cache/rate-limit)

### `get_rate_limit_status` — RATE LIMIT CHECKER
**Check before every run.** Returns how many API calls have been made today, breakdown by tool, remaining budget. **Zero API requests** — reads local history only.

```
get_rate_limit_status()
```

### `get_cached_data` — CACHE READER
**Re-read data you already fetched.** Returns the most recent cached result for a given tool+keyword combo. **Zero API requests** — reads local history only. Use instead of re-querying when data is still fresh.

```
get_cached_data(tool_name="full_keyword_research", keyword="stripe france")
get_cached_data()  # all cached entries today
```

### `full_keyword_research` — THE POWER TOOL
**Use FIRST for any keyword research.** One call dumps everything: time series, related queries (top + rising), related topics, regional interest, and autocomplete suggestions. Batches 4-5 API calls into one to minimize rate limit hits.

```
full_keyword_research(keyword="payment gateway france", timeframe="today 12-m", geo="FR")
```

### `compare_keywords`
Compare up to 5 keywords head-to-head. Returns full weekly time series + summary stats (mean, max, trend direction).

```
compare_keywords(keywords=["stripe", "paypal", "mangopay"], geo="FR")
```

### `get_related_queries`
Top + rising related searches for a keyword. **#1 tool for long-tail discovery.** Rising queries = fast-growing content opportunities.

```
get_related_queries(keyword="payment processing", geo="US")
```

### `get_related_topics`
Thematic connections — what topics surround a keyword. Good for content cluster planning.

```
get_related_topics(keyword="e-commerce payments")
```

### `get_interest_by_region`
Geographic breakdown of search interest. Use COUNTRY, REGION, or CITY resolution.

```
get_interest_by_region(keyword="online payments", geo="FR", resolution="REGION")
```

### `get_trending_searches`
Today's trending searches by country. Good for newsjacking or timely content.

```
get_trending_searches(country="france")
```

### `get_realtime_trending`
Real-time trending with news articles and images. Faster than daily trends.

```
get_realtime_trending(country="FR", count=50)
```

### `get_trending_analysis`
Rising + declining queries AND topics over a period. One call, two datasets.

```
get_trending_analysis(timeframe="today 1-m", geo="US")
```

### `get_suggestions`
Google autocomplete suggestions for long-tail variations.

```
get_suggestions(keyword="best payment")
```

---

## Usage Pattern (Optimal)

### For a new blog post or content piece:
1. `full_keyword_research(keyword="your topic", geo="TARGET_COUNTRY")` — get everything in one shot
2. Pick top + rising related queries for subheadings
3. Check regional interest if geo-targeting
4. Use autocomplete suggestions for FAQ section

### For competitor analysis:
1. `compare_keywords(keywords=["your term", "competitor term"], geo="TARGET")` — head-to-head
2. `get_related_queries` on both — find gaps

### For trend monitoring:
1. `get_trending_analysis(timeframe="today 1-m")` — weekly pulse
2. `get_trending_searches` for daily spikes

---

## Rate Limit Strategy

| Action | API calls | Risk |
|---|---|---|
| `get_rate_limit_status` | 0 | None — local read only |
| `get_cached_data` | 0 | None — local read only |
| `full_keyword_research` | 4-5 batched | Low (1 session call) |
| `compare_keywords` | 1 | Low |
| `get_related_queries` | 1 | Low |
| Individual tool combos | 1 each | Medium — max 3-4 per request |

**Rule:** Prefer `full_keyword_research` over calling individual tools separately. If you need data on 3 keywords, call `full_keyword_research` 3 times with a 5s pause between, NOT `compare_keywords` + `get_related_queries` + `get_interest_by_region` (which is 7+ calls).

**Before every run:** Call `get_rate_limit_status()` first to see remaining budget.

**Already fetched?** Use `get_cached_data()` instead of burning another API call.

**Every API call is logged** to `history/YYYY-MM-DD.json` (tool name, params, timestamp, status). This gives a full audit trail without any external database.

**On 429 error:** Stop all Google Trends calls. Wait 60 seconds. Resume with `full_keyword_research` only. Check `get_rate_limit_status()` after waiting.

---

## Geo Codes (Common)

| Country | Code |
|---|---|
| Worldwide | `""` (empty) |
| United States | `US` |
| France | `FR` |
| Switzerland | `CH` |
| United Kingdom | `GB` |
| Germany | `DE` |
| Canada | `CA` |

---

## Timeframe Options

| Timeframe | Meaning |
|---|---|
| `today 12-m` | Past 12 months (default, best for SEO) |
| `today 3-m` | Past 3 months (recent trends) |
| `today 1-m` | Past 1 month (very recent) |
| `now 7-d` | Past 7 days (spike detection) |
| `now 1-d` | Past 24 hours (real-time) |
| `YYYY-MM-DD YYYY-MM-DD` | Custom date range |

---

## Output Format

All tools return JSON with:
- `"status": "ok"` or `"status": "error"`
- `"queried_at"` — ISO timestamp
- Tool-specific data (time series, regions, queries, etc.)

On error: check for `"429"` or `"Too Many"` in error message → wait 60s.

---

## Example Workflow: Blog Post Research

```
1. full_keyword_research(keyword="stripe alternative europe", timeframe="today 12-m", geo="FR")
   → Get: mean interest, top queries, rising queries, regional breakdown, suggestions

2. Take the 5 top related queries → use as H2/H3 subheadings
3. Take the 3 rising queries → create "People Also Ask" FAQ entries
4. Take autocomplete suggestions → long-tail variations for internal linking
5. Check regional interest → if France > Switzerland, prioritize French content
```

---

## Installation (Already Done)

Server is at `~/mcps_server/GoogleTrendsMCP/` with venv configured. Uses `pytrends-modern` (not archived `pytrends`).

To verify: `cd ~/mcps_server/GoogleTrendsMCP && venv/bin/python -c "from pytrends_modern import TrendReq; print('OK')"`
