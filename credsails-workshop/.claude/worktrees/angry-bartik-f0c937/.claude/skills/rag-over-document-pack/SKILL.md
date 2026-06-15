---
name: rag-over-document-pack
description: Use when designing a per-document-pack RAG chatbot for CovIQ (the VDR) or CredSails (modelling / DD / CAM packs) — plain-English Q&A with source tracing and mid-session document upload. NOT for general RAG infrastructure, vector-DB selection, or app search features — see `architect` for system design.
---

# RAG over the document pack (CovIQ & CredSails)

One of the six reusable primitives: a **Q&A chatbot scoped to one stage's document pack**, answering in plain English **with citations**, and allowing **mid-session document upload**.

## When to use / when not
- **Use** when designing the per-pack Q&A agent for a CovIQ or CredSails stage.
- **Not** for choosing RAG infrastructure, embeddings, or generic product search.

## How to design it
1. **Scope to the pack** — index exactly one stage's documents (VDR, modelling pack, DD pack, CAM file), not the whole world.
2. **Cite every answer** — responses trace to doc/page/section (`provenance-and-confidence`).
3. **Mid-session upload** — let the user add a document during the session and re-index (with approval).
4. **One per pack** — each stage that needs Q&A ships its own scoped chatbot.

## CovIQ example
In diligence, the *Document Q&A Agent: index all VDR docs* answers natural-language questions with doc/page/section citations and maintains a received-vs-pending checklist — turning a 200–600-document VDR into a queryable pack.

## CredSails example
The pattern is explicit and repeated: Stages 3, 4, and 7 **each ship a RAG Q&A agent over that stage's document pack**. The Stage 3 modelling chatbot traces figures to source and lets the analyst *upload supporting docs mid-session*.

## Pitfalls
- Answering without citations defeats the purpose for IC/regulator-facing work.
- A single global chatbot over all packs loses the per-stage scoping and confuses provenance.
- Allowing mid-session upload without an approval step bypasses document governance.

## Sources
- section_path: 2. How the two products compare
  quote: "RAG chatbot over the document pack"
- section_path: Step 3.1 — Full Diligence Management
  quote: "Document Q&A Agent: index all VDR docs"
- section_path: 4.6 CredSails cross-cutting patterns to internalise
  quote: "each ship a RAG Q&A agent over that stage's document pack"
- section_path: Stage 3 — Financial Modelling (6 agents)
  quote: "upload supporting docs mid-session"
