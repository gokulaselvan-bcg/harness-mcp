"""Hero agent: extract Balance Sheet line items from a PDF via a runtime row template."""
from __future__ import annotations

import json

import pypdf

from .. import llm_client, prompts
from ..config import settings
from ..schemas import BSExtractionResult, BSTemplateRow


def _pdf_text(pdf_path: str) -> str:
    path = settings.data_dir / pdf_path
    reader = pypdf.PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"===PAGE {i}===\n{text.strip()}")
    return "\n\n".join(pages)


def run(pdf_path: str, template: list[BSTemplateRow]) -> BSExtractionResult:
    pdf_text = _pdf_text(pdf_path)
    system = prompts.cached_doc_blocks(prompts.SCHEMA_EXTRACTOR_INSTRUCTIONS, pdf_text)
    labels = [row.label for row in template]
    messages = [{"role": "user", "content": f"Extract these Balance Sheet rows: {json.dumps(labels)}"}]
    raw = llm_client.complete("schema_extractor", "extract", system, messages, max_tokens=2048)
    return BSExtractionResult.model_validate_json(raw)
