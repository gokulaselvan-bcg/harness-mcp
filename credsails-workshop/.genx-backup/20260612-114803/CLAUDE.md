# CLAUDE.md — CredSails Demo · SDLC Discipline Contract

This file is auto-loaded by Claude Code. It is the contract for how code is written in this repo. **Read fully before any work.**

This repo is the **CredSails end-to-end demo** — a slimmed agentic credit-origination→underwriting workflow that proves the six agentic primitives (agent-does-work, HITL gate, per-field citation/version, orchestrator-compiles-to-template, RAG chatbot, monitor/re-trigger). Design spec: `docs/2026-06-09-credsails-demo-design.md`.

This contract governs **HOW** code is written. The MCP server below holds the standards, patterns, and known failures. The skills in `.claude/skills/` provide role personas and language-specific guidance, all of which delegate to MCP for current content. Both this file and MCP are authoritative. When in doubt, MCP wins on specifics; this file wins on procedure.

> **Build provenance note.** The initial scaffold (this commit) was built **standalone**, by explicit developer decision, while the `sdlc-discipline` MCP server was not connected to the session. The load-bearing decisions are catalogued in the spec's "Build notes & deviations" section and are **to be recorded into the harness** (`draft()` → developer `submit()`) once the server is reachable. From here on, the rules below bind.

---

## MCP server

This project has an MCP server holding SDLC standards, design decisions, failure patterns, and agent personas. Querying it is mandatory.

- Server name (as registered with Claude Code): `sdlc-discipline`
- Transport: stdio (no URL, no auth token — Claude Code spawns the process)
- Launch command: `python -m sdlc_mcp`
- Configured via `.mcp.json` at the project root (mirrors `harness-mcp/.mcp.json`; resolves `${HARNESS_MCP_HOME:-/Users/putatundarishav/cases/crisil/harness-mcp}`). If `/mcp` does not list `sdlc-discipline`, fix the configuration before doing any work — relaunch Claude Code rooted in this directory and approve the server.
- Server unavailable: work stops. No fallback. No guessing from memory. Tell the developer.

---

## Skills Layer

Skills in `.claude/skills/` auto-activate based on the work being done. They are thin pointers — actual content lives in MCP.

1. **Role skills** (`developer`, `tester`, `architect`, `reviewer`, `debugger`, `refactorer`, `migration-author`, `api-designer`).
2. **Language skills** (`python-standards`, `java-standards`, `typescript-standards`).
3. **Domain/concern skills** (`commercial-credit-domain`, `hitl-gate-design`, `provenance-and-confidence`, `compile-to-template-and-record`, `rag-over-document-pack`, `deal-portfolio-monitoring`, `parallel-vs-sequential-agent-orchestration`).

---

## Non-Negotiable Rules

### Before writing code
1. **Query MCP first** for any non-trivial task. Read returned `decision`/`pattern`/`context`/`failure` entries before proposing an approach.
2. **Plan before code.** Any change touching more than one file requires a written plan (files affected, approach, tests, MCP entries consulted). Wait for developer approval.
3. **Adopt the relevant role persona** via `query("<role> role persona", types=["agent"])`.
4. **Apply language standards** via `query("", tags=["python"])` etc.

### While writing code
5. **Tests first.** Failing tests before implementation. 100% coverage on business logic.
6. **No hardcoding.** All configuration in files.
7. **Type-safe data.** Pydantic in Python, Zod in TypeScript, equivalent on every boundary.
8. **Lint and format on every save.**
9. **One change per PR — procedural enforcement.**
   - **At plan time**, count separable units. If > 1, the plan must open verbatim with: *"I count N separable units: [list each one]. Per rule #9 these should be separate PRs. Confirm: bundle on one branch with incremental commits, or structure as stacked PRs?"* and wait.
   - **Mid-implementation**, any unplanned fix means STOP; the next message must begin with **`SCOPE TRIPWIRE:`** stating what surfaced, why now, and the bundle/split/separate-PR ask — touch nothing related until answered.
   - The exact strings *"I count N separable units"* and *"SCOPE TRIPWIRE:"* are machine-greppable; paraphrasing defeats the audit.

### Gates and review
10. **Stop at gates** (plan approval, tests passing, lint clean, MCP standards satisfied).
11. **No self-approval.** Review by another team member before merge.

### Capturing learnings
12. **Failure capture (SDLC-level only).** Business-logic bugs go in the PR description, not MCP. SDLC/infra failures: prompt the developer, `draft()`, developer `submit()`. Never autonomous.
13. **All other entry types are tech-lead initiated.**

---

## MCP Usage Cheat Sheet

```
query(search_string, types?, tags?, status_filter?)
get(id)   get_supersession_chain(id)   list_recent(days, types?)   find_related(search_terms, types?)
draft(type, content)   submit(draft_id, author)   supersede(old_id, new_content, reason, author)   deprecate(id, reason, author)
```

**Default task start sequence:** query task keywords → query role persona → query language tags → plan → confirm → code.

---

## Failure Modes Where This Contract Binds Hardest
- "Just this once" hardcoding → no.
- Skipping the failing-test-first step because the change is small → no.
- Proceeding when MCP is down → no.
- Self-approving a PR because the reviewer is slow → no.
- Capturing business-logic bugs in MCP → no, they go in the PR description.

---

## Standalone Prototype Subproject (explicit deviation from this contract)

The `prototype/` tree is a **self-contained HTML demo canvas**, not the credsails-demo backend. Tests-first, no-hardcoding, Pydantic/Zod and "MCP-down → stop" rules above **do not apply** here — verification is a browser walkthrough.

- **Entry point:** `prototype/credsails_underwriting_v1.html` — single file, inline CSS/JS, only external dep = Google Fonts Inter. No build step.
- **Demo borrower:** **Macy's, Inc. (NYSE: M)**, fiscal year ended Feb 1, 2025; internal rating **BB+ (Stable)**. Was Cleveland-Cliffs (CLF) until commit `930966f` — never reintroduce CLF strings, file names or steel sector content.
- **State model:** single global `STATE` object; pure-DOM `render*()` functions per workspace; `setTimeout` simulates agent work; no network calls.
- **Stages:** `login → home → sourcing | screening | underwriting`. Underwriting has 4 sequentially-unlocked workspaces A (Financial) → B (Industry) → C (Scorecard) → D (Memo); each renders via `renderFinancial`/`renderIndustry`/`renderScorecard`/`renderMemoWs`.
- **Cross-stage state:** `STATE.pipeline = []` is shared from Sourcing → Screening → Underwriting; per-candidate status `pending|running|cleared|review|declined`.
- **Screening flow:** Step 1 = pipeline list (`renderScreenItem`); Step 2 = per-candidate detail with 4 agent cards (`renderScreeningDetail` + `renderScreenCheckCard`). Per-card state `pass|warn|fail|running`; cards with `warn` host an inline HITL review panel (`renderHitlReview`) until a decision is recorded, then collapse into an audit chip (`renderHitlAudit`).
- **HITL decisions:** `STATE.screening.hitlDecisions[ticker] = { decision, note, reviewer, date }` with `decision ∈ {approved, escalated, declined}`; reviewer hardcoded "Priya Sharma · Credit Analyst". Decision folds into the effective card state for the summary banner (approved → pass / declined → fail) and into `p.status` (approved → cleared, declined → declined, escalated → review).
- **Screening curation:** `SCREENING_CHECKS[ticker]` has rich Macy's-only content (Portfolio fit · Adverse media w/ HITL alert · Sanctions · Financial overview); `getScreeningChecks` returns a generic 4-pass fallback for other tickers. The Macy's Adverse media card is the only `warn` state in the demo and the only place the HITL panel renders.
- **Re-opening screening detail:** `openScreening(ticker)` short-circuits the staggered card animation when `STATE.screening.cardStates[ticker]` already exists, so the list's "Review checks" button on cleared / review / declined candidates shows the recorded final state (and the HITL audit chip) without re-running the four agents.
- **Canned data constants:** `DATA` (BS/IS/CF + spread), `INDUSTRY` (4 cards), `SCORECARD` (strip / factors / anchor matrix / ladder / sensitivity), `MEMO` (CAM), `SOURCING` (8 retailers), `SCREENING_CHECKS` (per-ticker 4-card details). All figures must remain internally consistent.
- **Preview:** `.claude/launch.json` registers `credsails-underwriting` (python `http.server` on `:8765` from `prototype/`). Launch via `mcp__Claude_Preview__preview_start({name:"credsails-underwriting"})`; navigate to `/credsails_underwriting_v1.html`.
- **Docx generator:** `prototype/tools/generate_rating_brief.py` requires `python-docx` in `backend/.venv`. Regenerate with `backend/.venv/bin/python prototype/tools/generate_rating_brief.py` → `prototype/assets/Macys_Credit_Rating_Brief.docx` (path must match the HTML download link).
- **Worktree:** branch `claude/lucid-elbakyan-446818`; commit on this branch, never push, do not touch the parent `credsails-demo` backend or its `data/clf_10k.txt`.
- **Browser quirk:** after `preview_eval('location.reload()')`, JS STATE can persist; if a fresh state is needed, programmatically reset `STATE` and call `render()` before screenshotting.
