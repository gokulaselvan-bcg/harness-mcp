"""Submit-time validation and conflict detection."""
from __future__ import annotations

from typing import Any

from .models import BODY_MODELS, DraftIn


class ValidationError(ValueError):
    pass


def validate_for_submit(entry_type: str, draft: DraftIn) -> None:
    """Raise ValidationError if the draft is not fit to be promoted to accepted."""
    if not draft.title.strip():
        raise ValidationError("Title must not be empty.")
    if not draft.tags:
        raise ValidationError("At least one tag is required.")

    model = BODY_MODELS.get(entry_type)
    if model is None:
        raise ValidationError(f"Unknown entry type: {entry_type}")

    try:
        body = model(**draft.body)
    except Exception as e:
        raise ValidationError(f"Body invalid for type '{entry_type}': {e}") from e

    if entry_type == "decision":
        # Strict: rule, reasoning, alternatives_considered all required and non-empty.
        for field in ("rule", "reasoning", "alternatives_considered"):
            value = getattr(body, field, "")
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(
                    f"Decision entries require non-empty '{field}'."
                )


def _title_similarity(a: str, b: str) -> float:
    """Dice coefficient over content tokens, in [0, 1]. No external deps."""
    ta = {t for t in a.lower().split() if len(t) > 2}
    tb = {t for t in b.lower().split() if len(t) > 2}
    if not ta or not tb:
        return 0.0
    return (2 * len(ta & tb)) / (len(ta) + len(tb))


def find_conflicts(
    title: str,
    tags: list[str],
    existing: list[dict[str, Any]],
    *,
    title_threshold: float = 0.4,
) -> list[dict[str, Any]]:
    """Return existing accepted entries whose tags overlap and title is similar.

    `existing` is a list of row dicts with keys: id, title, tags (list[str]), status.
    """
    tag_set = {t.lower() for t in tags}
    hits: list[dict[str, Any]] = []
    for row in existing:
        if row.get("status") != "accepted":
            continue
        row_tags = {t.lower() for t in row.get("tags") or []}
        if not (tag_set & row_tags):
            continue
        if _title_similarity(title, row.get("title", "")) < title_threshold:
            continue
        hits.append({"id": row["id"], "title": row["title"], "tags": list(row_tags)})
    return hits
