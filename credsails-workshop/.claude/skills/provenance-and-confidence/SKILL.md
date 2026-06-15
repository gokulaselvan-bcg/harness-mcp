---
name: provenance-and-confidence
description: Use when designing per-field citation, confidence tiering, and version-stamping for CovIQ or CredSails agent outputs (source page, confidence %, reliability tier, audit trail). NOT for general source citations, logging/observability, or VCS versioning in engineering work — for code review see `reviewer`, for system design see `architect`.
---

# Per-field provenance & confidence (CovIQ & CredSails)

One of the six reusable primitives: every machine-produced field carries **its source, a confidence signal, and a version stamp.** For these ratings-company products, traceability is a product requirement, not a UX nicety — outputs are IC- or regulator-facing.

## When to use / when not
- **Use** when designing how a CovIQ/CredSails agent attaches provenance to extracted or computed fields.
- **Not** for general engineering citations, audit logs, or git versioning.

## How to design it
1. **Per-field, not per-document** — citation granularity is the field (KPI, ratio, line item), with source page/doc.
2. **Confidence signal** — attach a confidence level; escalate low-confidence fields to HITL.
3. **Reliability tiering (credit)** — audited > reviewed > compiled > management-prepared; the tier sets the bar.
4. **Version stamp + audit trail** — every override/edit is stamped with rationale and author.

## CovIQ example
The CIM Extractor will *extract 30-50 KPIs w/ page citations*; the IC Pack Assembler will *flag low-confidence / thin-source sections* before the memo goes to committee. Provenance here protects the IC decision, not a regulator filing.

## CredSails example
The numeric tiering is a CredSails specialization of the shared pattern: confidence thresholds escalate **95% public/audited, 99% private management-prepared**, and Doc Intelligence writes a raw layer with **per-field confidence + page refs + GAAP/IFRS tag**. Because the CAM is regulator-facing, *Every override, edit, waiver, and triangulation break is version-stamped with rationale and analyst ID.*

## Pitfalls
- Document-level citations aren't enough — a reader must trace a *single field* to its source.
- Treating the 95%/99% thresholds as universal: they are CredSails' regulated specialization; CovIQ uses confidence *flagging*, not hard thresholds.
- Provenance without HITL escalation on low confidence is just decoration.

## Sources
- section_path: 2. How the two products compare
  quote: "Citation + traceability per field"
- section_path: Step 2.1 — CIM Extraction & Triage
  quote: "extract 30-50 KPIs w/ page citations"
- section_path: Step 4.1 — IC Memo Drafting & Deal Close
  quote: "flag low-confidence / thin-source sections"
- section_path: 4.6 CredSails cross-cutting patterns to internalise
  quote: "95% public/audited, 99% private management-prepared"
- section_path: Stage 2 — Doc Intelligence (6 agents)
  quote: "per-field confidence + page refs + GAAP/IFRS tag"
- section_path: 4.6 CredSails cross-cutting patterns to internalise
  quote: "Every override, edit, waiver, and triangulation break is version-stamped with rationale and analyst ID"
