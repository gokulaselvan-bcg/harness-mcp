"""Pydantic models for hero-agent outputs.

ONE model per agent output, shared by both stub and live paths: stub fixtures and
live Claude responses are parsed through the *same* model before persistence, so
shapes can't drift and flipping to a real key needs no code change.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    key: str
    value: str
    source_page: int
    confidence: float = 1.0
    reliability_tier: str = "audited"  # audited | reviewed | management_prepared


class ExtractionResult(BaseModel):
    fields: list[ExtractedField]


class CAMSection(BaseModel):
    section: str
    prose: str


class CAMWriteResult(BaseModel):
    sections: list[CAMSection]


class CAMEditResult(BaseModel):
    proposed_diff: str
    rationale: str | None = None


class ChatResult(BaseModel):
    answer: str
    # Keys of the extraction fields / ratios the answer is about. The citation chip
    # shown is the *persisted* source_page of these (deterministic across modes),
    # not whatever retrieval surfaced.
    cited_keys: list[str] = Field(default_factory=list)


# ---- Balance Sheet extractor (WS-001) ---------------------------------------

class BSTemplateRow(BaseModel):
    label: str = Field(min_length=1)
    expected_unit: str = "USD millions"


class BSExtractedRow(BaseModel):
    label: str
    value: str
    source_page: int = Field(ge=1)
    confidence: Literal["L", "M", "H"]


class BSExtractionResult(BaseModel):
    populated: list[BSExtractedRow] = Field(min_length=1)
