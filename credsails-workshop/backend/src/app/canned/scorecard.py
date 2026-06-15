"""Deterministic scorecard (canned): PD/LGD/EAD + internal grade + cited qualitative dims.

Seeded to land one notch BELOW the public agency grade (BB) at BB-, so the
internal-vs-agency divergence is a teaching point (conservative, through-the-cycle
methodology) rather than an error. Qualitative dims carry citations so the citation
primitive (#3) shows up in the regulated core, not just extraction.
"""
from __future__ import annotations

from .. import citations, models


def compute(
    fields: dict[str, models.ExtractionField],
    ratios: list[dict],
    ten_k_doc_id: int,
    sentinel_doc_id: int,
) -> dict:
    ead = float(fields["total_debt"].value) if "total_debt" in fields else None
    ratios_map = {r["name"]: r["value"] for r in ratios}
    return {
        "ratios_json": ratios_map,
        "pd": 0.018,
        "lgd": 0.45,
        "ead": ead,
        "internal_grade": "BB-",
        "qualitative_dims_json": [
            {
                "dimension": "Industry Risk",
                "assessment": "Neutral — highly cyclical steel sector, automotive-demand sensitive",
                "citation": citations.doc_page(ten_k_doc_id, 4),
            },
            {
                "dimension": "Leverage & Coverage",
                "assessment": "Favorable — DSCR ~4.00x, net leverage ~3.11x",
                "citation": citations.doc_page(ten_k_doc_id, 3),
            },
            {
                "dimension": "Collateral & Liens",
                "assessment": "Neutral — senior ABL lien on inventory/receivables, no conflicts",
                "citation": citations.reference_data(sentinel_doc_id),
            },
        ],
    }
