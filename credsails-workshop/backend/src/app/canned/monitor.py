"""Canned post-commit monitor signal.

A watcher "polling since commit" surfaces an agency rating action (a downgrade from
the BB seeded at origination to B+). payload pins the new grade + as_of so the change
fires deterministically against deal.agency_grade.
"""
from __future__ import annotations


def downgrade_signal() -> dict:
    return {
        "signal_type": "agency_rating_action",
        "payload": {
            "agency_grade": "B+",
            "as_of": "2026-07-01",
            "source_url": "https://disclosure.spglobal.com/ratings/  (illustrative rating action)",
        },
    }
