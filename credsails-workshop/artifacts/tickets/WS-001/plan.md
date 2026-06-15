# Implementation Plan: Schema-driven Balance Sheet Extractor Agent

**File:** `artifacts/tickets/WS-001/plan.md`
**Spec:** `artifacts/tickets/WS-001/spec.md`
**Task ID:** WS-001
**Created:** 2026-06-12
**Status:** Completed

---

## Progress Summary

**Status:** Completed
**Last Updated:** 2026-06-12
**Completed Steps:** 6 / 6

---

## 0. Preconditions, Open Questions, and Risks

### Preconditions

- Backend virtualenv is active (`source backend/.venv/bin/activate`) and `pip install -e ".[dev]"` has run.
- `data/workshop_macys_bs.pdf` exists (pre-staged — confirmed in repo).
- Existing test suite passes before any change: `cd backend && pytest` → 13 green.

### Open Questions — Resolved Here

**Q001-NO-MATCH-ROW-HANDLING → Option 4 adopted.**
The prompt will instruct Claude: *"Always return one row per template label. If a figure cannot
be located confidently, return your best estimate or 'N/A' as the value with `confidence = 'L'`."*
This preserves positional alignment (one row per template entry), surfaces ambiguity to the
analyst via the HITL gate, and requires no special null-handling in the Pydantic model (S002).
Impact: `SCHEMA_EXTRACTOR_INSTRUCTIONS` wording, T001 fixture must include at least one `"L"` row.

**Q002-PDF-TEXT-EXTRACTION → `pypdf` inline in `schema_extractor.py`.**
`pypdf>=4.0` is already in `pyproject.toml` (no new dependency). The agent uses
`pypdf.PdfReader` to extract page text, wraps each page in `===PAGE N===` markers (matching
the format `orchestrator._load_pages()` already uses for `clf_10k.txt`), then passes the
assembled string to `prompts.cached_doc_blocks()`. Source-page attribution flows naturally
because the markers are visible to Claude in the prompt.

### Risks

- **R001-NO-MATCH-UNDEFINED**: Resolved by Q001 decision above.
- **R002-PDF-TEXT-EXTRACTION**: `pypdf` text quality on the workshop PDF is unknown. Validated
  in K002 smoke test. If text extraction is poor, the plan note in K002 flags the fallback
  (pre-convert to `.txt` the same way `clf_10k.txt` was created).
- **R003-PROMPT-BRITTLENESS**: Confidence rubric instructions keep low-quality extractions
  flagged `L`; HITL gate catches them before the spread.

---

## 1. Implementation Strategy

**Critical path:** Models → Prompt → Fixture → Agent → Endpoint → Tests

All changes are purely additive (N005). The five existing hero-agent files are untouched.
The new files follow the exact same structural pattern:

```
prompts/__init__.py  ← add constant
schemas.py           ← add 3 models
fixtures/schema_extractor.json  ← stub response
agents/schema_extractor.py      ← new agent
main.py              ← add 1 route + 1 request body
tests/test_schema_extractor.py  ← new test file
```

No architectural decisions rise to ADR level (additive, no infrastructure change). No ADRs
exist yet in this repo.

Parallel opportunity: P002 (prompt) and P003 (fixture) are independent of each other and can
be written in either order, but both must complete before P004 (agent).

---

## 1b. Related Documentation

- Spec: `artifacts/tickets/WS-001/spec.md`
- ARD: `artifacts/tickets/WS-001/ard.md`
- Analogous agent: `backend/src/app/agents/extractor.py` (pattern to mirror)
- Analogous test: `backend/tests/test_llm_mode.py` (stub fixture parity test pattern)
- Existing prompt module: `backend/src/app/prompts/__init__.py`

---

## 2. Requirements Traceability

| Spec ID | How covered |
|---|---|
| F001-AGENT-RUN | P004: `run(pdf_path, template) -> BSExtractionResult` |
| F002-PDF-READ | P004: `pypdf.PdfReader` reads PDF under `settings.data_dir` |
| F003-TEMPLATE-DRIVEN-PROMPT | P002: `SCHEMA_EXTRACTOR_INSTRUCTIONS`; P004 builds user message from template labels |
| F004-CONFIDENCE-RUBRIC | P002: H/M/L rubric in instruction constant |
| F005-ORDER-PRESERVED | P002: prompt instructs Claude to preserve order; P001 M003 validates list |
| F006-ENDPOINT | P005: `POST /api/extract/balance-sheet` |
| F007-STUB-FIXTURE | P003: `fixtures/schema_extractor.json` |
| N001-SYNC-HANDLER | P005: `def` (not `async def`) endpoint |
| N002-TIMEOUT | P004: inherited via `llm_client.complete()` → `settings.llm_timeout_seconds` |
| N003-NO-STREAMING | P004: `complete()` returns a single string |
| N004-SINGLE-PDF | P001/P004: `pdf_path: str` (scalar) |
| N005-BACKWARDS-COMPAT | All steps: additive only; verified in K003 |
| E001-NO-MATCH | P002: Q001 resolution baked into prompt instruction |
| E002-AMBIGUOUS-LABEL | P002: confidence rubric forces `L`; no code change needed |
| E003-UNIT-MISMATCH | P002: prompt instructs Claude to note unit discrepancy in value string with `L`/`M` |
| E004-STUB-MISSING-FIXTURE | Existing `llm_client._stub` raises `LLMError` → 502; tested in I002 |
| E005-MALFORMED-LLM-RESPONSE | P004: `model_validate_json` raises; propagates as `LLMError` |

---

## 2b. Testing Strategy

**Approach:** Write the stub fixture (P003) and model definitions (P001) before the agent (P004).
The fixture serves as a contract that drives both the implementation and the tests — a lightweight
TDD anchor.

**Test types:**
- **Unit:** Pydantic model round-trips (U001–U003); agent call with mock (U004–U005).
- **Integration:** Endpoint via `TestClient` (I001–I002).
- **Regression:** Full existing suite run (I003) at K003.

**Checkpoint placement:**
- K001 after P001 — models must parse correctly before the agent or endpoint is written.
- K002 after P004 — agent stub call must return a valid result before the endpoint is wired.
- K003 after P006 — full suite (new + existing) must be green before any commit.

---

## 3. Implementation Steps (P###)

### Work Package: Foundation (Models + Prompt + Fixture)

- [x] **P001-ADD-PYDANTIC-MODELS**
  - **Purpose**: Define the three new Pydantic models that form the shared contract between
    the stub fixture, the live LLM response, and the endpoint serialiser.
  - **What to do**:
    1. Open `backend/src/app/schemas.py`.
    2. Append `BSTemplateRow`, `BSExtractedRow`, `BSExtractionResult` after the existing models.
    3. Use `Literal["L", "M", "H"]` for `BSExtractedRow.confidence`.
    4. Add `Field(ge=1)` constraint on `BSExtractedRow.source_page`.
    5. Add `Field(min_length=1)` on `BSTemplateRow.label`.
    6. Add `Field(min_length=1)` on `BSExtractionResult.populated` (V004).
  - **Interface/contract notes**:
    - `BSTemplateRow`: `label: str`, `expected_unit: str = "USD millions"`
    - `BSExtractedRow`: `label: str`, `value: str`, `source_page: int (≥1)`, `confidence: Literal["L","M","H"]`
    - `BSExtractionResult`: `populated: list[BSExtractedRow] (min 1 item)`
    - All models inherit `BaseModel`; no `orm_mode` needed (not persisted directly).
  - **Implements**: M001, M002, M003, V001, V002, V003, V004
  - **Files affected**:
    - **W001**: `backend/src/app/schemas.py` (modify — additive append)
  - **Code quality**:
    - **Follows**: Y100-SINGLE-RESPONSIBILITY, PY101-TYPE-ANNOTATIONS, PY200-PYDANTIC-MODELS
    - **Avoids**: Z102-GOD-OBJECTS (no extra fields beyond the ARD contract)
  - **Dependencies**: none
  - **Validation**: `pytest tests/test_schema_extractor.py::test_bs_template_row_valid` — added in P006, but models can be spot-checked with a Python REPL round-trip after this step.

---

- [x] **P002-ADD-PROMPT-CONSTANT**
  - **Purpose**: Define `SCHEMA_EXTRACTOR_INSTRUCTIONS` in the prompts module, incorporating
    the Q001 no-match resolution and the H/M/L confidence rubric.
  - **What to do**:
    1. Open `backend/src/app/prompts/__init__.py`.
    2. Append `SCHEMA_EXTRACTOR_INSTRUCTIONS` constant (string).
    3. Instruction must:
       - Tell Claude it is a balance-sheet extraction agent.
       - List the H/M/L rubric (H = explicit label, M = derived, L = inferred/ambiguous/not found).
       - Instruct Claude to **always** return one row per template label even if the figure
         is absent — use `value = "N/A"` and `confidence = "L"` in that case (Q001 decision).
       - Specify the exact JSON response envelope:
         `{"populated": [{"label", "value", "source_page", "confidence"}]}`.
       - Remind Claude that pages are delimited by `===PAGE N===` markers so it can report
         the correct `source_page`.
  - **Implements**: F003, F004, E001, E002, E003
  - **Files affected**:
    - **W002**: `backend/src/app/prompts/__init__.py` (modify — additive append)
  - **Code quality**:
    - **Follows**: Y100-SINGLE-RESPONSIBILITY (prompt constants only; no logic)
    - **Avoids**: Z200-LEAKY-ABSTRACTION (no settings imports in prompts module)
  - **Dependencies**: none
  - **Validation**: Visual review of the constant; full validation deferred to K002.

---

- [x] **P003-CREATE-STUB-FIXTURE**
  - **Purpose**: Create `fixtures/schema_extractor.json` — the deterministic offline response
    that stub mode returns. This is the contract T001 specifies.
  - **What to do**:
    1. Create `backend/src/app/fixtures/schema_extractor.json`.
    2. The JSON must be a valid `BSExtractionResult` — a single object with key `"populated"`.
    3. Include exactly 7 rows matching the example template from the ARD:
       Cash & equivalents, Total current assets, Total assets, Total debt,
       Total current liabilities, Total liabilities, Total equity.
    4. Each row: `label`, `value` (realistic Macy's-plausible figure), `source_page` (2–4),
       `confidence` ∈ `{"H","M","L"}`.
    5. At least one row must have `confidence = "L"` (exercises HITL trigger path, S006).
    6. Example row: `{"label": "Total assets", "value": "9134", "source_page": 3, "confidence": "H"}`
  - **Interface/contract notes**: Must parse cleanly through `BSExtractionResult.model_validate_json()`.
  - **Implements**: F007, T001, S006
  - **Files affected**:
    - **W003**: `backend/src/app/fixtures/schema_extractor.json` (create)
  - **Code quality**:
    - **Follows**: PY200-PYDANTIC-MODELS (fixture is validated by the same model as the live path)
  - **Dependencies**: P001 (model must be defined to validate the fixture shape mentally)
  - **Validation**: Python one-liner after creation:
    ```
    python -c "from app.schemas import BSExtractionResult; import pathlib; BSExtractionResult.model_validate_json(pathlib.Path('src/app/fixtures/schema_extractor.json').read_text()); print('ok')"
    ```
    Run from `backend/` with venv active.

---

### Work Package: Agent + Endpoint

- [x] **P004-CREATE-AGENT**
  - **Purpose**: Implement `agents/schema_extractor.py` — the new hero agent that reads a PDF
    and extracts Balance Sheet rows via Claude.
  - **What to do**:
    1. Create `backend/src/app/agents/schema_extractor.py`.
    2. Add `from __future__ import annotations` and typed imports.
    3. Implement PDF text extraction helper: use `pypdf.PdfReader` to read each page; build
       the assembled string as `"\n\n".join(f"===PAGE {i+1}===\n{page.extract_text()}" for i, page in enumerate(reader.pages))`.
       Resolve `pdf_path` against `settings.data_dir`.
    4. Implement `run(pdf_path: str, template: list[BSTemplateRow]) -> BSExtractionResult`:
       - Extract PDF text (step 3).
       - Build system blocks: `prompts.cached_doc_blocks(prompts.SCHEMA_EXTRACTOR_INSTRUCTIONS, pdf_text)`.
       - Build user message: list the template labels as a JSON array in the message text so
         Claude knows exactly which rows to extract.
       - Call `llm_client.complete("schema_extractor", "extract", system, messages, max_tokens=2048)`.
       - Parse: `return BSExtractionResult.model_validate_json(raw)`.
    5. No imports of `settings.placeholder_key` or any stub-selection logic.
  - **Interface/contract notes**:
    - `run(pdf_path: str, template: list[BSTemplateRow]) -> BSExtractionResult`
    - `pdf_path` is resolved to `settings.data_dir / pdf_path`; caller passes filename only.
  - **Implements**: C001, A001, F001, F002, F003, F005, N002, N003, N004, E005
  - **Files affected**:
    - **W004**: `backend/src/app/agents/schema_extractor.py` (create)
  - **Code quality**:
    - **Follows**: Y100-SINGLE-RESPONSIBILITY, Y103-DEPENDENCY-INJECTION, PY101-TYPE-ANNOTATIONS, PY200-PYDANTIC-MODELS
    - **Avoids**: Z200-LEAKY-ABSTRACTION (no stub/live branching), PZ101-BARE-EXCEPT (no bare except)
  - **Dependencies**: P001 (models), P002 (prompt constant), P003 (fixture — for stub path)
  - **Validation**: See K002.

---

- [x] **P005-REGISTER-ENDPOINT**
  - **Purpose**: Add `POST /api/extract/balance-sheet` to `main.py` as a sync handler.
  - **What to do**:
    1. Open `backend/src/app/main.py`.
    2. Add import: `from .agents import schema_extractor`.
    3. Add import of the new schemas at the top of the request-body section:
       `from .schemas import BSTemplateRow, BSExtractionResult`.
    4. Define request body class (after existing classes):
       ```python
       class BSExtractReq(BaseModel):
           pdf_path: str
           template: list[BSTemplateRow]
       ```
    5. Register the route **before the `StaticFiles` mount** (all API routes must precede it):
       ```python
       @app.post("/api/extract/balance-sheet")
       def extract_balance_sheet(body: BSExtractReq):
           result = schema_extractor.run(body.pdf_path, body.template)
           return result.model_dump()
       ```
    6. No `Depends(get_session)` needed — the endpoint does not touch the DB.
  - **Interface/contract notes**:
    - Request: `{"pdf_path": "workshop_macys_bs.pdf", "template": [{"label": "...", "expected_unit": "USD millions"}]}`
    - Response 200: `{"populated": [{"label", "value", "source_page", "confidence"}]}`
    - Response 502: existing `LLMError` handler fires automatically.
  - **Implements**: C003, A003, F006, N001, N005
  - **Files affected**:
    - **W005**: `backend/src/app/main.py` (modify — additive; no existing route changed)
  - **Code quality**:
    - **Follows**: Y100-SINGLE-RESPONSIBILITY, N001-SYNC-HANDLER
    - **Avoids**: Z102-GOD-OBJECTS (`BSExtractReq` is a thin DTO)
  - **Dependencies**: P004 (agent), P001 (models)
  - **Validation**: See K002 (endpoint smoke via `TestClient`).

---

### Work Package: Tests

- [x] **P006-WRITE-TESTS**
  - **Purpose**: Write the full test file covering U001–U005, I001–I002, and implicitly I003.
  - **What to do**:
    1. Create `backend/tests/test_schema_extractor.py`.
    2. Implement the following test functions (see spec U/I IDs for each):

    **U001-MODEL-ROUND-TRIP-TEMPLATE-ROW**
    ```python
    def test_bs_template_row_valid():
        row = BSTemplateRow(label="Total assets", expected_unit="USD millions")
        assert row.label == "Total assets"

    def test_bs_template_row_rejects_empty_label():
        with pytest.raises(ValidationError):
            BSTemplateRow(label="", expected_unit="USD millions")
    ```

    **U002-MODEL-ROUND-TRIP-EXTRACTED-ROW**
    ```python
    def test_bs_extracted_row_rejects_bad_confidence():
        with pytest.raises(ValidationError):
            BSExtractedRow(label="x", value="1", source_page=1, confidence="X")

    def test_bs_extracted_row_rejects_zero_source_page():
        with pytest.raises(ValidationError):
            BSExtractedRow(label="x", value="1", source_page=0, confidence="H")
    ```

    **U003-MODEL-ROUND-TRIP-EXTRACTION-RESULT**
    ```python
    def test_bs_extraction_result_json_round_trip():
        raw = '{"populated": [{"label": "Total assets", "value": "9134", "source_page": 3, "confidence": "H"}]}'
        result = BSExtractionResult.model_validate_json(raw)
        assert result.populated[0].confidence == "H"
    ```

    **U004-AGENT-STUB**
    ```python
    def test_schema_extractor_stub_returns_valid_result():
        template = [BSTemplateRow(label="Total assets")]
        result = schema_extractor.run("workshop_macys_bs.pdf", template)
        assert isinstance(result, BSExtractionResult)
        assert len(result.populated) >= 1
        for row in result.populated:
            assert row.source_page >= 1
            assert row.confidence in {"L", "M", "H"}
    ```
    *(Stub mode active because no real API key is set in tests — mirrors `test_llm_mode.py` pattern.)*

    **U005-AGENT-LLM-ERROR**
    ```python
    def test_schema_extractor_propagates_llm_error(monkeypatch):
        from app import llm_client
        from app.llm_client import LLMError
        monkeypatch.setattr(llm_client, "complete", lambda *a, **kw: (_ for _ in ()).throw(LLMError("boom")))
        with pytest.raises(LLMError):
            schema_extractor.run("workshop_macys_bs.pdf", [BSTemplateRow(label="x")])
    ```

    **I001-ENDPOINT-STUB**
    ```python
    def test_extract_balance_sheet_endpoint(client):
        body = {
            "pdf_path": "workshop_macys_bs.pdf",
            "template": [
                {"label": "Cash & equivalents", "expected_unit": "USD millions"},
                {"label": "Total assets", "expected_unit": "USD millions"},
            ],
        }
        r = client.post("/api/extract/balance-sheet", json=body)
        assert r.status_code == 200
        data = r.json()
        assert "populated" in data
        assert len(data["populated"]) >= 1
        for row in data["populated"]:
            assert "source_page" in row
            assert "confidence" in row
            assert row["confidence"] in ("L", "M", "H")
    ```

    **I002-ENDPOINT-MISSING-FIXTURE**
    ```python
    def test_extract_balance_sheet_missing_fixture(client, tmp_path, monkeypatch):
        # Point fixtures dir at a dir with no schema_extractor.json
        import app.llm_client as lc
        monkeypatch.setattr(lc, "FIXTURES_DIR", tmp_path)
        body = {"pdf_path": "workshop_macys_bs.pdf", "template": [{"label": "x"}]}
        r = client.post("/api/extract/balance-sheet", json=body)
        assert r.status_code == 502
    ```

    3. Add necessary imports at the top:
       `pytest`, `BSTemplateRow`, `BSExtractedRow`, `BSExtractionResult` from `app.schemas`;
       `schema_extractor` from `app.agents`; `ValidationError` from `pydantic`.

    4. U004 and I001 implicitly confirm I003 (existing suite) is unaffected — also run the
       full suite at K003.

  - **Implements**: U001–U005, I001–I002, I003 (via K003)
  - **Files affected**:
    - **W006**: `backend/tests/test_schema_extractor.py` (create)
  - **Code quality**:
    - **Follows**: Y100-SINGLE-RESPONSIBILITY (each test asserts one observable behaviour)
    - **Avoids**: Z102-GOD-OBJECTS (no test does more than one logical check per function)
  - **Dependencies**: P001, P003, P004, P005
  - **Validation**: See K003.

---

## 4. File Change Summary (W###)

- [ ] **W001**: `backend/src/app/schemas.py`
  - **Action**: Modify (additive append)
  - **Purpose**: Add `BSTemplateRow`, `BSExtractedRow`, `BSExtractionResult` models
  - **Related specs**: M001, M002, M003, V001–V004
  - **Modified in steps**: P001

- [ ] **W002**: `backend/src/app/prompts/__init__.py`
  - **Action**: Modify (additive append)
  - **Purpose**: Add `SCHEMA_EXTRACTOR_INSTRUCTIONS` constant
  - **Related specs**: C002, F003, F004, E001–E003
  - **Modified in steps**: P002

- [ ] **W003**: `backend/src/app/fixtures/schema_extractor.json`
  - **Action**: Create
  - **Purpose**: Deterministic stub response for offline/test execution
  - **Related specs**: F007, T001, S006
  - **Modified in steps**: P003

- [ ] **W004**: `backend/src/app/agents/schema_extractor.py`
  - **Action**: Create
  - **Purpose**: Hero agent — PDF read → Claude prompt → Pydantic parse
  - **Related specs**: C001, A001, F001–F005
  - **Modified in steps**: P004

- [ ] **W005**: `backend/src/app/main.py`
  - **Action**: Modify (additive — one new class + one new route)
  - **Purpose**: Expose `POST /api/extract/balance-sheet`
  - **Related specs**: C003, A003, F006
  - **Modified in steps**: P005

- [ ] **W006**: `backend/tests/test_schema_extractor.py`
  - **Action**: Create
  - **Purpose**: Unit + integration tests for models, agent, and endpoint
  - **Related specs**: U001–U005, I001–I002
  - **Modified in steps**: P006

---

## 5. Integration Points (G###)

- **G001-LLM-CLIENT-SEAM**: `schema_extractor.run()` calls `llm_client.complete("schema_extractor", ...)`.
  In stub mode this returns the fixture; in live mode it calls Claude. Identical seam to all
  four existing hero agents.
  - **Connects**: `agents/schema_extractor.py` ↔ `llm_client.py` ↔ `fixtures/schema_extractor.json` (stub) / Anthropic API (live)
  - **Contract**: A001 (`run` function signature)
  - **Implemented in**: P003, P004

- **G002-FASTAPI-ENDPOINT**: The HTTP layer in `main.py` delegates entirely to `schema_extractor.run()`.
  Error routing reuses the existing `LLMError` handler — no new handler registered.
  - **Connects**: `main.py` ↔ `agents/schema_extractor.py`
  - **Contract**: A003 (endpoint contract)
  - **Implemented in**: P005

---

## 6. Testing Checkpoints (K###)

- [ ] **K001-MODELS-PARSE**
  - **After step**: P001
  - **Run**:
    ```bash
    cd backend
    python -c "
    from app.schemas import BSTemplateRow, BSExtractedRow, BSExtractionResult
    r = BSExtractedRow(label='x', value='1', source_page=1, confidence='H')
    print('models ok:', r)
    "
    ```
  - **Validates**: M001, M002, M003, V001–V004

- [ ] **K002-AGENT-STUB-SMOKE**
  - **After step**: P004 (P005 should also be complete to test endpoint path)
  - **Run**:
    ```bash
    cd backend
    pytest tests/test_schema_extractor.py::test_schema_extractor_stub_returns_valid_result \
           tests/test_schema_extractor.py::test_extract_balance_sheet_endpoint -v
    ```
  - **Validates**: F001–F007, S001–S004, U004, I001
  - **R002 note**: If `pypdf` extracts no text from the PDF in live mode, the agent will still
    work in stub mode (fixture path). Verify PDF text extraction separately:
    ```bash
    python -c "
    import pypdf, pathlib
    r = pypdf.PdfReader(str(pathlib.Path('..') / 'data' / 'workshop_macys_bs.pdf'))
    print(f'{len(r.pages)} pages, first page chars: {len(r.pages[0].extract_text())}')
    "
    ```

- [ ] **K003-FULL-SUITE**
  - **After step**: P006
  - **Run**:
    ```bash
    cd backend
    pytest -v
    ```
  - **Validates**: S005 (all 13 + new tests pass), N005 (no existing test broken), I003

---

## 7. Commit Points (X###)

- [ ] **X001-FOUNDATION**
  - **After step**: P003
  - **Includes files**: W001, W002, W003
  - **Message template**: `feat(ws-001): add BS extractor models, prompt, and stub fixture`

- [ ] **X002-AGENT-AND-ENDPOINT**
  - **After step**: P005
  - **Includes files**: W004, W005
  - **Message template**: `feat(ws-001): add schema_extractor agent and /api/extract/balance-sheet endpoint`

- [ ] **X003-TESTS**
  - **After step**: P006
  - **Includes files**: W006
  - **Message template**: `test(ws-001): add schema_extractor unit + integration tests`

---

## 8. Final Validation & Acceptance

**Functional:**
- F001–F007 verified via K002 and K003.

**Non-functional:**
- N001 (sync handler): `def extract_balance_sheet` — no `async` in W005.
- N002 (timeout): Inherited from `settings.llm_timeout_seconds = 120.0`; no override needed.
- N003 (no streaming): `llm_client.complete()` returns a string; no streaming path exists.
- N004 (single PDF): `pdf_path: str` scalar in `BSExtractReq`.
- N005 (backwards compat): K003 full suite passes.

**Edge cases:**
- E001 (no-match): Prompt instructs `"N/A"` + `"L"` — covered by at least one `"L"` row in T001.
- E004 (missing fixture): I002 test validates 502 response.
- E005 (malformed response): U005 test validates error propagation.

**Manual smoke test (optional, post-implementation):**
```bash
cd backend && uvicorn app.main:app --reload
curl -s -X POST http://localhost:8000/api/extract/balance-sheet \
  -H "Content-Type: application/json" \
  -d '{"pdf_path":"workshop_macys_bs.pdf","template":[{"label":"Total assets","expected_unit":"USD millions"},{"label":"Total equity","expected_unit":"USD millions"}]}' \
  | python -m json.tool
```
Assert: HTTP 200, `populated` has 2 rows, each with `source_page` ≥ 1 and `confidence` ∈ {L,M,H}.

**Acceptance criteria (S###):**
- S001 (Pydantic gate): `model_validate_json` in P004 → every response parsed.
- S002 (all rows populated): Q001 decision + prompt instruction.
- S003 (source + confidence on every row): V002–V003 + M002 definition.
- S004 (endpoint < 120 s): N002 timeout; manual test confirms.
- S005 (existing tests pass): K003.
- S006 (L rows flagged): T001 fixture contains at least one `"L"` row; I001 asserts confidence field present.

---

## 9. Rollback Plan

- **Safe stop points**: X001 is entirely additive to `schemas.py` + `prompts/__init__.py` and a new JSON file — zero runtime impact. X002 adds the agent file and one new route; the existing routes are untouched.
- **Revert procedure**:
  - After X001 only: `git revert X001` removes model/prompt/fixture additions; no DB migration needed.
  - After X002: `git revert X002` removes the new agent file and the new route from `main.py`.
  - After X003: `git revert X003` removes the test file.
  - No schema migrations were introduced — rollback requires no Alembic downgrade.

---

## Implementation Log (Populate During /implement)

## Execution Gaps vs Spec

*(empty)*

## Lessons Learned

*(empty)*

## Key Decisions and Deviations From Plan

*(empty)*

## Validation Results

*(empty)*
