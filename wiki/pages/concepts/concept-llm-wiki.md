---
title: LLM Wiki Pattern
type: concept
tags: [knowledge-management, llm, wiki, second-brain]
sources: 1
created: 2026-04-09
updated: 2026-04-09
---

# Concept: LLM Wiki Pattern

## Definition

A knowledge management approach where an LLM incrementally builds and maintains a persistent wiki, as opposed to traditional RAG-style retrieval systems.

## Core Principles

1. **Persistent Compounding**
   - Knowledge is compiled once and kept current
   - Cross-references already exist when querying
   - No need to re-derive synthesis on every question

2. **LLM-Driven Maintenance**
   - The LLM handles all bookkeeping
   - Updates cross-references automatically
   - Flags contradictions between sources
   - Touches 10-15 files in one ingest operation

3. **Three-Layer Architecture**
   - Raw sources (immutable)
   - Wiki pages (LLM-generated)
   - Schema (conventions)

4. **Human in the Loop**
   - Human curates sources
   - Human directs analysis
   - Human asks questions
   - LLM does the grunt work

## Practical Applications

- Personal knowledge management
- Research accumulation
- Book companion wikis
- Team internal wikis
- Competitive analysis
- Due diligence

## Related Entities
- [[entity-vannevar-bush]] - Original Memex visionary

## Related Concepts
- [[concept-memex]] - Bush's 1945 vision
- [[concept-rag]] - Contrast with RAG retrieval

## Practical Notes

### Tools to Use
- **Obsidian**: Primary wiki browser
- **Obsidian Web Clipper**: For clipping articles
- **qmd**: Search engine when wiki grows

### Workflow
1. Drop source in `raw/`
2. Tell LLM to ingest
3. LLM creates summary, updates entities/concepts
4. LLM updates index and log
5. Query wiki for synthesized answers

## Status

✅ **Active** - Core system implemented 2026-04-09

---

*Source: [[source-llm-wiki-pattern]]*
