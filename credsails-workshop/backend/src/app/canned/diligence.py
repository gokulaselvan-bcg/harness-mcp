"""Canned due-diligence findings (US reference layer).

Citations are `reference_data` kind -> the sentinel reference_data document, so a DD
chip never dangles against a fictive 10-K page.
"""
from __future__ import annotations

from .. import citations


def findings(sentinel_doc_id: int) -> list[dict]:
    cite = citations.reference_data(sentinel_doc_id)
    return [
        {
            "finding_type": "OFAC / PEP Screen",
            "result": "No OFAC or PEP matches across the entity, directors, and UBOs.",
            "citation": cite,
        },
        {
            "finding_type": "Adverse Media",
            "result": "One low-severity environmental compliance item (2023); resolved.",
            "citation": cite,
        },
        {
            "finding_type": "UCC-1 Liens",
            "result": "Senior ABL lien on inventory & receivables; no conflicting junior liens.",
            "citation": cite,
        },
    ]
