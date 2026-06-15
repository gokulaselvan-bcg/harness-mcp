"""Versioning/supersession + append-only, hash-chained audit log."""
from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app import audit, models, orchestrator as orch, store
from app.db import engine


def test_field_supersession_keeps_one_current(session):
    deal = orch.seed_deal(session)
    orch.run_extraction(session, deal)
    fmap = store.field_map(session, deal.id)
    orig = fmap["total_debt"]
    orch.edit_field(session, deal, orig.id, "4000")
    current = store.field_map(session, deal.id)
    assert current["total_debt"].value == "4000"
    assert current["total_debt"].version == orig.version + 1
    # exactly one current row for the key (partial unique index holds)
    rows = [f for f in store.current_fields(session, deal.id) if f.key == "total_debt"]
    assert len(rows) == 1


def test_partial_unique_blocks_two_current(session):
    deal = orch.seed_deal(session)
    session.add(models.ExtractionField(deal_id=deal.id, key="dup", value="1", version=1))
    session.add(models.ExtractionField(deal_id=deal.id, key="dup", value="2", version=2))
    with pytest.raises(IntegrityError):
        session.flush()  # two current rows for (deal, key) violate the partial unique index
    session.rollback()


def test_audit_log_is_append_only(session):
    deal = orch.seed_deal(session)
    row = audit.record(session, deal_id=deal.id, actor="x", actor_type="system", action="probe")
    session.commit()
    with pytest.raises(IntegrityError):
        with engine.begin() as c:
            c.execute(text("UPDATE audit_log SET action='hacked' WHERE id=:i"), {"i": row.id})
    with pytest.raises(IntegrityError):
        with engine.begin() as c:
            c.execute(text("DELETE FROM audit_log WHERE id=:i"), {"i": row.id})


def test_hash_chain_detects_forgery(session):
    deal = orch.seed_deal(session)
    audit.record(session, deal_id=deal.id, actor="a", actor_type="agent", action="extract")
    session.commit()
    assert audit.verify_chain(session, deal.id) is True
    # an INSERT is allowed by the trigger, but a forged row_hash breaks verification
    session.add(models.AuditLog(deal_id=deal.id, actor="evil", actor_type="system",
                                action="forge", prev_hash="zzz", row_hash="not-a-real-hash"))
    session.commit()
    assert audit.verify_chain(session, deal.id) is False
