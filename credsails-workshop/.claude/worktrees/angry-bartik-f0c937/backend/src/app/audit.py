"""Append-only, hash-chained audit log.

Every state-changing operation calls `record(...)`. The chain is scoped per deal
and ordered by the monotonic autoincrement id. `row_hash` is computed pre-INSERT
over a canonical serialization that *includes* `prev_hash`, so any later tampering
(which the DB trigger already forbids) is also detectable by `verify_chain`.
"""
from __future__ import annotations

import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

# Fields that participate in the hash (NOT id/timestamp/row_hash itself).
_HASHED_FIELDS = (
    "deal_id",
    "actor",
    "actor_type",
    "action",
    "target_table",
    "target_row_id",
    "target_version",
    "old_value",
    "new_value",
    "rationale",
    "prev_hash",
)


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(payload: dict) -> str:
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _last_hash(session: Session, deal_id: int) -> str | None:
    row = (
        session.execute(
            select(models.AuditLog)
            .where(models.AuditLog.deal_id == deal_id)
            .order_by(models.AuditLog.id.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    return row.row_hash if row else None


def record(
    session: Session,
    *,
    deal_id: int,
    actor: str,
    actor_type: str,
    action: str,
    target_table: str | None = None,
    target_row_id: int | None = None,
    target_version: int | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    rationale: str | None = None,
) -> models.AuditLog:
    prev = _last_hash(session, deal_id)
    payload = {
        "deal_id": deal_id,
        "actor": actor,
        "actor_type": actor_type,
        "action": action,
        "target_table": target_table,
        "target_row_id": target_row_id,
        "target_version": target_version,
        "old_value": old_value,
        "new_value": new_value,
        "rationale": rationale,
        "prev_hash": prev,
    }
    entry = models.AuditLog(row_hash=_hash(payload), **payload)
    session.add(entry)
    session.flush()  # assign id
    return entry


def verify_chain(session: Session, deal_id: int) -> bool:
    rows = (
        session.execute(
            select(models.AuditLog)
            .where(models.AuditLog.deal_id == deal_id)
            .order_by(models.AuditLog.id.asc())
        )
        .scalars()
        .all()
    )
    prev: str | None = None
    for r in rows:
        payload = {f: getattr(r, f) for f in _HASHED_FIELDS}
        if r.prev_hash != prev or r.row_hash != _hash(payload):
            return False
        prev = r.row_hash
    return True
