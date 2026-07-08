---
title: LLM Wiki Pattern Source Document
type: raw-source
date: 2026-04-09
source: Original idea file
---

# LLM Wiki Pattern

A pattern for building personal knowledge bases using LLMs.

## The Core Idea

Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and the raw sources.

## Three Layers

1. **Raw sources** — your curated collection of source documents
2. **The wiki** — a directory of LLM-generated markdown files
3. **The schema** — a document that tells the LLM how the wiki is structured

## Operations

- **Ingest**: Drop a new source, LLM processes it
- **Query**: Ask questions against the wiki
- **Lint**: Health-check the wiki periodically

## Why This Works

LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass.

---

*This is the raw source document - never modified by LLM*

---

## Related Concepts

- [[concept-llm-wiki]] - The LLM Wiki pattern
- [[concept-memex]] - Bush's Memex vision
- [[concept-rag]] - Traditional RAG approach
- [[concept-hypertext]] - Digital linking

## Related Entities

- [[entity-vannevar-bush]] - Original visionary
- [[entity-ted-nelson]] - Hypertext pioneer
- [[entity-tim-berners-lee]] - Web inventor
- [[entity-openai]] - AI company enabling this

## Key Figure: Vannevar Bush

> "The part he couldn't solve was who does the maintenance. The LLM handles that."
