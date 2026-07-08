---
title: RAG (Retrieval-Augmented Generation)
type: concept
tags: [llm, retrieval, knowledge-management, ai]
sources: 1
created: 2026-04-09
updated: 2026-04-09
---

# Concept: RAG (Retrieval-Augmented Generation)

## Definition

Retrieval-Augmented Generation is a pattern where an LLM retrieves relevant document chunks at query time to generate answers. The LLM re-derives knowledge on every question.

## How RAG Works

1. Upload documents to a vector database
2. Embed documents into vectors
3. At query time, retrieve relevant chunks
4. LLM generates answer from retrieved chunks

## Problems with RAG

- **No accumulation**: Every query rediscovering knowledge
- **No cross-references**: Answers don't build on previous work
- **Context limits**: Can only use a few chunks per query
- **No synthesis**: Each answer is isolated

## LLM Wiki vs RAG

| Aspect | RAG | LLM Wiki |
|--------|-----|----------|
| Knowledge | Re-derived each query | Compiled once |
| Cross-refs | None | Built-in |
| Accumulation | No | Yes |
| Synthesis | Limited | Rich |

> "This works, but the LLM is rediscovering knowledge from scratch on every question." [[source-llm-wiki-pattern]]

## Related Concepts

- [[concept-llm-wiki]] - The solution to RAG's limitations
- [[concept-hypertext]] - Predecessor linking technology

## Related Entities

- [[entity-openai]] - Creator of GPT models (commonly used in RAG)

---

*Source: [[source-llm-wiki-pattern]]*
