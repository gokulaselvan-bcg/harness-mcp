"""Hero agent: write CAM section prose from the deterministically-stamped slots."""
from __future__ import annotations

import json

from .. import llm_client, prompts
from ..schemas import CAMWriteResult


def run(doc_text: str, skeleton: list[dict]) -> CAMWriteResult:
    facts = json.dumps(skeleton, indent=2, default=str)
    system = prompts.cached_doc_blocks(prompts.CAM_WRITER_INSTRUCTIONS, doc_text)
    messages = [
        {"role": "user", "content": "Write prose for each CAM section using these facts:\n" + facts}
    ]
    raw = llm_client.complete("cam_writer", "compile", system, messages, max_tokens=3000)
    return CAMWriteResult.model_validate_json(raw)
