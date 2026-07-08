---
title: LLM Wiki Pattern
type: source
tags: [llm-wiki, second-brain, knowledge-management, memex]
sources: 1
created: 2026-04-09
updated: 2026-04-09
---

# Source: LLM Wiki Pattern

**Type**: Article / Idea File  
**Origin**: Custom concept based on Vannevar Bush's Memex  
**Added**: 2026-04-09

## Overview

A pattern for building personal knowledge bases using LLMs. Instead of RAG-style retrieval, the LLM incrementally builds and maintains a persistent wiki.

## Core Thesis

> "Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question."

The LLM Wiki pattern solves this by maintaining a persistent, compounding artifact where:
- Cross-references are already built
- Contradictions are flagged
- Synthesis reflects everything read

## Three Layers

1. **Raw Sources**: Immutable documents (source of truth)
2. **Wiki Pages**: LLM-generated, interlinked markdown
3. **Schema**: Conventions and workflows (AGENTS.md)

## Key Insights

### 1. Accumulation > Retrieval
Knowledge compiled once, kept current—not re-derived on every query.

### 2. LLMs Do the Maintenance
> "LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass."

### 3. Three Operations
- **Ingest**: Read source → Create/update pages → Update index → Log
- **Query**: Check index → Read pages → Synthesize → File back
- **Lint**: Health-check for contradictions, orphans, gaps

## Architecture Details

### Index Format
Content-oriented catalog. Updated on every ingest. Organized by category.

### Log Format
Chronological, append-only. Entries start with `## [YYYY-MM-DD] action | Title`

### Optional Tools
- **Obsidian**: IDE for browsing wiki
- **qmd**: Local search engine for markdown
- **Obsidian Web Clipper**: Browser extension to clip articles
- **Marp**: Slide deck generation
- **Dataview**: Query over frontmatter

## Why This Works

The tedious part of maintaining a knowledge base is bookkeeping. Humans abandon wikis because maintenance burden grows faster than value. LLMs don't have this problem.

## Connection to Memex

Vannevar Bush's Memex (1945) envisioned a personal, curated knowledge store with associative trails. The LLM solves the maintenance problem Bush couldn't.

## Related Concepts
- [[concept-llm-wiki]] - The LLM Wiki approach
- [[concept-memex]] - Vannevar Bush's original vision

---

*Citation: LLM Wiki idea file, 2026-04-09*
