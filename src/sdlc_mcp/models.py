"""Pydantic models for SDLC entries and their type-specific bodies."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Union

from pydantic import BaseModel, Field, field_validator

EntryType = Literal["decision", "failure", "pattern", "context", "exception", "agent"]
Status = Literal["proposed", "accepted", "superseded", "deprecated"]

ID_PREFIX: dict[str, str] = {
    "decision": "DEC",
    "failure": "FAIL",
    "pattern": "PAT",
    "context": "CTX",
    "exception": "EXC",
    "agent": "AGT",
}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- Type-specific bodies ---------------------------------------------------

class DecisionBody(BaseModel):
    rule: str
    reasoning: str
    alternatives_considered: str


class FailureBody(BaseModel):
    symptom: str
    root_cause: str
    detection: str
    prevention: str


class PatternBody(BaseModel):
    use_case: str
    structure: str
    when_to_apply: str
    when_not_to_apply: str


class ContextBody(BaseModel):
    area: str
    content: str


class ExceptionBody(BaseModel):
    overrides_id: str
    scope: str
    reason: str


class AgentBody(BaseModel):
    role: str
    prompt: str
    applies_to: str


BODY_MODELS: dict[str, type[BaseModel]] = {
    "decision": DecisionBody,
    "failure": FailureBody,
    "pattern": PatternBody,
    "context": ContextBody,
    "exception": ExceptionBody,
    "agent": AgentBody,
}

AnyBody = Union[DecisionBody, FailureBody, PatternBody, ContextBody, ExceptionBody, AgentBody]


def parse_body(entry_type: str, raw: dict[str, Any]) -> BaseModel:
    model = BODY_MODELS.get(entry_type)
    if model is None:
        raise ValueError(f"Unknown entry type: {entry_type}")
    return model(**raw)


# --- Shared envelope --------------------------------------------------------

class Entry(BaseModel):
    """Canonical entry as returned to callers."""
    id: str
    type: EntryType
    title: str
    tags: list[str]
    author: str
    created_at: str
    status: Status
    supersedes: str | None = None
    superseded_by: str | None = None
    last_referenced_at: str | None = None
    reference_count: int = 0
    evidence_links: list[str] = Field(default_factory=list)
    body: dict[str, Any]


class DraftIn(BaseModel):
    """Payload shape accepted by the draft() tool. `type` plus a content dict."""
    title: str
    tags: list[str]
    body: dict[str, Any]
    evidence_links: list[str] = Field(default_factory=list)
    supersedes: str | None = None

    @field_validator("tags")
    @classmethod
    def _at_least_one_tag(cls, v: list[str]) -> list[str]:
        v = [t.strip() for t in v if t and t.strip()]
        if not v:
            raise ValueError("At least one tag is required.")
        return v
