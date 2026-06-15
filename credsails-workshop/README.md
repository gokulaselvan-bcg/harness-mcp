# CredSails — end-to-end demo

A single runnable web app that walks one US borrower (Cleveland-Cliffs Inc.) from
document intake to a committed Credit Application Memo, making the **six agentic
primitives** visible: agent-does-the-work · HITL approval gate · per-field
citation/version stamp · orchestrator-compiles-to-template · RAG chatbot · continuous
monitor/re-trigger.

~4 "hero" steps make **real Claude calls**; the rest (financial modeling, scorecard,
due diligence) is canned/deterministic. With the placeholder API key the whole demo
runs **offline in stub mode**; drop in a real key to flip the hero agents to live
Claude — no code change.

Full design: [`docs/2026-06-09-credsails-demo-design.md`](docs/2026-06-09-credsails-demo-design.md).

## Run it

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate    # Python >= 3.10
pip install -e ".[dev]"
cp .env.example .env            # ships a dummy key -> stub mode
alembic upgrade head            # creates credsails.db
uvicorn app.main:app --reload   # http://127.0.0.1:8000
```

Open the URL, click **Seed / Reset deal**, then walk the 8 steps top-to-bottom.

### Go live (optional)
Put a real key in `backend/.env` (`ANTHROPIC_API_KEY=sk-ant-...`, optionally
`ANTHROPIC_MODEL=<current Sonnet>`) and restart. The header badge flips to **LLM: live**
and the four hero agents (extraction, CAM prose, CAM-edit diff, RAG chat) call Claude.
The chat citation lands on the same persisted page as in stub mode.

## Test

```bash
cd backend && pytest        # 13 tests, stub mode, deterministic
```

## Layout
- `backend/src/app/` — FastAPI app: `models`/`db`/`store`/`audit` (persistence + append-only hash-chained audit), `llm_client` (live/stub switch), `agents/` (hero Claude calls), `canned/` (deterministic spread/score/DD/monitor), `orchestrator` (8-step spine), `main` (REST + SPA), `static/` (vanilla-JS stepper UI).
- `data/clf_10k.txt` — representative public-10-K excerpt (extraction source).
- `.mcp.json` + `CLAUDE.md` + `.claude/skills/` — harness-consumer contract (see CLAUDE.md).
