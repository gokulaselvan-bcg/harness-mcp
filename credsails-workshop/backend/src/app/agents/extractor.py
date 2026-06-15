"""Hero agent: extract credit fields from the 10-K (REAL Claude in live mode)."""
from __future__ import annotations

from .. import llm_client, prompts
from ..schemas import ExtractionResult


def run(doc_text: str) -> ExtractionResult:
    system = prompts.cached_doc_blocks(prompts.EXTRACTOR_INSTRUCTIONS, doc_text)
    messages = [{"role": "user", "content": "Extract the standard credit fields from this 10-K."}]
    raw = llm_client.complete("extractor", "extract", system, messages, max_tokens=2048)
    return ExtractionResult.model_validate_json(raw)
