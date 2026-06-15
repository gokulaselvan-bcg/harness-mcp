"""Tests for WS-001: schema_extractor agent, models, and endpoint."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.agents import schema_extractor
from app.schemas import BSExtractedRow, BSExtractionResult, BSTemplateRow


# ---- U001: BSTemplateRow ----------------------------------------------------

def test_bs_template_row_valid():
    row = BSTemplateRow(label="Total assets", expected_unit="USD millions")
    assert row.label == "Total assets"
    assert row.expected_unit == "USD millions"


def test_bs_template_row_default_unit():
    row = BSTemplateRow(label="Total equity")
    assert row.expected_unit == "USD millions"


def test_bs_template_row_rejects_empty_label():
    with pytest.raises(ValidationError):
        BSTemplateRow(label="")


# ---- U002: BSExtractedRow ---------------------------------------------------

def test_bs_extracted_row_valid():
    row = BSExtractedRow(label="Total assets", value="9134", source_page=3, confidence="H")
    assert row.confidence == "H"
    assert row.source_page == 3


def test_bs_extracted_row_rejects_bad_confidence():
    with pytest.raises(ValidationError):
        BSExtractedRow(label="x", value="1", source_page=1, confidence="X")


def test_bs_extracted_row_rejects_zero_source_page():
    with pytest.raises(ValidationError):
        BSExtractedRow(label="x", value="1", source_page=0, confidence="H")


def test_bs_extracted_row_rejects_negative_source_page():
    with pytest.raises(ValidationError):
        BSExtractedRow(label="x", value="1", source_page=-1, confidence="M")


# ---- U003: BSExtractionResult -----------------------------------------------

def test_bs_extraction_result_json_round_trip():
    raw = '{"populated": [{"label": "Total assets", "value": "9134", "source_page": 3, "confidence": "H"}]}'
    result = BSExtractionResult.model_validate_json(raw)
    assert result.populated[0].confidence == "H"
    assert result.populated[0].source_page == 3


def test_bs_extraction_result_rejects_empty_populated():
    with pytest.raises(ValidationError):
        BSExtractionResult.model_validate_json('{"populated": []}')


# ---- U004: agent stub -------------------------------------------------------

def test_schema_extractor_stub_returns_valid_result():
    template = [
        BSTemplateRow(label="Cash & equivalents"),
        BSTemplateRow(label="Total assets"),
    ]
    result = schema_extractor.run("workshop_macys_bs.pdf", template)
    assert isinstance(result, BSExtractionResult)
    assert len(result.populated) >= 1
    for row in result.populated:
        assert row.source_page >= 1
        assert row.confidence in {"L", "M", "H"}


def test_schema_extractor_stub_has_hitl_row():
    template = [BSTemplateRow(label="Total equity")]
    result = schema_extractor.run("workshop_macys_bs.pdf", template)
    low = [r for r in result.populated if r.confidence == "L"]
    assert len(low) >= 1, "fixture must contain at least one L-confidence row (S006)"


# ---- U005: LLMError propagation ---------------------------------------------

def test_schema_extractor_propagates_llm_error(monkeypatch):
    from app import llm_client
    from app.llm_client import LLMError

    def _raise(*args, **kwargs):
        raise LLMError("boom")

    monkeypatch.setattr(llm_client, "complete", _raise)
    with pytest.raises(LLMError):
        schema_extractor.run("workshop_macys_bs.pdf", [BSTemplateRow(label="x")])


# ---- I001: endpoint stub ----------------------------------------------------

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


# ---- I002: missing fixture → 502 --------------------------------------------

def test_extract_balance_sheet_missing_fixture(client, tmp_path, monkeypatch):
    import app.llm_client as lc

    monkeypatch.setattr(lc, "FIXTURES_DIR", tmp_path)
    body = {
        "pdf_path": "workshop_macys_bs.pdf",
        "template": [{"label": "x", "expected_unit": "USD millions"}],
    }
    r = client.post("/api/extract/balance-sheet", json=body)
    assert r.status_code == 502
