---
title: Wiki Schema
description: Rules and conventions for the LLM Wiki second brain
---

# LLM Wiki Schema - Wael's Second Brain

## Overview

This is a **persistent, compounding knowledge base** maintained by the LLM. Unlike RAG systems that re-derive knowledge on every query, this wiki accumulates insights over time with cross-references already built.

**Three Layers:**
1. **Raw Sources** → Immutable source documents (never modified)
2. **Wiki Pages** → LLM-generated, interlinked markdown files  
3. **Schema (this file)** → Conventions and workflows

---

## Directory Structure

```
wiki/
├── AGENTS.md           ← This schema (source of truth)
├── index.md           ← Content catalog (updated every ingest)
├── log.md             ← Chronological append-only log
├── raw/               ← Immutable source documents
│   ├── articles/      ← Web-clipped articles
│   ├── documents/     ← PDFs, papers
│   ├── conversations/ ← Chat exports
│   └── notes/         ← Voice memos, handwritten scans
└── pages/             ← LLM-generated wiki pages
    ├── entities/       ← People, companies, products
    ├── concepts/       ← Theories, frameworks, methods
    ├── summaries/      ← Source summaries
    └── sources/        ← Full source documentation
```

---

## File Naming Conventions

- **Entities**: `entity-[name-lowercase].md` (e.g., `entity-elia.md`)
- **Concepts**: `concept-[name-lowercase].md` (e.g., `concept-llm-wiki.md`)
- **Summaries**: `summary-[source-slug].md` (e.g., `summary-llm-wiki-pattern.md`)
- **Sources**: `source-[source-slug].md` (e.g., `source-llm-wiki-pattern.md`)

---

## Page Format

Every wiki page MUST have this frontmatter:

```yaml
---
title: Page Title
type: entity|concept|summary|source
tags: [tag1, tag2]
sources: [count]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Entity Pages
```markdown
# [Entity Name]

## Definition
Brief description.

## Key Attributes
- **Type**: ...
- **Origin**: ...
- **Status**: ...

## Connections
- Related to [[concept-X]]
- Part of [[entity-Y]]

## Notes
Free-form insights.
```

### Concept Pages
```markdown
# [Concept Name]

## Definition
Clear, concise definition.

## Core Principles
1. ...
2. ...

## Related Entities
- [[entity-X]]

## Related Concepts
- [[concept-Y]]

## Practical Applications
How to apply this.
```

---

## Operations

### Ingest Workflow

1. **Receive**: New source dropped in `raw/` directory
2. **Read**: LLM reads and analyzes source
3. **Summarize**: Create `pages/summaries/summary-[slug].md`
4. **Extract Entities**: Update `pages/entities/` pages
5. **Extract Concepts**: Update `pages/concepts/` pages
6. **Update Index**: Add entry to `index.md`
7. **Log**: Append entry to `log.md`
8. **Cross-Reference**: Check for contradictions, update related pages

### Query Workflow

1. **Check Index**: Read `index.md` to find relevant pages
2. **Drill Down**: Read specific pages
3. **Synthesize**: Generate answer with citations
4. **File Back**: If answer is valuable, create new wiki page

### Lint Workflow

Run periodically to health-check wiki:
- [ ] Find contradictions between pages
- [ ] Find stale claims superseded by newer sources
- [ ] Find orphan pages with no inbound links
- [ ] Find concepts mentioned but lacking pages
- [ ] Find missing cross-references
- [ ] Identify data gaps for web search

---

## Index Format

```markdown
# Wiki Index

**Last Updated**: YYYY-MM-DD  
**Total Pages**: N  
**Total Sources**: N

## Pages

### Entities (N)
| Page | Summary | Tags | Updated |
|------|---------|------|---------|

### Concepts (N)
| Page | Summary | Tags | Updated |
|------|---------|------|---------|

### Summaries (N)
| Page | Source | Key Insight | Date |
|------|--------|-------------|------|

### Sources (N)
| Page | Type | Topics | Added |
|------|------|--------|-------|
```

---

## Log Format

```markdown
# Wiki Log

Append-only chronological record.

## Entry Template
## [YYYY-MM-DD] action | Title

**Action**: ingest | query | lint | update | create
**Title**: Brief title of the operation
**Pages touched**: List of modified pages

### Details
What happened.
```

Example entry:
```markdown
## [2026-04-09] ingest | LLM Wiki Pattern

**Action**: ingest  
**Pages touched**: summary-llm-wiki-pattern, concept-second-brain, index, log

### Details
Ingested the LLM Wiki idea file. Created core schema and directory structure.
Key insight: LLMs can handle the "bookkeeping" that makes wikis useful.
```

---

## Citation Format

Always cite sources using this format:
> [[source-slug]] - "[Quote or reference]" (p. N)

Example:
> The wiki is a persistent, compounding artifact. [[llm-wiki-pattern]] - "The cross-references are already there" 

---

## Cross-Reference Rules

1. **Always link** to related entities and concepts
2. **Flag contradictions** with `⚠️ CONTRADICTION:` header
3. **Mark stale** claims with `📅 Deprecated:` and date
4. **Track evolution** of ideas across sources

---

## Workflow Commands

| Command | Action |
|---------|--------|
| `ingest [file]` | Process new source |
| `query [question]` | Ask wiki a question |
| `lint` | Health-check wiki |
| `index` | Update content catalog |
| `log [entry]` | Add log entry |

---

## Success Criteria

- [ ] Every source has a summary page
- [ ] Every entity has inbound links
- [ ] Every concept has at least one source
- [ ] No orphan pages (verified by lint)
- [ ] Index is current after every ingest
- [ ] Log captures all operations

---

*Last Updated: 2026-04-09*
*Version: 1.0*
