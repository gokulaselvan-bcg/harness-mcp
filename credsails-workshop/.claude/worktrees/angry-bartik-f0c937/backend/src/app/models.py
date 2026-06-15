"""SQLAlchemy models for the CredSails demo.

Versioning convention (extraction_field, ratio, scorecard, cam):
- Rows are never mutated in place. An edit/recompute INSERTs a new version and
  sets the prior row's `superseded_by` to the new id.
- The *current* row is the one with `superseded_by IS NULL`, enforced by a
  partial UNIQUE index (defined here with `sqlite_where`, so create_all keeps the
  WHERE clause — Alembic autogenerate would drop it).

The audit_log is append-only + hash-chained (see audit.py); a BEFORE UPDATE/DELETE
trigger (added in the migration) makes mutation impossible at the DB level.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Deal(Base):
    __tablename__ = "deal"

    id: Mapped[int] = mapped_column(primary_key=True)
    borrower_name: Mapped[str] = mapped_column(String)
    naics_code: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="in_progress")  # in_progress|committed|re_review
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    # Public agency grade (single source of truth for the live view; snapshotted into cam.slots_json at compile).
    agency_grade: Mapped[str | None] = mapped_column(String, nullable=True)
    agency_grade_as_of: Mapped[str | None] = mapped_column(String, nullable=True)
    agency_grade_source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())


class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    doc_type: Mapped[str] = mapped_column(String)  # "10k" | "reference_data"
    path: Mapped[str | None] = mapped_column(String, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


class DocChunk(Base):
    __tablename__ = "doc_chunk"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"))
    page: Mapped[int] = mapped_column(Integer)
    char_start: Mapped[int] = mapped_column(Integer, default=0)
    char_end: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)

    __table_args__ = (Index("ix_doc_chunk_document", "document_id", "page"),)


class ExtractionField(Base):
    __tablename__ = "extraction_field"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    key: Mapped[str] = mapped_column(String)
    value: Mapped[str | None] = mapped_column(String, nullable=True)
    source_doc_id: Mapped[int | None] = mapped_column(ForeignKey("document.id"), nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    reliability_tier: Mapped[str] = mapped_column(String, default="audited")  # audited|reviewed|management_prepared
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.0)
    hitl_required: Mapped[bool] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed|approved|superseded
    version: Mapped[int] = mapped_column(Integer, default=1)
    superseded_by: Mapped[int | None] = mapped_column(ForeignKey("extraction_field.id"), nullable=True)
    # Provenance of the producing agent
    produced_by: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    llm_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())

    __table_args__ = (
        Index(
            "uq_extraction_field_current",
            "deal_id",
            "key",
            unique=True,
            sqlite_where=text("superseded_by IS NULL"),
        ),
    )


class Ratio(Base):
    __tablename__ = "ratio"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    name: Mapped[str] = mapped_column(String)
    value: Mapped[str] = mapped_column(String)
    source_field_ids_json: Mapped[list] = mapped_column(JSON, default=list)
    version: Mapped[int] = mapped_column(Integer, default=1)
    superseded_by: Mapped[int | None] = mapped_column(ForeignKey("ratio.id"), nullable=True)

    __table_args__ = (
        Index(
            "uq_ratio_current",
            "deal_id",
            "name",
            unique=True,
            sqlite_where=text("superseded_by IS NULL"),
        ),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)  # monotonic; chain order, scoped per deal
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    actor: Mapped[str] = mapped_column(String)
    actor_type: Mapped[str] = mapped_column(String)  # agent|human|system
    action: Mapped[str] = mapped_column(String)
    target_table: Mapped[str | None] = mapped_column(String, nullable=True)
    target_row_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())
    prev_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    row_hash: Mapped[str] = mapped_column(String)

    __table_args__ = (Index("ix_audit_log_deal_ts", "deal_id", "timestamp"),)


class Scorecard(Base):
    __tablename__ = "scorecard"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    ratios_json: Mapped[dict] = mapped_column(JSON, default=dict)
    pd: Mapped[float | None] = mapped_column(Float, nullable=True)
    lgd: Mapped[float | None] = mapped_column(Float, nullable=True)
    ead: Mapped[float | None] = mapped_column(Float, nullable=True)
    internal_grade: Mapped[str | None] = mapped_column(String, nullable=True)
    qualitative_dims_json: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed|approved|superseded
    version: Mapped[int] = mapped_column(Integer, default=1)
    superseded_by: Mapped[int | None] = mapped_column(ForeignKey("scorecard.id"), nullable=True)

    __table_args__ = (
        Index(
            "uq_scorecard_current",
            "deal_id",
            unique=True,
            sqlite_where=text("superseded_by IS NULL"),
        ),
    )


class DDFinding(Base):
    __tablename__ = "dd_finding"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    finding_type: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(Text)
    citation: Mapped[dict] = mapped_column(JSON, default=dict)  # citation shape (reference_data kind)


class CAM(Base):
    __tablename__ = "cam"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    content_markdown: Mapped[str] = mapped_column(Text, default="")
    slots_json: Mapped[list] = mapped_column(JSON, default=list)  # [{section, source_table, source_id, source_version, citation, prose}]
    status: Mapped[str] = mapped_column(String, default="draft")  # draft|committed|superseded
    superseded_by: Mapped[int | None] = mapped_column(ForeignKey("cam.id"), nullable=True)
    produced_by: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    llm_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())

    __table_args__ = (
        Index(
            "uq_cam_current",
            "deal_id",
            unique=True,
            sqlite_where=text("superseded_by IS NULL"),
        ),
    )


class CAMEdit(Base):
    __tablename__ = "cam_edit"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    cam_id: Mapped[int] = mapped_column(ForeignKey("cam.id"))
    instruction: Mapped[str] = mapped_column(Text)
    proposed_diff: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed|approved|rejected
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    produced_by: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    llm_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())


class MonitorEvent(Base):
    __tablename__ = "monitor_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    signal_type: Mapped[str] = mapped_column(String)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    fired_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())
    re_review_triggered: Mapped[bool] = mapped_column(Integer, default=0)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deal.id"))
    role: Mapped[str] = mapped_column(String)  # user|assistant
    content: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    produced_by: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
    llm_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, server_default=func.now())

    __table_args__ = (Index("ix_chat_message_deal_ts", "deal_id", "timestamp"),)
