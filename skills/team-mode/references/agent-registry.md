# Agent Registry — Team Mode Eligibility

## Eligible Agents (can be team members)

### Custom Agents (from opencode.json)

| Agent | Role | Personality File | Best For |
|-------|------|-----------------|----------|
| **gilfoyle** | Backend & Full-Stack Engineer | `agents/gilfoyle.md` | FastAPI, Python, React, debugging, deployment, shell scripts, API work |
| **picasso** | Elite Frontend Specialist | `agents/picasso.md` | React, TypeScript, Tailwind, Framer Motion, UI/UX design, visual QA |
| **setbon** | Marketing & Conversion Expert | `agents/setbon.md` | Alex Hormozi system, conversion optimization, pricing, offers, funnels |
| **googlebot** | SEO & Web Crawling Specialist | `agents/googlebot.md` | SEO audits, web crawling, sitemap analysis, structured data, Core Web Vitals |
| **your-saas-seo** | your-saas SEO Strategist | `agents/your-saas-seo.md` | Autonomous 90-day SEO plan, competitive intelligence, pillar pages |
| **your-saas-community-organic** | Multi-Platform Content Creator | `agents/your-saas-community-organic.md` | Instagram, Pinterest, Reddit, YouTube, Facebook, LinkedIn, X content + Zernio scheduling |
| **mirrorpay-telegram** | Telegram Lead Gen | `agents/mirrorpay-telegram.md` | Telegram group scanning, prospect invitation, MirrorPay channel conversion |
| **markov** | Trading Orchestrator | `agents/markov.md` | Coordinates technical + fundamental analysts, market analysis |
| **markov-technical-analyst** | Chart Analysis | `agents/markov-technical-analyst.md` | TradingView MCP, technical indicators, chart patterns |
| **markov-fundamental-analyst** | Geopolitics & Sentiment | `agents/markov-fundamental-analyst.md` | WorldMonitor, news analysis, fundamental data, sentiment |
| **your-brand** | Luxury Fashion Resale | `agents/your-brand.md` | France/Switzerland luxury fashion, product listings, marketplace |
| **your-agency-agency** | B2B Digital Solutions | `agents/your-agency-agency.md` | B2B services, client management, agency operations |
| **zovaboost** | SMMPanel Services | `agents/zovaboost.md` | Social media marketing panel, service delivery |
| **tiktok-youtube-auto** | Content Automation | `agents/tiktok-youtube-auto.md` | TikTok/YouTube automation, Python/FastAPI content pipelines |
| **reddit-saas-scraper** | Reddit Problem Hunter | `agents/reddit-saas-scraper.md` | Reddit scanning for SaaS opportunities (read-only — use with caution in teams) |
| **netfluxe** | IPTV + USB Content | `agents/netfluxe.md` | IPTV services, USB content distribution |
| **account-verification** | Verified Accounts | `agents/account-verification.md` | Social media account verification |
| **your-saas-assistant** | Directus AI Expert | `agents/your-saas-assistant.md` | Directus CMS, your-saas/FlowCheckout plugin development |

### Built-In OMO Agents

| Agent | Role | Notes |
|-------|------|-------|
| **sisyphus** | Default orchestrator | Full tool access, can be team lead |
| **atlas** | General-purpose worker | Full tool access |
| **sisyphus-junior** | Category-routed worker | Routes through category model selection |

## Ineligible Agents (cannot be team members)

| Agent | Reason | Alternative |
|-------|--------|-------------|
| **oracle** | Read-only — cannot write to mailbox files | Use `delegate-task` with `subagent_type: "oracle"` for read-only analysis |
| **librarian** | Read-only — cannot write to mailbox | Use `delegate-task` for research tasks |
| **explore** | Read-only — cannot write to mailbox | Use `delegate-task` for code exploration |
| **multimodal-looker** | Read-only tool access | Use `delegate-task` for media analysis |
| **metis** | Pre-planning consultant, restricted tools | Use in plan mode, not team mode |
| **momus** | Plan reviewer, restricted tools | Use for post-implementation review via delegate-task |
| **prometheus** | Plan-mode-only, restricted to `.omo/*.md` writes | Use `/shared/ulw-plan` for planning |

## Choosing Agents for a Task

### By Domain

| Task Type | Primary Agent(s) | Support Agent(s) |
|-----------|------------------|-------------------|
| Backend API work | gilfoyle | — |
| Frontend/UI work | picasso | — |
| Full-stack feature | gilfoyle + picasso | setbon (if user-facing) |
| Marketing campaign | setbon | your-saas-community-organic, googlebot |
| SEO optimization | googlebot | your-saas-seo |
| Content creation | your-saas-community-organic | setbon (strategy) |
| Trading analysis | markov | markov-technical-analyst, markov-fundamental-analyst |
| Debugging | gilfoyle | picasso (if frontend) |
| E-commerce | your-brand | picasso (UI), setbon (marketing) |
| B2B services | your-agency-agency | setbon (sales) |

### By Complexity

| Complexity | Recommended Approach |
|------------|---------------------|
| Simple (2 agents) | Direct team_create with inline spec |
| Medium (3-4 agents) | Team + shared task list with dependencies |
| Complex (5+ agents) | Team + pre-declared spec file + category-routed members for research |

## Adding New Agents

When creating a new agent via the `elia-subworker-creator` skill, it automatically becomes eligible for team mode if:
1. It's registered in `opencode.json` with `mode: "subagent"`
2. It has a personality file in `~/.config/opencode/agents/`
3. It has write access (not read-only restricted)

The agent doesn't need to be explicitly added to any team eligibility list — the team system checks opencode.json registration at runtime.
