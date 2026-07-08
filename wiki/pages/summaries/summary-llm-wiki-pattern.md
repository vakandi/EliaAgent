---
title: "Summary: LLM Wiki Pattern"
type: summary
source: llm-wiki-pattern-source.md
created: 2026-04-09
updated: 2026-04-09
---

# Summary: LLM Wiki Pattern

**Source**: [[raw/articles/llm-wiki-pattern-source.md]]
**Date Ingested**: 2026-04-09

## Core Idea

The LLM Wiki pattern transforms how we use LLMs with documents. Instead of RAG-style retrieval where the LLM re-derives knowledge on every query, this approach builds a **persistent, compounding knowledge base**.

## Key Takeaways

1. **Accumulation > Retrieval** - Knowledge is compiled once and kept current
2. **LLMs Do Maintenance** - Cross-references, contradictions, updates handled automatically
3. **Three Layers** - [[raw/articles/llm-wiki-pattern-source.md]] → [[source-llm-wiki-pattern.md]] → [[concept-llm-wiki.md]]

## Architecture

```
Raw Sources (immutable)
    ↓
Wiki Pages (LLM-generated)
    ↓  
Schema (conventions)
```

## Key Quote

> "LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass."

## Related Pages

- [[concept-llm-wiki]] - Full concept definition
- [[concept-memex]] - Historical precursor
- [[concept-rag]] - Alternative approach
- [[entity-vannevar-bush]] - Visionary behind Memex

## Tags
#knowledge-management #llm #wiki #second-brain #memex

---

*This summary was generated during first ingest on 2026-04-09*
