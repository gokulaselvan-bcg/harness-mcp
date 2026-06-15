# WS-001 — Schema-driven Balance Sheet extractor agent

**Type:** Task
**Priority:** Workshop demo
**Status:** Open
**Assignee:** Workshop driver

## Goal

Build a new credsails agent that extracts Balance Sheet line items from a
borrower's financial-statement PDF, matching a runtime-provided row template,
and exposes it via a FastAPI endpoint the prototype UI can call. Runtime LLM
calls go through the `claude` CLI subprocess (no Anthropic API key required).

## Inputs

- Agent Requirement Document: `artifacts/tickets/WS-001/ard.md` (canonical
  source of behavior, inputs, outputs, constraints)
- Source PDF: `data/workshop_macys_bs.pdf` (pre-staged Macy's 10-K BS
  excerpt)
- Template fixture: `data/workshop_bs_template.json`

## Definition of done

- New file `backend/src/app/agents/schema_extractor.py` with a single
  `run(pdf_path, template) -> BSExtractionResult` function.
- New endpoint `POST /api/extract/balance-sheet` in `backend/src/app/main.py`.
- New Pydantic models in `backend/src/app/schemas.py`: `BSTemplateRow`,
  `BSExtractedRow`, `BSExtractionResult`.
- Tests:
  - Pydantic round-trip for all three new models.
  - Agent function with mocked subprocess returns a valid result.
  - Endpoint integration: feed staged PDF + template, assert structure.
- Existing tests still pass.
- `curl` against the running server returns a populated extraction for the
  staged Macy's PDF.

## Constraints

- No Anthropic API key.
- Sync handlers only (matches credsails convention).
- Pydantic validation gate on every LLM response.

## Out of scope

- Income Statement or Cash Flow extraction.
- PDF multipart upload.
- Prototype UI wire-up (handled separately at the end of the workshop if time
  permits).
