# Spec: Schema-driven Balance Sheet Extractor Agent

**File:** `artifacts/tickets/WS-001/spec.md`
**Task ID:** WS-001
**Created:** 2026-06-12
**Status:** Draft

---

## Overview

Build a new CredSails hero agent — `schema_extractor` — that reads a borrower's financial-statement
PDF and extracts Balance Sheet line items matching a **runtime-provided row template** (label +
expected unit). The agent replaces the canned `DATA.balanceSheet` array in the Financial Analysis
prototype with real, cited extraction output.

**Why a new agent?** The existing `extractor.py` is bound to a hard-coded field set. Different
borrowers and credit templates require different line items; this agent takes the template at
runtime so one code path serves all borrower types without modification.

The new agent follows the identical live/stub seam used by the four existing hero agents:
`llm_client.complete()` → same Pydantic parse gate → same `store.py` persistence chain.

---

## Success Criteria

- **S001-PYDANTIC-GATE**: Every LLM response is parsed through `BSExtractionResult` before
  any caller receives it; a malformed response raises a validation error, never a raw exception.
- **S002-ALL-ROWS-POPULATED**: `populated` contains exactly one `BSExtractedRow` per
  `BSTemplateRow` in the input template (Q001 governs the no-match case).
- **S003-SOURCE-AND-CONFIDENCE**: Every `BSExtractedRow` carries a non-null `source_page` (int)
  and a `confidence` value in `{"L", "M", "H"}`.
- **S004-ENDPOINT-REACHABLE**: `POST /api/extract/balance-sheet` returns HTTP 200 with a
  populated JSON body for the staged Macy's PDF within 120 s.
- **S005-EXISTING-TESTS-PASS**: All thirteen existing tests continue to pass after the change.
- **S006-HITL-TRIGGER**: Any `BSExtractedRow` with `confidence == "L"` is surfaced in the
  Financial Analysis UI review flow (row-level flag; UI wire-up is out of scope for this ticket
  but the flag must be present in the API response).

---

## Requirements Analysis

### Functional Requirements

- **F001-AGENT-RUN**: The agent exposes a single callable `run(pdf_path: str, template: list[BSTemplateRow]) -> BSExtractionResult`.
- **F002-PDF-READ**: The agent reads the full text of `pdf_path` (resolved under `data/`).
- **F003-TEMPLATE-DRIVEN-PROMPT**: The prompt instructs Claude to find each `template[i].label`
  in the PDF Balance Sheet section and return the corresponding figure.
- **F004-CONFIDENCE-RUBRIC**: Claude is instructed to rate each row H/M/L per the existing
  prototype rubric:
  - `H` — explicitly stated on a labelled BS line.
  - `M` — calculated or derived from adjacent BS lines.
  - `L` — cross-section inference or ambiguous label; triggers HITL.
- **F005-ORDER-PRESERVED**: `populated` rows are returned in the same order as `template`.
- **F006-ENDPOINT**: `POST /api/extract/balance-sheet` accepts a JSON body
  `{"pdf_path": str, "template": [{"label": str, "expected_unit": str}]}` and returns the
  serialised `BSExtractionResult`.
- **F007-STUB-FIXTURE**: A JSON fixture file `fixtures/schema_extractor.json` provides a
  deterministic offline response; stub mode is selected automatically when no real API key is set.

### Non-Functional Requirements

- **N001-SYNC-HANDLER**: The FastAPI endpoint is a synchronous handler (FastAPI runs it in a
  threadpool). No `async def`, no background tasks.
- **N002-TIMEOUT**: `llm_client.complete()` timeout is 120 s (inherited from
  `settings.llm_timeout_seconds`).
- **N003-NO-STREAMING**: Response is collected as a single string; no server-sent events.
- **N004-SINGLE-PDF**: One PDF per call; no fan-out or batching.
- **N005-BACKWARDS-COMPAT**: No existing model, endpoint, or test is modified (additive only).

### Dependencies

- **D001-LLM-CLIENT**: `backend/src/app/llm_client.py` — reuse `complete()` and `provenance()`.
  No new subprocess mechanism.
- **D002-PROMPTS-MODULE**: `backend/src/app/prompts/__init__.py` — add
  `SCHEMA_EXTRACTOR_INSTRUCTIONS` constant and reuse `cached_doc_blocks()`.
- **D003-SCHEMAS-MODULE**: `backend/src/app/schemas.py` — add `BSTemplateRow`,
  `BSExtractedRow`, `BSExtractionResult` as additive models.
- **D004-MAIN-PY**: `backend/src/app/main.py` — register one new route; no existing routes change.
- **D005-PDF-FILE**: `data/workshop_macys_bs.pdf` — pre-staged; callers pass the filename,
  the agent resolves the path against `data/`.
- **D006-FIXTURE-FILE**: `backend/src/app/fixtures/schema_extractor.json` — must exist before
  any test runs; mirrors the shape of a real `BSExtractionResult`.

### Edge Cases

- **E001-NO-MATCH**: A template row whose label is not found in the PDF. **Resolution governed
  by Q001.** Until resolved, treat as a blocking gap — do not implement silently.
- **E002-AMBIGUOUS-LABEL**: Two Balance Sheet lines that could match the same template label
  (e.g. "Total liabilities" vs "Total liabilities and equity"). Agent uses confidence `L` and
  returns the closer match; analyst reviews in HITL.
- **E003-UNIT-MISMATCH**: Extracted figure appears to be in a different unit than
  `expected_unit`. Agent includes the raw figure with confidence `M` or `L` and a note; unit
  normalisation is out of scope.
- **E004-STUB-MISSING-FIXTURE**: If stub mode is active but `fixtures/schema_extractor.json`
  is absent, `llm_client._stub()` raises `LLMError`; the existing `_llm_error` handler returns
  HTTP 502.
- **E005-MALFORMED-LLM-RESPONSE**: If the live LLM response is not valid JSON or fails Pydantic
  validation, the exception propagates through `LLMError` → HTTP 502 (consistent with other agents).

### Out of Scope

- Income Statement extraction (separate agent, later).
- Cash Flow extraction (separate agent, later).
- PDF upload via multipart — caller supplies a pre-staged path.
- Prototype UI wire-up (handled separately at end of workshop if time permits).
- Schema validation of the template beyond Pydantic type checks (ARD explicit non-goal).
- Borrowers other than Macy's for the workshop demo.

---

## Technical Approach

Follow the **identical pattern** established by the four existing hero agents:

1. Add prompt constant(s) to `prompts/__init__.py`.
2. Add three Pydantic models to `schemas.py`.
3. Create `agents/schema_extractor.py` with a single `run()` function that calls
   `llm_client.complete()` and parses through the new models.
4. Add a JSON fixture `fixtures/schema_extractor.json` for stub mode.
5. Register `POST /api/extract/balance-sheet` in `main.py` using the same sync-handler pattern.
6. Add tests in `tests/test_schema_extractor.py`.

No new libraries. No subprocess subprocess. PDF text is extracted using the existing `retrieval.py`
text extraction path (or equivalent — see Q002).

### Related ADRs

No ADRs recorded yet. If a decision about no-match handling (Q001) or PDF text extraction method
(Q002) rises to architectural significance, create one via `/adr`.

### Code Quality Considerations

General standards (apply to all new files):
- **Y100-SINGLE-RESPONSIBILITY**: `schema_extractor.py` has exactly one job — run the LLM call
  and parse the result. PDF reading and HTTP binding stay in their respective layers.
- **Y103-DEPENDENCY-INJECTION**: `run()` accepts `pdf_path` and `template` as parameters; no
  global state, no module-level singletons.
- **Z102-GOD-OBJECTS**: `BSExtractionResult` must not grow miscellaneous fields; it is the
  verbatim agent output shape.
- **Z200-LEAKY-ABSTRACTION**: The stub/live switch belongs in `llm_client.py`; `schema_extractor.py`
  must not branch on `settings.placeholder_key`.

Python-specific:
- **PY101-TYPE-ANNOTATIONS**: All public functions fully annotated; `from __future__ import annotations`
  at the top of every new file.
- **PY200-PYDANTIC-MODELS**: Use `model_validate_json()` (Pydantic v2) — not `parse_raw()` — consistent
  with `extractor.py:12`.
- **PZ101-BARE-EXCEPT**: No bare `except`; catch `LLMError` or `ValidationError` explicitly.

---

## Detailed Component Design

### C001-SCHEMA-EXTRACTOR-AGENT

**File:** `backend/src/app/agents/schema_extractor.py`

**Responsibilities:**
- Accept `pdf_path: str` and `template: list[BSTemplateRow]`.
- Build the system prompt from `prompts.SCHEMA_EXTRACTOR_INSTRUCTIONS` and the PDF text.
- Build the user message listing the template row labels.
- Call `llm_client.complete("schema_extractor", "extract", system, messages, max_tokens=2048)`.
- Parse the raw JSON string via `BSExtractionResult.model_validate_json(raw)`.
- Return the validated `BSExtractionResult`.

**Public interface:**
- **A001-RUN**: `run(pdf_path: str, template: list[BSTemplateRow]) -> BSExtractionResult`

**Error handling:**
- `LLMError` propagates; caller (endpoint) returns HTTP 502 via existing handler.
- `ValidationError` propagates; endpoint catches via existing `LLMError` handler or returns 422.

**Follows:** Y100-SINGLE-RESPONSIBILITY, Y103-DEPENDENCY-INJECTION, PY101-TYPE-ANNOTATIONS, PY200-PYDANTIC-MODELS
**Avoids:** Z200-LEAKY-ABSTRACTION (no `settings.placeholder_key` check here), PZ101-BARE-EXCEPT

---

### C002-PROMPT-CONSTANT

**File:** `backend/src/app/prompts/__init__.py` (additive only)

**Responsibilities:**
- Define `SCHEMA_EXTRACTOR_INSTRUCTIONS: str` — the system instruction telling Claude to match
  each label in the Balance Sheet, emit a value, `source_page`, and `confidence` (H/M/L), and
  respond with JSON matching the `BSExtractionResult` shape.

**A002-CACHED-DOC-BLOCKS**: Reuse existing `cached_doc_blocks(instructions, doc_text)` to build
the system blocks list — no new helper needed.

---

### C003-ENDPOINT

**File:** `backend/src/app/main.py` (additive only)

**Responsibilities:**
- Define request body `BSExtractReq(BaseModel)` with `pdf_path: str` and
  `template: list[BSTemplateRow]`.
- Register `POST /api/extract/balance-sheet` as a sync handler.
- Call `agents.schema_extractor.run(body.pdf_path, body.template)`.
- Return `BSExtractionResult` (Pydantic `.model_dump()` serialised by FastAPI).

**A003-ENDPOINT**: `POST /api/extract/balance-sheet`
- Request: `{"pdf_path": "workshop_macys_bs.pdf", "template": [...]}`
- Response 200: `{"populated": [{"label", "value", "source_page", "confidence"}, ...]}`
- Response 502: `{"error": "llm_error", "detail": "..."}` (via existing handler)

**Follows:** N001-SYNC-HANDLER, N005-BACKWARDS-COMPAT
**Avoids:** Z102-GOD-OBJECTS (request body is a thin DTO, not a fat model)

---

## Data Model

### M001-BS-TEMPLATE-ROW

**File:** `backend/src/app/schemas.py`

Purpose: Represents one requested line item in the caller's extraction template.

| Field           | Type  | Notes                                     |
|-----------------|-------|-------------------------------------------|
| `label`         | `str` | Human-readable BS line name (e.g. "Total assets") |
| `expected_unit` | `str` | Default `"USD millions"`; informational only |

**Validation rules:**
- **V001-LABEL-NONEMPTY**: `label` must be a non-empty string.

**Follows:** PY200-PYDANTIC-MODELS
**Avoids:** Z102-GOD-OBJECTS

---

### M002-BS-EXTRACTED-ROW

**File:** `backend/src/app/schemas.py`

Purpose: One agent-produced row: the extracted figure for a single template label.

| Field         | Type                    | Notes                                             |
|---------------|-------------------------|---------------------------------------------------|
| `label`       | `str`                   | Must match the template row label verbatim        |
| `value`       | `str`                   | Extracted numeric figure as a string              |
| `source_page` | `int`                   | 1-based PDF page number                           |
| `confidence`  | `Literal["L","M","H"]`  | HITL trigger when `"L"`                           |

**Validation rules:**
- **V002-CONFIDENCE-ENUM**: `confidence` must be exactly one of `"L"`, `"M"`, `"H"`.
- **V003-SOURCE-PAGE-POSITIVE**: `source_page >= 1`.

**Follows:** PY200-PYDANTIC-MODELS, PY101-TYPE-ANNOTATIONS
**Avoids:** Z102-GOD-OBJECTS

---

### M003-BS-EXTRACTION-RESULT

**File:** `backend/src/app/schemas.py`

Purpose: Top-level agent output; the JSON envelope Claude responds with and the endpoint returns.

| Field       | Type                   | Notes                            |
|-------------|------------------------|----------------------------------|
| `populated` | `list[BSExtractedRow]` | One entry per template row (see Q001) |

**Validation rules:**
- **V004-POPULATED-NONEMPTY**: `populated` must have at least one item (guards against an empty
  LLM response slipping through).

**Follows:** PY200-PYDANTIC-MODELS
**Avoids:** Z102-GOD-OBJECTS

---

## Testing Strategy

### Unit Test Scenarios

- **U001-MODEL-ROUND-TRIP-TEMPLATE-ROW**: Instantiate `BSTemplateRow` with valid and invalid
  data; assert Pydantic raises on empty label. Validates M001, V001.
- **U002-MODEL-ROUND-TRIP-EXTRACTED-ROW**: Instantiate `BSExtractedRow`; assert confidence
  rejects values outside `{"L","M","H"}` and `source_page < 1`. Validates M002, V002, V003.
- **U003-MODEL-ROUND-TRIP-EXTRACTION-RESULT**: Round-trip `BSExtractionResult` as JSON string
  via `model_validate_json()`. Validates M003, S001.
- **U004-AGENT-STUB**: Call `schema_extractor.run()` in stub mode (fixture present); assert the
  return value is a valid `BSExtractionResult` and `populated` is non-empty. Validates F001, S001.
- **U005-AGENT-LLM-ERROR**: Patch `llm_client.complete` to raise `LLMError`; assert it
  propagates out of `run()` unchanged (no swallowing). Validates E005.

### Integration Test Scenarios

- **I001-ENDPOINT-STUB**: `POST /api/extract/balance-sheet` with a valid body in stub mode;
  assert HTTP 200, `populated` list has correct length, each row has `source_page` and
  `confidence`. Validates F006, S003, S004.
- **I002-ENDPOINT-MISSING-FIXTURE**: Rename/remove fixture, call endpoint in stub mode; assert
  HTTP 502. Validates E004.
- **I003-EXISTING-SUITE-UNCHANGED**: Run full existing test suite; assert all 13 tests still
  pass. Validates S005, N005.

### Test Data Requirements

- **T001-STUB-FIXTURE**: `backend/src/app/fixtures/schema_extractor.json` — a valid
  `BSExtractionResult` JSON with 7 rows matching the example template (Cash & equivalents,
  Total current assets, Total assets, Total debt, Total current liabilities, Total liabilities,
  Total equity); each row has a realistic `source_page` (2–4) and `confidence` in
  `{"H","M","L"}`. At least one row must have `confidence == "L"` to exercise E001/S006.
- **T002-MACYS-PDF**: `data/workshop_macys_bs.pdf` — pre-staged; used by I001 in live mode
  integration smoke test only.

---

## Risk Assessment

- **R001-NO-MATCH-UNDEFINED**: The ARD does not specify what to do when a template label has no
  match in the PDF. Shipping without a decision risks silently omitting rows (violates S002) or
  returning a malformed response (violates S001). **Mitigation:** resolve Q001 before
  implementation begins.
- **R002-PDF-TEXT-EXTRACTION**: Method for reading PDF text is not specified in the ARD. If the
  existing `retrieval.py` path extracts insufficient text for multi-page PDFs, the agent will
  produce low-confidence or missing rows. **Mitigation:** resolve Q002; validate against
  `data/workshop_macys_bs.pdf` in the test run.
- **R003-PROMPT-BRITTLENESS**: Template-driven prompts must enumerate all label strings in the
  user message. Claude may hallucinate values if labels are vague. **Mitigation:** confidence
  rubric forces `L` on ambiguous matches and the HITL gate catches them before the spread.

---

## Open Questions

### Q001-NO-MATCH-ROW-HANDLING
**Question:** What should the agent return for a `BSTemplateRow` whose label is not found in
the PDF Balance Sheet?

**Context:** The ARD "Behavior" section (steps 2–4) only covers the happy path. S002 requires
one `BSExtractedRow` per template row. If the agent simply omits a row, `populated` will have
fewer items than `template`, breaking downstream callers that rely on positional alignment.

**Possible answers:**
1. **Null-value sentinel** — include the row with `value = null` (or `"N/A"`), `source_page = 0`,
   `confidence = "L"`. Analyst sees it in HITL and manually fills it. Preserves row count (S002).
2. **Omit silently** — `populated` may be shorter than `template`. Downstream caller must
   tolerate missing rows. Breaks positional assumption.
3. **Hard error** — `run()` raises `LLMError` if any row is missing. Safe but blocks the whole
   extraction if even one label is absent.
4. **LLM best-guess with `L` confidence** — instruct Claude to always return a row even when
   uncertain, using `confidence = "L"` for anything ambiguous or absent. Closest match
   selected, flagged for review.

**Recommended:** Option 4 (LLM best-guess, `L` confidence) — consistent with the confidence
rubric in the ARD and least disruptive to the downstream data model.

**Who decides:** Workshop driver / product owner.

**Impact:** Affects `SCHEMA_EXTRACTOR_INSTRUCTIONS` wording, V004, S002, and the fixture T001.

---

### Q002-PDF-TEXT-EXTRACTION-METHOD
**Question:** Which mechanism extracts raw text from the PDF before it is injected into the
Claude prompt?

**Context:** `extractor.py` receives `doc_text: str` already extracted by the orchestrator
(via `retrieval.py`). The new endpoint receives only a `pdf_path`. It is unclear whether the
agent should:

1. Call `retrieval.py`'s extraction helper directly.
2. Use `pypdf` / `pdfminer` inline in `schema_extractor.py`.
3. Expect the *caller* (endpoint) to pre-extract and pass text.

**Recommended:** Option 1 — reuse `retrieval.py`; keeps PDF handling in one place.

**Who decides:** Workshop driver.

**Impact:** Affects C001, A001 signature (whether `pdf_path` or `doc_text` is passed internally),
and test setup for I001.
