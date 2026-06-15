"""Deterministic financial spread + ratios (canned).

Each ratio links back to the *current approved* extraction_field ids it derives from,
so the RAG answer "where did the leverage figure come from?" is data-backed.
"""
from __future__ import annotations

from .. import models


def _num(fields: dict[str, models.ExtractionField], key: str) -> float:
    return float(fields[key].value)


def compute(fields: dict[str, models.ExtractionField]) -> list[dict]:
    out: list[dict] = []
    if {"total_debt", "cash_and_equivalents", "adjusted_ebitda"} <= fields.keys():
        lev = (_num(fields, "total_debt") - _num(fields, "cash_and_equivalents")) / _num(fields, "adjusted_ebitda")
        out.append(
            {
                "name": "leverage_net_debt_ebitda",
                "value": f"{lev:.2f}x",
                "source_field_ids": [
                    fields["total_debt"].id,
                    fields["cash_and_equivalents"].id,
                    fields["adjusted_ebitda"].id,
                ],
            }
        )
    if {"adjusted_ebitda", "interest_expense"} <= fields.keys():
        dscr = _num(fields, "adjusted_ebitda") / _num(fields, "interest_expense")
        out.append(
            {
                "name": "dscr",
                "value": f"{dscr:.2f}x",
                "source_field_ids": [fields["adjusted_ebitda"].id, fields["interest_expense"].id],
            }
        )
    if {"current_assets", "current_liabilities"} <= fields.keys():
        cr = _num(fields, "current_assets") / _num(fields, "current_liabilities")
        out.append(
            {
                "name": "current_ratio",
                "value": f"{cr:.2f}x",
                "source_field_ids": [fields["current_assets"].id, fields["current_liabilities"].id],
            }
        )
    return out
