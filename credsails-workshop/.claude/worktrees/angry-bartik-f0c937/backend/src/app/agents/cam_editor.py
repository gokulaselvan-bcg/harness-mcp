"""Hero agent: propose a diff to the committed CAM from a plain-English instruction."""
from __future__ import annotations

from .. import llm_client, prompts
from ..schemas import CAMEditResult


def run(cam_markdown: str, instruction: str) -> CAMEditResult:
    system = [{"type": "text", "text": prompts.CAM_EDITOR_INSTRUCTIONS}]
    messages = [
        {"role": "user", "content": f"CURRENT CAM:\n{cam_markdown}\n\nINSTRUCTION: {instruction}"}
    ]
    raw = llm_client.complete("cam_editor", "edit", system, messages, max_tokens=1500)
    return CAMEditResult.model_validate_json(raw)
