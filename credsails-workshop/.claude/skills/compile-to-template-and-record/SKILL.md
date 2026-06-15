---
name: compile-to-template-and-record
description: Use when designing the orchestrator that compiles CovIQ/CredSails agent outputs into a firm-standard template (IC memo, CAM) and writes the result to the knowledge base / LOS / deal record, feeding downstream stages. NOT for generic build pipelines, templating engines, or API response shaping — see `architect` / `api-designer` for system and contract design.
---

# Compile-to-template-and-record (CovIQ & CredSails)

One of the six reusable primitives: a stage ends with an **orchestrator** that assembles upstream agent outputs into a **firm template** and **writes to the system of record**, where it feeds the next stage.

## When to use / when not
- **Use** when designing how a CovIQ/CredSails stage assembles its deliverable and persists it.
- **Not** for generic CI build steps, string templating, or HTTP response shaping.

## How to design it
1. **Single firm template** per artifact (IC memo, CAM) — agents fill sections; the orchestrator owns layout.
2. **Write to the system of record** — Knowledge Base / CRM (CovIQ); LOS (CredSails) — tagged for retrieval.
3. **Feed downstream** — the persisted record is the input to the next stage (no re-querying).
4. **Carry provenance through** — exhibits/sections keep their citations (`provenance-and-confidence`).

## CovIQ example
Early stages *compile firm-template package* and save to the Knowledge Base (tagged by sector/archetype/date); at close, the *Orchestrator saves memo/packs/exhibits/Q&A to KB* and logs the IC decision to CRM for future calibration.

## CredSails example
Stage 7 will *assemble the full Credit Application Memo from all prior stages* — CAM Generation produces a *full first-draft CAM* with inline citations, into the LOS. Upstream, the industry section is built so it *feeds Stage 7 CAM*.

## Pitfalls
- Letting each agent format its own output → inconsistent, non-comparable artifacts.
- Persisting the artifact but not the structured record → the next stage re-does work.
- Compiling without preserving per-field citations → the regulator-facing CAM loses traceability.

## Sources
- section_path: 2. How the two products compare
  quote: "Orchestrator compiles to firm template"
- section_path: Step 1.1 — Market Mapping & Universe Building
  quote: "compile firm-template package"
- section_path: Step 4.1 — IC Memo Drafting & Deal Close
  quote: "Orchestrator saves memo/packs/exhibits/Q&A to KB"
- section_path: Stage 7 — Underwriting Memo / CAM (5 agents)
  quote: "assemble the full **Credit Application Memo** from all prior stages"
- section_path: Stage 7 — Underwriting Memo / CAM (5 agents)
  quote: "full first-draft CAM"
- section_path: Stage 5 — Industry Analysis (6 agents)
  quote: "feeds Stage 7 CAM"
