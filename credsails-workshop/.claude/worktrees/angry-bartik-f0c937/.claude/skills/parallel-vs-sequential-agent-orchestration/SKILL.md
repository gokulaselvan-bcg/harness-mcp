---
name: parallel-vs-sequential-agent-orchestration
description: Use when deciding how to decompose a CovIQ/CredSails stage into parallel vs sequential agent chains with dependency-aware synthesis (e.g. parallel diligence/analysis workstreams that fan in to a memo). NOT for generic concurrency, job scheduling, or microservice decomposition — see `architect` for service architecture.
---

# Parallel vs sequential agent orchestration (CovIQ & CredSails)

The baseline primitive — **agents do the heavy lifting** (retrieve, extract, normalise, draft) — made concrete: decide which agents run **in parallel** (independent workstreams) vs **sequentially** (each depends on the last), then **synthesise**. Pair this with `hitl-gate-design` for the human-decision points.

## When to use / when not
- **Use** when laying out the agent graph for a CovIQ/CredSails stage.
- **Not** for generic threading/async, queue/worker design, or splitting microservices.

## How to decide
1. **Parallel** when workstreams are independent (no shared upstream output) — fan them out, then fan in.
2. **Sequential** when a step consumes the prior step's output — and re-check the dependency chain on every human edit.
3. **Synthesise** the parallel outputs into one reviewable package before the HITL gate.
4. **Per-item parallelism** — sometimes the same agent set runs once *per* sub-entity (per industry, per workstream).

## CovIQ example
In Preliminary Analysis, *the analytical workstreams that were sequential are now run in parallel by agents* — Peer Benchmarker, Market Researcher, Financial Analyst and LBO Model Builder run concurrently, then a Narrative/Red-Flag tracker synthesises before the VP review.

## CredSails example
Credit Due Diligence runs *five parallel DD workstreams* (sanctions, adverse media, legal, collateral, lien) that fan into a RAG chatbot + CDD summary; Industry Analysis will *run four assessment agents in parallel, once per industry*. Financial Modelling stays sequential, where *every edit triggers reconciliation re-check*.

## Pitfalls
- Forcing a sequential chain where workstreams are independent → needless latency.
- Parallelising steps with hidden dependencies → inconsistent synthesis.
- Skipping dependency re-checks after a human edit → stale downstream figures.

## Sources
- section_path: 2. How the two products compare
  quote: "AGENT does the heavy lifting"
- section_path: Step 2.2 — Preliminary Analysis
  quote: "the analytical workstreams that were sequential are now run **in parallel** by agents"
- section_path: Stage 4 — Credit Due Diligence (8 agents)
  quote: "five **parallel** DD workstreams"
- section_path: Stage 5 — Industry Analysis (6 agents)
  quote: "run four assessment agents **in parallel, once per industry**"
- section_path: Stage 3 — Financial Modelling (6 agents)
  quote: "every edit triggers reconciliation re-check"
