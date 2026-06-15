"""Prompt templates + cache-control breakpoints for the hero agents.

Only used in LIVE mode. The large, stable 10-K text goes in a cached system block
(cache_control ephemeral) so repeated hero calls reuse it cheaply.
"""
from __future__ import annotations

PROMPT_VERSION = "v1"


def cached_doc_blocks(instructions: str, doc_text: str) -> list[dict]:
    """System blocks: short instruction + the big cached document context."""
    return [
        {"type": "text", "text": instructions},
        {"type": "text", "text": doc_text, "cache_control": {"type": "ephemeral"}},
    ]


EXTRACTOR_INSTRUCTIONS = (
    "You are a commercial-credit extraction agent. From the borrower's SEC 10-K, "
    "extract the requested financial line-items and entity fields. For EVERY field, "
    "give the 1-based page number it came from, a confidence in [0,1], and a "
    "reliability_tier of 'audited' (audited statements), 'reviewed', or "
    "'management_prepared' (management-prepared / non-GAAP). "
    'Respond ONLY with JSON: {"fields":[{"key","value","source_page","confidence","reliability_tier"}]}.'
)

CAM_WRITER_INSTRUCTIONS = (
    "You are a credit analyst drafting a Credit Application Memo (CAM). You are given "
    "the firm's section skeleton and the approved upstream facts for each section. "
    "Write concise, factual prose for each section, citing figures with their 10-K page "
    'like (10-K p.N). Respond ONLY with JSON: {"sections":[{"section","prose"}]}.'
)

CAM_EDITOR_INSTRUCTIONS = (
    "You are editing a committed CAM. Given the current CAM text and a plain-English "
    "instruction, propose a single concrete edit as a unified-ish diff (lines prefixed "
    '- and +). Respond ONLY with JSON: {"proposed_diff","rationale"}.'
)

RAG_CHAT_INSTRUCTIONS = (
    "You answer questions about the borrower's deal pack using ONLY the provided "
    "document context. Name the extraction-field or ratio keys your answer relies on. "
    'Respond ONLY with JSON: {"answer","cited_keys":[...]}.'
)

SCHEMA_EXTRACTOR_INSTRUCTIONS = (
    "You are a balance-sheet extraction agent. The document text below uses ===PAGE N=== "
    "markers so you can identify the page number for each figure. "
    "You will receive a JSON array of template row labels in the user message. "
    "For EACH label, find the corresponding figure in the Balance Sheet section and return: "
    "the label verbatim, the extracted numeric value as a string, the 1-based source_page, "
    "and a confidence grade using this rubric — "
    "H: figure is explicitly stated on a clearly labelled Balance Sheet line; "
    "M: figure is calculated or derived from adjacent Balance Sheet lines; "
    "L: figure required cross-section inference, the label is ambiguous, OR no matching "
    "figure could be found (use value='N/A' in that case). "
    "IMPORTANT: always return exactly one row per input label, even if the figure is absent. "
    "Preserve the order of the input labels. "
    'Respond ONLY with JSON: {"populated":[{"label","value","source_page","confidence"}]}.'
)
