"""Live/stub switch + shape parity."""
from __future__ import annotations

from app import llm_client
from app.config import settings
from app.schemas import ExtractionResult


def test_stub_mode_active_with_placeholder_key():
    assert settings.placeholder_key is True
    assert settings.llm_mode == "stub"


def test_stub_fixture_parses_into_shared_schema():
    raw = llm_client.complete("extractor", "extract", system=[], messages=[])
    result = ExtractionResult.model_validate_json(raw)  # same model the live path uses
    assert len(result.fields) == 14
    mgmt = [f for f in result.fields if f.reliability_tier == "management_prepared"]
    assert mgmt and mgmt[0].key == "adjusted_ebitda"


def test_provenance_reports_mode():
    prov = llm_client.provenance("extractor")
    assert prov["produced_by"] == "agent:extractor"
    assert prov["llm_mode"] == "stub"
