# Agent Requirement Document — Balance Sheet Extractor

**Agent name:** `schema_extractor` (balance-sheet variant)
**Owner:** CredSails workshop fork
**Status:** Draft — awaiting `/spec` review
**Related ticket:** `WS-001`

> **NOTE TO WORKSHOP DRIVER:**
> This ARD is intentionally **incomplete**. The "Behavior" section silently
> omits how the agent handles a template row that has no match in the source
> PDF. The `/spec` adversarial reviewers should flag this gap. If they miss it,
> the runbook gives you a one-line lead-in to surface it. Leave the omission in
> place when you copy this file into the fork.

---

## Purpose

Extract Balance Sheet line items from a borrower's financial-statement PDF,
matching the line items the caller has requested in a row-template. Output a
structured set of (label, value, source page, confidence) records that the
CredSails Financial Analysis workspace can render directly.

This replaces the canned `DATA.balanceSheet` array used by the prototype's
Financial Analysis page with real, cited extraction output.

## Why a schema-driven agent (and not the existing `extractor.py`)

The existing `backend/src/app/agents/extractor.py` is bound to a single
hard-coded set of 10-K credit fields. Different borrowers and different credit
templates need different line items. Re-prompting the agent in code each time
defeats the credsails goal of "one harness, many borrowers." This agent takes
the **row template at runtime**, so the same code serves Generic, Financial
Institutions, and (later) Industrials templates without modification.

## Inputs

| Field      | Type                  | Notes                                                                  |
|------------|-----------------------|------------------------------------------------------------------------|
| `pdf_path` | `str`                 | Path under `data/`. Pre-staged for the workshop demo.          |
| `template` | `list[BSTemplateRow]` | Each row carries `label: str` and `expected_unit: str` (default `"USD millions"`). |

Example template:

```json
[
  {"label": "Cash & equivalents",       "expected_unit": "USD millions"},
  {"label": "Total current assets",     "expected_unit": "USD millions"},
  {"label": "Total assets",             "expected_unit": "USD millions"},
  {"label": "Total debt",               "expected_unit": "USD millions"},
  {"label": "Total current liabilities","expected_unit": "USD millions"},
  {"label": "Total liabilities",        "expected_unit": "USD millions"},
  {"label": "Total equity",             "expected_unit": "USD millions"}
]
```

## Outputs

| Field       | Type                  | Notes                                                              |
|-------------|-----------------------|--------------------------------------------------------------------|
| `populated` | `list[BSExtractedRow]`| Each row: `label`, `value`, `source_page: int`, `confidence: "L"|"M"|"H"` |

Confidence rubric (from existing prototype usage, preserved here for parity):

- `H`: value is explicitly stated on a clearly labeled line in the BS.
- `M`: value is calculated or derived from adjacent BS lines.
- `L`: value required cross-section inference, or label is ambiguous. **HITL
  review required** by the analyst before it enters the spread.

## Behavior

1. The agent shall read the source PDF text (`pdf_path` resolved under
   `data/`).
2. For each row in `template`, the agent shall find the corresponding figure in
   the PDF Balance Sheet section.
3. The agent shall emit a value, the page on which it was found, and a
   confidence grade.
4. The agent shall return all extracted rows in `populated`, preserving the
   order of `template`.

## Constraints

- Sync execution; FastAPI threadpool handles long Claude calls.
- `claude` CLI subprocess timeout: 120 seconds.
- Output validated by `BSExtractionResult` Pydantic model before persistence.
- Result persisted via existing `store.py` (versioning + audit-chain).
- No streaming.
- No multi-document fan-out — one PDF per call.

## Non-goals

- Income Statement extraction (separate agent later).
- Cash Flow extraction (separate agent later).
- PDF upload via multipart — caller passes a pre-staged path.
- Schema validation of the caller's `template` beyond Pydantic type checks.
- Borrower other than Macy's for the workshop demo.

## Success criteria

- The agent passes the Pydantic gate on every response.
- Every row in `populated` carries a `source_page` and `confidence`.
- Low-confidence (`L`) rows trigger the existing HITL review flow in the
  prototype Financial Analysis UI.
- The endpoint completes in under 120 seconds on the workshop PDF.
- Existing tests (the four hero agents, the canned modules) continue to pass.

## Open questions for review

- *(none currently identified — to be expanded during `/spec` adversarial review)*

---

## Appendix — relationship to existing artifacts

- Pydantic models live in `backend/src/app/schemas.py` (new additions:
  `BSTemplateRow`, `BSExtractedRow`, `BSExtractionResult`).
- Agent code lives in `backend/src/app/agents/schema_extractor.py` (new file).
- Endpoint lives in `backend/src/app/main.py` (`POST /api/extract/balance-sheet`).
- Persistence reuses `backend/src/app/store.py` and `backend/src/app/audit.py`
  without modification.
