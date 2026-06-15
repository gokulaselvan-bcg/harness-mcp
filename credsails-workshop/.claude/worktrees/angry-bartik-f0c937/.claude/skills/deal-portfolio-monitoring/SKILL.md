---
name: deal-portfolio-monitoring
description: Use when designing always-on monitors that re-trigger CovIQ/CredSails workflows on emerging-opportunity or early-warning signals (sponsor exits, founder departures, debt maturities, EWIs). NOT for generic ops/observability, uptime alerting, or cron jobs — see `architect` for infrastructure concerns.
---

# Deal & portfolio monitoring (CovIQ & CredSails)

One of the six reusable primitives: **continuous monitoring / re-trigger.** Agents watch for signals after a workflow has "finished" and re-activate it when something changes — emerging opportunity on the buy side, early warning on the credit side.

## When to use / when not
- **Use** when designing a monitor that re-triggers a CovIQ/CredSails workflow on a domain signal.
- **Not** for system observability, uptime/SLA alerting, or scheduled engineering jobs.

## How to design it
1. **Define the signals** — domain events, not metrics (sponsor exit, founder departure, debt maturity, UCC-1 lapse, rating action).
2. **Register the subject** — passed targets / on-watch borrowers are registered with the monitor, not dropped.
3. **Re-trigger the workflow** — a signal re-opens the relevant stage with context, routed to a human.
4. **Bucket by confidence/horizon** — so a human triages high-signal events first.

## CovIQ example
The *Emerging Opportunity Detector monitors passed targets* and re-triggers on signals like sponsor exit or founder departure; a *Sponsor Activity Monitor (continuous)* watches for new fund closes, team changes, and portfolio companies crossing their exit window.

## CredSails example
The Stage 1 Opportunity Finder will *scan public signals (debt maturity from 10-K*, RCF expiry, capex guidance, rating actions) plus private signals, and the prioritiser overlays *EWI + heatmap + stress overlay* — the early-warning analogue of CovIQ's emerging-opportunity detection.

## Pitfalls
- Monitoring metrics instead of domain signals → noise, not deals.
- Re-triggering straight into action without a HITL gate → violates the no-decision-without-sign-off rule.
- Dropping passed/declined subjects instead of registering them → the re-trigger never fires.

## Sources
- section_path: 2. How the two products compare
  quote: "Continuous monitoring / re-trigger"
- section_path: Step 1.1 — Market Mapping & Universe Building
  quote: "Emerging Opportunity Detector monitors passed targets"
- section_path: Step 1.4 — Sponsor Intelligence & Engagement
  quote: "Sponsor Activity Monitor (continuous)"
- section_path: Stage 1 — Lead Origination (7 agents)
  quote: "scan public signals (debt maturity from 10-K"
- section_path: Stage 1 — Lead Origination (7 agents)
  quote: "EWI + heatmap + stress overlay"
