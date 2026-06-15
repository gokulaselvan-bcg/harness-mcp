"""The live/stub LLM switch — the single seam between the demo and Claude.

- STUB (placeholder/missing key): return a deterministic fixture keyed by agent.
  The whole demo runs offline and repeatably.
- LIVE (real key): a SYNC Anthropic client, non-streaming, with prompt caching.
  Sync on purpose: FastAPI runs sync handlers in a threadpool, so a multi-second
  call never blocks the loop and we reuse the reference's sync Session pattern.

Both paths return a JSON string parsed by the SAME Pydantic model in schemas.py.
"""
from __future__ import annotations

from pathlib import Path

from . import prompts
from .config import settings

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class LLMError(Exception):
    """Raised on a live-call failure so handlers can return a structured error."""


def complete(agent: str, step: str, system, messages, max_tokens: int = 2048) -> str:
    """Return the model's text output (a JSON string) for `agent`."""
    if settings.placeholder_key:
        return _stub(agent, step)
    return _live(system, messages, max_tokens)


def _stub(agent: str, step: str) -> str:
    path = FIXTURES_DIR / f"{agent}.json"
    if not path.exists():
        raise LLMError(f"missing stub fixture for agent={agent!r} step={step!r}: {path}")
    return path.read_text(encoding="utf-8")


def _live(system, messages, max_tokens: int) -> str:
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=settings.anthropic_api_key, timeout=settings.llm_timeout_seconds)
        resp = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    except LLMError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface as structured error, never a raw 500
        raise LLMError(f"live Claude call failed: {exc}") from exc


def provenance(agent: str) -> dict:
    """Provenance stamp for rows a hero agent produces."""
    return {
        "produced_by": f"agent:{agent}",
        "model": settings.anthropic_model,
        "prompt_version": prompts.PROMPT_VERSION,
        "llm_mode": settings.llm_mode,
    }
