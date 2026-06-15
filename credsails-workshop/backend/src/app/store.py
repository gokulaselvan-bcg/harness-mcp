"""Persistence helpers: versioning, supersession, and latest-per-key reads.

The versioned tables (extraction_field, ratio, scorecard, cam) carry a partial
UNIQUE index over `(... ) WHERE superseded_by IS NULL`. That means we can't have
two "current" rows for the same logical key even momentarily — so `supersede`
vacates the old row's current-slot (self-reference) *before* inserting the new
current row, then repoints it. All within one transaction.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def get_deal(session: Session, deal_id: int | None = None) -> models.Deal | None:
    stmt = select(models.Deal)
    if deal_id is not None:
        stmt = stmt.where(models.Deal.id == deal_id)
    return session.execute(stmt.order_by(models.Deal.id.asc()).limit(1)).scalars().first()


def supersede(session: Session, old, new) -> None:
    """Replace `old` (a persisted versioned row) with `new` (unpersisted)."""
    old.superseded_by = old.id  # vacate the current-slot to satisfy the partial-unique index
    session.flush()
    session.add(new)
    session.flush()  # new gets an id; it is now the sole current row
    old.superseded_by = new.id
    if hasattr(old, "status"):
        old.status = "superseded"
    session.flush()


# ---- extraction_field -------------------------------------------------------

def current_fields(session: Session, deal_id: int) -> list[models.ExtractionField]:
    return list(
        session.execute(
            select(models.ExtractionField)
            .where(
                models.ExtractionField.deal_id == deal_id,
                models.ExtractionField.superseded_by.is_(None),
            )
            .order_by(models.ExtractionField.key.asc())
        )
        .scalars()
        .all()
    )


def field_map(session: Session, deal_id: int) -> dict[str, models.ExtractionField]:
    return {f.key: f for f in current_fields(session, deal_id)}


def new_field_version(session: Session, old: models.ExtractionField, value: str) -> models.ExtractionField:
    """Edit = a fresh version carrying human provenance; supersedes the old row."""
    new = models.ExtractionField(
        deal_id=old.deal_id,
        key=old.key,
        value=value,
        source_doc_id=old.source_doc_id,
        source_page=old.source_page,
        confidence=old.confidence,
        reliability_tier=old.reliability_tier,
        confidence_threshold=old.confidence_threshold,
        hitl_required=old.hitl_required,
        status="proposed",
        version=old.version + 1,
        produced_by="human:analyst",
    )
    supersede(session, old, new)
    return new


# ---- ratio ------------------------------------------------------------------

def current_ratios(session: Session, deal_id: int) -> list[models.Ratio]:
    return list(
        session.execute(
            select(models.Ratio)
            .where(models.Ratio.deal_id == deal_id, models.Ratio.superseded_by.is_(None))
            .order_by(models.Ratio.name.asc())
        )
        .scalars()
        .all()
    )


# ---- one-per-deal versioned rows (scorecard, cam) ---------------------------

def current_scorecard(session: Session, deal_id: int) -> models.Scorecard | None:
    return (
        session.execute(
            select(models.Scorecard).where(
                models.Scorecard.deal_id == deal_id,
                models.Scorecard.superseded_by.is_(None),
            )
        )
        .scalars()
        .first()
    )


def current_cam(session: Session, deal_id: int) -> models.CAM | None:
    return (
        session.execute(
            select(models.CAM).where(
                models.CAM.deal_id == deal_id, models.CAM.superseded_by.is_(None)
            )
        )
        .scalars()
        .first()
    )


def dd_findings(session: Session, deal_id: int) -> list[models.DDFinding]:
    return list(
        session.execute(
            select(models.DDFinding)
            .where(models.DDFinding.deal_id == deal_id)
            .order_by(models.DDFinding.id.asc())
        )
        .scalars()
        .all()
    )
