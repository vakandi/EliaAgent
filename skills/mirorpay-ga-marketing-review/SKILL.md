---
name: your-saas-ga-marketing-review
description: >-
  Full marketing director review of your-saas's GA4 data — traffic sources,
  conversion funnel, user behavior, AB test variant performance, and revenue
  (plan pricing events). Uses gsc-mcp to pull all GA4 data + Vercel CLI to
  check rolling-release AB testing status. Saves a structured .md report with
  executive summary, findings, and action items.

  Trigger this skill whenever the user asks to:
  - "Review your-saas analytics" / "Check your-saas conversion data"
  - "How is your-saas converting?" / "Marketing review"
  - "Check GA4 for your-saas" / "See your-saas traffic and revenue"
  - "Analyze AB test variants" / "Check variant performance"
  - "Run a marketing audit" / "Conversion funnel review"
  - Any request combining "your-saas" + "analytics/revenue/conversion/traffic"
  - Even vague requests like "how are we doing with your-saas" or "give me the numbers"
  
  If the user asks about another project (your-brand, FlowCheckout, etc.) but
  the question is about marketing analytics, also trigger — the skill accepts
  an `account` param for multi-site support.

compatibility:
  - Requires `gsc-mcp` MCP server registered in mcp_servers.json
  - Requires Vercel CLI (`vercel`) in PATH
  - Requires your-saas-homepage Vercel project linked locally
---

# your-saas GA Marketing Review Skill

You are a **data-driven marketing director** reviewing your-saas's performance. Your job is to:
1. Pull all available GA4 data via the GSC MCP (`gsc-mcp`) server
2. Check Vercel AB testing status via the Vercel CLI
3. Synthesize everything into a structured report saved as a `.md` file
4. Surface actionable insights — not just data, but **what it means for the business**

## Data Sources

| Source | Tool | What it gives you |
|--------|------|-------------------|
| **GSC MCP** | `mcp-cli call gsc-mcp <tool> '{"account":"your-saas"}'` | All GA4 data: traffic, users, conversions, revenue, variants |
| **Vercel CLI** | `vercel rr fetch` from the your-saas-homepage directory | Rolling release / AB testing configuration status |

**Key GA4 tools to call** (all via `gsc-mcp`, `account="your-saas"`):
- `ga4_traffic_sources` — Sessions by channel, source, medium (with engagement, conversions, revenue)
- `ga4_user_behavior` — Device, country, new vs returning breakdown
- `ga4_page_performance` — Per-page metrics (views, engagement, bounce, conversions, revenue)
- `ga4_conversion_funnel` — Event sequence counts (page_view → scroll → form_start → login → purchase)
- `ga4_realtime` — Active users right now (useful for pulse check)
- `ga4_organic_landing_pages` — Organic landing pages (can be sparse)
- `traffic_health_check` — Combined GSC impressions + GA4 sessions
- `page_analysis` — Cross-reference GSC ranking + GA4 engagement per page

**Optional depth tools** (call if report needs more insight):
- `quick_wins` — Pages needing title/meta/description improvements (NOTE: tool was renamed from `seo_quick_wins`)
- `seo_striking_distance` — Queries in positions 4-15 close to top 3
- `ai_visibility_audit` — Which AI crawlers can access the site (9 crawlers)
- `sitemap_audit` — Sitemap URLs vs indexed status
- `ga4_funnel` — Full funnel with custom steps (requires `steps` array)
- `ga4_event_breakdown` — Query event count broken down by dimension or event parameter. For `ab_test_variant`, pass `event_name="ab_variant_viewed"` with `dimension_name="customEvent:ab_test_variant"`. ✅ Registered since 2026-07-08 — use `dimension_name`, NOT `parameter_key`.
- `mcp-ga4-ultimate list_custom_dimensions` — List registered custom dimensions (use `account="mirrorpay"`).

### AB Test Variant Decoder

The `ab_variant_viewed` event fires **once per page load** with a **compound** `ab_test_variant` parameter containing ALL 5 section variants in one string: `hero_B|section2_pain|why_E|how_none|compare_none`

Format: `hero_{variant}|section2_{variant}|why_{variant}|how_{variant}|compare_{variant}`

| Section | Variant values | Default | Components map |
|---------|---------------|---------|---------------|
| `hero` | `A` `B` `C` `D` | `B` | A=HeroA (white, face), B=HeroB (127x Hormozi), C=HeroC (pain-first), D=HeroD (3 value cards) |
| `section2` | `trust` `killer` `value` `compare` `stats` `pain` | `pain` | trust=TrustStack, killer=SilentKiller, value=ValueStack, compare=OldWayNewWay, stats=StatsBar, pain=PainThreats |
| `why` | `A` `B` `C` `D` `E` | `E` | A=BentoGrid, B=IconGrid, C=Transformation, D=ReasonStack, E=TrustStack |
| `how` | `A` `B` `none` | `none` | A=3-step grid, B=Alternating timeline, none=hidden |
| `compare` | `original` `matrix` `workflow` `verdict` `none` | `none` | original=ComparisonGrid, matrix=DecisionMatrix, workflow=WorkflowGap, verdict=VerdictCards, none=hidden |

**Source:** `DevVariantSwitcher.tsx` (lines 30-34 type defs, lines 48-54 defaults, lines 147-183 labels)

**Events fired:**
- `ab_variant_viewed` — fires **once per page load** with ALL 5 section variants as a compound pipe-delimited string: `hero_B|section2_pain|why_E|how_none|compare_none`
- `ab_variant_selected` — fires only in dev mode when manually switching variants

**✅ `ab_test_variant` is now registered as a GA4 custom dimension** (as of 2026-07-08).
- Use `dimension_name="customEvent:ab_test_variant"` in `ga4_event_breakdown`
- Do NOT use `parameter_key` — it will fail with 400 error
- New events from registration date onward are directly tagged. Historical data before the fix used 5 events per page load with single-section values (e.g., `hero_B`). Both formats will appear in the dimension.

## Workflow

### Step 1: Check Vercel AB Testing Status

Run from the your-saas-homepage directory:
```bash
vercel rr fetch --cwd ~/Documents/your-saas/your-saas-homepage 2>&1
```

This tells you:
- Whether rolling releases are **enabled or disabled**
- Number of stages configured
- Advancement type (automatic vs manual-approval)
- Any currently active rolling release

**Why this matters:** If rolling releases are enabled, there's an active AB test splitting traffic between deployments. If disabled, check GA4 for any custom variant tracking (like the `ab_variant_viewed` event).

### Step 2: Pull GA4 Data

Call each of the following tools in parallel where possible. Use `account="your-saas"` for all calls (omit for default which is also your-saas).

```bash
# Core data (always pull these)
mcp-cli call gsc-mcp ga4_traffic_sources '{"site_url":"sc-domain:your-saas.com"}'
mcp-cli call gsc-mcp ga4_user_behavior '{"site_url":"sc-domain:your-saas.com"}'
mcp-cli call gsc-mcp ga4_page_performance '{"site_url":"sc-domain:your-saas.com"}'
mcp-cli call gsc-mcp ga4_conversion_funnel '{"site_url":"sc-domain:your-saas.com"}'

# Pulse check
mcp-cli call gsc-mcp ga4_realtime '{"site_url":"sc-domain:your-saas.com"}'
```

**To get cleaner data (exclude the owner's Morocco testing traffic):**
```bash
# Filter to US-only traffic for cleaner user behavior signal
mcp-cli call gsc-mcp ga4_traffic_sources '{"site_url":"sc-domain:your-saas.com","account":"your-saas","country":"United States"}'
mcp-cli call gsc-mcp ga4_user_behavior '{"site_url":"sc-domain:your-saas.com","account":"your-saas","country":"United States"}'
mcp-cli call gsc-mcp ga4_page_performance '{"site_url":"sc-domain:your-saas.com","account":"your-saas","country":"United States"}'
```

**If you need historical depth (weekly/bi-weekly reviews):**
```bash
mcp-cli call gsc-mcp ga4_page_performance '{"site_url":"sc-domain:your-saas.com","account":"your-saas","start_date":"90daysAgo"}'
mcp-cli call gsc-mcp traffic_health_check '{"site_url":"sc-domain:your-saas.com","account":"your-saas"}'
mcp-cli call gsc-mcp page_analysis '{"site_url":"sc-domain:your-saas.com","account":"your-saas","page":"/pricing"}'
```

#### Quick AB Test Data Pull (run this in parallel with core data):
```bash
# 1. Raw variant configs (all time) — compound strings like hero_B|section2_pain|why_E|...
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"ab_variant_viewed","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# 2. Variant configs LAST 28 DAYS (for current report)
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"ab_variant_viewed","dimension_name":"customEvent:ab_test_variant","start_date":"28daysAgo"}'

# 3. Cross-event: which configs led to pricing views?
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"view_pricing","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# 4. Cross-event: which configs led to form_start?
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"form_start","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# 5. Cross-event: which configs led to login?
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"login","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# 6. Cross-event: which configs led to billing click?
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"billing_upgrade_clicked","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# 7. Check registered custom dimensions (confirm dimension exists)
mcp-cli call mcp-ga4-ultimate list_custom_dimensions '{"property_id":"538362794","account":"mirrorpay"}'
```

### AB Test Extraction Protocol — 5-Step Analysis

**⚠️ ALWAYS run this.** Even with low traffic. The data accumulates over time and every report builds the history.

**Step 1: Pull raw variant distribution**
```bash
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"ab_variant_viewed","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'
```
This returns all unique `ab_test_variant` values with their event counts. Values look like:
- `hero_B|section2_pain|why_E|how_none|compare_none` (new format — full config, 1 event per page load)
- `hero_B` (old format — single section, from 5-events-per-page-load era, will disappear once old data rolls off)

**Step 2: Parse compound strings by section**
Each compound string is pipe-delimited: `hero_{V}|section2_{V}|why_{V}|how_{V}|compare_{V}`. Split on `|` to extract per-section variant. Then calculate per-section distribution:

```
Example compound: "hero_B|section2_pain|why_E|how_none|compare_none"
Parsed:            hero=B, section2=pain, why=E, how=none, compare=none
```

Group ALL compound values by each section to get per-section share:

```
hero:       B=40%  A=30%  C=20%  D=10%   → winner: hero_B
section2:   pain=60%  killer=20%  trust=20%  → winner: section2_pain
why:        E=100%   → only variant shown
how:        none=100% → section hidden for everyone
compare:    none=100% → section hidden for everyone
```

**Step 3: Cross-reference variant configs with key conversion events**
Since ONE compound event = ONE page load with the EXACT config, the correlation is now direct. Use `ga4_event_breakdown` with conversion event names to see which configs drove action:

```
# See which variant configs ended up viewing pricing
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"view_pricing","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# See which variant configs led to form start
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"form_start","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'

# See which variant configs led to login
mcp-cli call gsc-mcp ga4_event_breakdown '{"event_name":"login","dimension_name":"customEvent:ab_test_variant","start_date":"90daysAgo"}'
```

Parse each compound string to identify the winning config per conversion stage:

```
view_pricing breakdown:
  "hero_B|section2_pain|why_E|..." → 8 events
  "hero_A|section2_killer|why_E|..." → 4 events
```
Then manually compare:
- Which configs reach pricing vs just bounce
- Which configs convert to form_start → login → billing_click

If a variant config has high page views but low downstream conversion, that variant is underperforming.

**Step 4: Identify dominant full configurations**
Since 1 event = 1 exact config, the most common compound string IS the dominant experience. To find it:
1. Sort all compound values by event count descending
2. The top result is the most common full config shown to users
3. Compare with `hero_B|section2_pain|why_E|how_none|compare_none` (default)
4. If non-default configs have significant traffic, those are the active experiments
5. If only 1-2 compounds appear, most users see the same default experience

**Step 5: Track variant configs over time**
Keep a running log in the report:
```
Variant History:
- 2026-07-01: hero_B 100%, section2_pain 100%, why_E 100%  (all defaults)
- 2026-07-08: hero_A 30%, hero_B 40%, hero_C 20%, hero_D 10%  (testing began)
- 2026-07-15: ...
```

This tells you:
- When experiments started/stopped
- Which variants are being tested vs control
- Whether traffic allocation changed (e.g., from 50/50 to 90/10 = winner declared)

### Step 3: Synthesize the Report

Write the report to: `your-saas-marketing-review/YYYY-MM-DD-your-saas-marketing-review.md`

Create the directory if it doesn't exist:
```bash
mkdir -p ~/Documents/your-saas/your-saas-marketing-review
```

## Report Template

```markdown
# your-saas Marketing Review — YYYY-MM-DD

## Executive Summary
_Brief (~3 sentences): Overall traffic trend, conversion health, revenue status,
and 1-2 key findings that need attention right now._

## 1. Traffic Overview
| Metric | Value | vs Previous |
|--------|-------|------------|
| Total Sessions | X | ±X% |
| Active Users (last 28d) | X | — |
| Top Channel | X (X%) | — |
| Top Source | X (X sessions) | — |
| Top Country | X (X%) | — |

**Devices:** Desktop X% / Mobile X% / Tablet X%

**New vs Returning:** X% new / X% returning

**Key insight:** _What does this traffic composition tell us? Is the audience
quality improving? Are we reaching the right markets?_

## 2. Conversion Funnel
_Numbers from ga4_conversion_funnel + ga4_page_performance_

| Step | Event Count | Drop-off | Rate |
|------|------------|----------|------|
| Page View | X | — | 100% |
| Scroll | X | X (X%) | X% |
| User Engagement | X | X (X%) | X% |
| Form Start | X | X (X%) | X% |
| Login / Sign Up | X | X (X%) | X% |
| Pricing View | X | X (X%) | X% |
| Purchase / Payment | X | X (X%) | X% |

**Conversion Rate (overall):** X%
**Biggest drop-off point:** _Which step loses the most users? Why?_

## 3. AB Test / Variant Analysis
_From Vercel rolling-release status + GA4 ab_variant_viewed events (dimension: `customEvent:ab_test_variant`)_

**Vercel Rolling Release Status:** Enabled / Disabled
**Stages configured:** X stages (advancement: automatic/manual)

**ab_variant_viewed events (last 28d):** X events (= X unique page loads with variant config) ✅ 1 event = 1 full config
**ab_test_variant dimension:** ✅ Registered since 2026-07-08

### Raw Variant Configs
_From `ga4_event_breakdown` with `dimension_name="customEvent:ab_test_variant"`. Compound format: `hero_V|section2_V|why_V|how_V|compare_V`_

| Full Config (compound) | hero | section2 | why | how | compare | Event Count | Share |
|---|---|---|---|---|---|---|---|
| hero_B\|section2_pain\|why_E\|how_none\|compare_none | hero_B | section2_pain | why_E | none | none | X | X% |
| hero_A\|section2_killer\|why_D\|how_none\|compare_none | hero_A | section2_killer | why_D | none | none | X | X% |
| ... | ... | ... | ... | ... | ... | ... | ... |

### Per-Section Winner Analysis
_Parsed from compound strings — each section's variant share across all configs_

| Section | Variants Active | Winner | Confidence | Notes |
|---------|----------------|--------|------------|-------|
| hero | A/B/C/D | hero_B (X%) | Low/Med/High | Default is hero_B |
| section2 | trust/killer/value/compare/stats/pain | section2_pain (X%) | Low/Med/High | Default is pain |
| why | A/B/C/D/E | why_E (X%) | Low/Med/High | Default is E |
| how | A/B/none | none (X%) | Low/Med/High | Default is none (hidden) |
| compare | original/matrix/workflow/verdict/none | none (X%) | Low/Med/High | Default is none (hidden) |

### Variant Config → Conversion Correlation
_Cross-eventing: which configs appear in `view_pricing`, `form_start`, `login`, `billing_upgrade_clicked` events_

| Config | ab_variant_viewed | view_pricing | form_start | login | billing_click | Conversion Rate |
|--------|------------------|-------------|-----------|-------|--------------|----------------|
| hero_B\|s2_pain\|why_E\|none\|none | X | X | X | X | X | X% |
| hero_A\|s2_killer\|why_D\|none\|none | X | X | X | X | X | X% |
| (other configs) | ... | ... | ... | ... | ... | ... |

**Conversion Rate = billing_click ÷ ab_variant_viewed** — higher = better variant for driving revenue.

**Analysis:**
- _Which config drives the highest conversion rate?_
- _Is the default config outperforming experiments?_
- _Should any low-performing variants be eliminated to focus traffic on winners?_
- _Are there configs with high view_pricing but zero billing_click? (bad sign)_

| Date | Experiment | Variants | Allocation | Verdict |
|------|-----------|----------|------------|---------|
| YYYY-MM-DD | hero | A: 50%, B: 50% | Even split | Collecting data |
| YYYY-MM-DD | section2 | pain: 50%, killer: 50% | Even split | Collecting data |
| ... | ... | ... | ... | ... |

**Analysis:**
- _Are there enough variant events to be statistically significant?_
- _Which sections are actively being tested vs showing default only?_
- _Is there a clear winner emerging? (compare variant share + downstream conversion)_
- _Should any low-performing variants be eliminated to focus traffic on winners?_

## 4. Revenue & Conversion Value
_From ga4_page_performance (total_revenue field) + conversion funnel purchase events_

| Metric | Value |
|--------|-------|
| Total Revenue (last 28d) | EUR X |
| Revenue-generating pages | X pages |
| Conversion events | X |

**Revenue by page:** _(list pages that generated revenue)_

**Note:** If total_revenue is 0 across all pages, it means either:
- The GA4 e-commerce/purchase event isn't firing correctly
- No purchase events occurred in the period
- The GA4 property has the wrong view/filter

## 5. Top Pages Analysis
_From ga4_page_performance — top 10 pages by views or revenue_

| Page | Views | Avg Session | Engagement Rate | Bounce Rate | Revenue |
|------|-------|------------|----------------|-------------|---------|
| / | X | Xs | X% | X% | EUR X |
| /pricing | X | Xs | X% | X% | EUR X |
| ... | ... | ... | ... | ... | ... |

**Pages with issues:** _(high bounce, low engagement, 0 views but tracked users)_

## 6. SEO & Technical Health (Optional)
_If quick_wins, striking_distance, or ai_visibility_audit were called_

- **Quick SEO wins:** X pages need meta improvements
- **Striking distance queries:** X queries close to top 3
- **AI crawler visibility:** X of 9 crawlers can access
- **GSC indexed URLs:** X of X sitemap URLs indexed

## 7. Recommendations

_Based on ALL the data above, provide 3-5 concrete action items:_

1. **[Priority: High/Med/Low]** — Specific recommendation with data evidence
2. **[Priority: High/Med/Low]** — Specific recommendation with data evidence
3. ...

## Data Snapshot
_GA4 period: 28daysAgo → today (unless otherwise noted)_
_Crawled: YYYY-MM-DD HH:MM_
```

## Report Location

Save all reports to:
```
~/Documents/your-saas/your-saas-marketing-review/
```

Filename format: `YYYY-MM-DD-your-saas-marketing-review.md`

The `your-saas-marketing-review/` directory is organized as a running log. Each
report is a standalone snapshot. The most recent report can be referenced as
"the current marketing review."

## Data Quality — Pre-July 10 Contamination

**⚠️ CRITICAL CONTEXT:** All traffic before **July 10, 2026** is heavily contaminated by the owner's own development/testing traffic from Morocco (Casablanca). This manifests as:
- ~57% of sessions from Morocco (50 of 88)
- ~70% Direct channel traffic (62 of 88)
- Inflated `/auth/login`, `/dashboard/*`, `/dashboard/setup` page views
- Auth/dashboard engagement rates skewed (the owner spending hours testing)

**In every report, you MUST:**
1. Flag the Morocco/Direct traffic contamination in the Executive Summary
2. Note that metrics before July 10 reflect founder testing, not real user behavior
3. When possible, include a "US Only" view using the `country: "United States"` parameter on MCP tools to show cleaner data
4. Do NOT dismiss all data — returning visitor rate (34%), blog engagement (100%), and social referral traffic (12 sessions from FB/IG) are genuine signals even if absolute numbers are small

**After July 10, 2026:** Assume progressively cleaner data as the owner will implement filtering (browser extension or GA4 Internal Traffic Data Filter). Continue flagging any unusual Morocco/Direct dominance.

## Fallback Behavior

**If Vercel rolling-release check fails** (project not linked, auth expired):
- Skip Vercel check and note it in the report
- Still pull all GA4 data
- Recommend running `vercel link` to re-establish the connection

**If GA4 data returns empty or zeroes:**
- Note whether the period makes sense (new site, recent launch, etc.)
- Check if the GA4 property ID is correct (your-saas = 538362794)
- Recommend verifying gtag (`G-HXY60VCEV0`) is firing on the site

**If any GSC MCP tool errors:**
- Log the error in the report's "Data Quality" section
- Continue with remaining tools
- The report should still be useful with partial data

## Writing Style

Write like a **marketing director reporting to a founder**:
- **Direct and honest** — if conversion is bad, say it. If it's good, say it.
- **Data-backed** — every claim must reference the specific tool/data point
- **Action-oriented** — end with recommendations, not just observations
- **Business context** — explain WHY a metric matters, not just what it is
  (e.g., "Bounce rate on /pricing is 50% — this is expected for a pricing page
  where users compare plans, but 50% means half leave without starting a form")

Don't pad the report with fluff. Every section should justify its existence with
useful signal. If a section has no useful data (e.g., 0 conversions), say so
briefly and move on — don't write paragraphs about nothing.
