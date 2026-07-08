---
title: Elia Brain - Self Analysis Schema
description: Rules for Elia's self-improvement wiki
---

# Elia Brain - Self Analysis Wiki

> [!links]+ Quick Access
> [[index|Index]] · [[log.md|Log]] · [[Welcome|Welcome]] · [[wiki/HOME|Wiki Hub]] · [[pages/issues/|Issues]] · [[pages/mistakes/|Mistakes]] · [[pages/bottlenecks/|Bottlenecks]]

**Purpose**: Let Elia (AI agent) analyze her own performance, track mistakes, identify bottlenecks, and compound improvements over time.

## The Core Idea

Instead of forgetting mistakes after each session, Elia compiles her learning into a persistent wiki. Every issue analyzed, every bottleneck identified, every improvement made - **compounds over time**.

> "Every conclusion goes back to the wiki" - Karpathy's LLM Wiki pattern adapted for agent self-improvement

## Architecture

```
brain/
├── AGENTS.md           ← This schema
├── index.md           ← Content catalog (all pages)
├── log.md             ← Chronological record of all analysis
├── raw/              ← Immutable session data, outputs, errors
└── pages/
    ├── issues/        ← Problems identified
    ├── mistakes/      ← Errors made
    ├── bottlenecks/   ← Performance bottlenecks
    ├── improvements/  ← Improvements made
    ├── analysis/      ← Session analyses
    └── patterns/      ← Recurring patterns discovered
```

## File Naming

- Issues: `issue-[YYYY-MM-DD]-[short-name].md`
- Mistakes: `mistake-[YYYY-MM-DD]-[short-name].md`
- Bottlenecks: `bottleneck-[name].md`
- Analysis: `analysis-[YYYY-MM-DD].md`

## Page Format

```yaml
---
title: Issue Title
type: issue|mistake|bottleneck|improvement|analysis
date: YYYY-MM-DD
severity: high|medium|low
status: open|in-progress|resolved
recurring: true|false
tags: [tag1, tag2]
---

# Title

## What Happened
Description of the issue.

## Root Cause
Why it happened.

## Impact
What was the effect?

## Resolution
How it was/will be fixed.

## Prevention
How to prevent recurrence.

## Related Pages
- [[related-page]]
```

## Operations

### 1. Ingest (After each session)
```bash
# Check for new raw session data
ls -lt brain/raw/YYYY-MM-DD/

# Review session output
cat docs/YYYY-MM-DD/run_*.md

# Identify:
# - New issues → Create in pages/issues/
# - New mistakes → Create in pages/mistakes/
# - Improvements made → Create in pages/improvements/
# - Log to log.md
```

### 2. Query (Before new session)
```
Before starting work, query the brain:
- Check open issues for relevant context
- Check patterns that apply to current task
- Review recent mistakes to avoid repeating
- Check bottleneck pages for known limitations
```

### 3. Lint (Weekly)
```bash
# Check for:
grep -r "\[\[\\.\\./" brain/pages/  # Broken links
grep -r "status: open" brain/pages/   # Stale issues
find brain/pages -name "*.md"          # Orphan pages

# Verify:
# - All links resolve
# - Open issues still relevant
# - Resolved items actually resolved
# - Patterns still recurring
```

### 4. Bottleneck Tracking
- Monitor for repeated slowdowns
- Create bottleneck pages
- Link to related issues
- Update status when resolved

### 5. Pattern Detection
- Find recurring themes across issues
- Create pattern pages in pages/patterns/
- Update prevention strategies
- Link related issues to pattern

## Index Format

```markdown
# Index

## Open Issues (N)
| Page | Severity | Date | Status |

## Recent Analysis (N)
| Date | Key Findings |

## Bottlenecks (N)
| Name | Severity | Related Issues |
```

## Log Format

```markdown
## [YYYY-MM-DD] type | Summary
- Pages touched: list
- Key finding: ...
```

## Elia Self-Analysis Rules

1. **Every session**: Review outputs, log significant events
2. **Every mistake**: Document immediately, update prevention
3. **Every week**: Run lint, update patterns
4. **Every month**: Review recurring issues, update schema if needed

## Workflow Integration

### When to Query the Brain
- **At session start**: Check [[index|index.md]] for open issues relevant to current task
- **When stuck**: Review [[pages/patterns/|patterns/]] for known bottlenecks
- **Before repeating work**: Check [[pages/mistakes/|mistakes/]] to avoid past errors
- **Critical blockers**: Check [[pages/issues/|issues/]] for open problems

### When to Update the Brain
- **After blocking issue**: Create issue page in [[pages/issues/|issues/]] with resolution plan
- **After making mistake**: Document in [[pages/mistakes/|mistakes/]] with prevention
- **After improvement**: Document in [[pages/improvements/|improvements/]]
- **When pattern emerges**: Create/update [[pages/patterns/|patterns/]] page
- **After session**: Log to [[log.md|log.md]]

### Quick Brain Commands
```bash
# Check for open issues
grep -l "status: open" brain/pages/issues/*.md

# Check for recurring patterns
grep -l "recurring: true" brain/pages/patterns/*.md

# Recent mistakes
ls -lt brain/pages/mistakes/ | head -5

# Open bottlenecks
grep -l "status: open" brain/pages/bottlenecks/*.md
```

## Key Metrics to Track

- Response time by task type
- Error frequency by category
- Task completion rate
- Improvement over time
- Pattern emergence

---

*Schema Version: 1.0*
*Created: 2026-04-09*
*Based on: Karpathy's LLM Wiki pattern*
