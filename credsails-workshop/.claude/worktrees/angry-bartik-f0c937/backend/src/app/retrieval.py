"""Keyword retrieval over doc_chunk — identical in stub and live mode.

No embeddings (Anthropic has no embeddings API; an external embedder would add a
dependency and cross-mode nondeterminism for no teaching value). Retrieval supplies
the answer *context*; the citation chip shown to the user is the deterministic
persisted source_page of the field/ratio in question (resolved by the caller).
"""
from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def search(session: Session, deal_id: int, query: str, limit: int = 3) -> list[models.DocChunk]:
    chunks = (
        session.execute(
            select(models.DocChunk)
            .join(models.Document, models.DocChunk.document_id == models.Document.id)
            .where(models.Document.deal_id == deal_id)
        )
        .scalars()
        .all()
    )
    q = set(_tokens(query))
    scored: list[tuple[int, models.DocChunk]] = []
    for c in chunks:
        ct = _tokens(c.text)
        score = sum(ct.count(t) for t in q)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1].page))
    return [c for _, c in scored[:limit]]
