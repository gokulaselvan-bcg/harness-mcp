"""The uniform citation shape (an embedded value, not a table).

kind:
- "doc_page"       -> a real (document_id, page) in the 10-K
- "reference_data" -> canned DD (OFAC/UCC/bureau) -> the sentinel reference_data document, page=None
- "external_url"   -> the public agency-grade source (URL + as_of)
The UI renders the chip by `kind`.
"""
from __future__ import annotations


def doc_page(document_id: int, page: int) -> dict:
    return {"kind": "doc_page", "document_id": document_id, "page": page, "source_url": None, "as_of": None}


def reference_data(document_id: int) -> dict:
    return {"kind": "reference_data", "document_id": document_id, "page": None, "source_url": None, "as_of": None}


def external_url(source_url: str, as_of: str | None = None) -> dict:
    return {"kind": "external_url", "document_id": None, "page": None, "source_url": source_url, "as_of": as_of}
