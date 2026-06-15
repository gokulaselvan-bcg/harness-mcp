"""Hero agent: answer deal-pack questions from retrieved context (REAL Claude in live)."""
from __future__ import annotations

from .. import llm_client, prompts
from ..schemas import ChatResult


def run(question: str, context_chunks) -> ChatResult:
    context = "\n\n".join(f"[10-K p.{c.page}] {c.text}" for c in context_chunks)
    system = [
        {"type": "text", "text": prompts.RAG_CHAT_INSTRUCTIONS},
        {"type": "text", "text": context or "(no context)", "cache_control": {"type": "ephemeral"}},
    ]
    messages = [{"role": "user", "content": question}]
    raw = llm_client.complete("rag_chat", "chat", system, messages, max_tokens=1024)
    return ChatResult.model_validate_json(raw)
