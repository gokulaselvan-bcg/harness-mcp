---
name: hitl-gate-design
description: Use when designing human-in-the-loop approval gates for CovIQ deal workflows or CredSails credit underwriting — deciding who approves what (CovIQ VP/MD/Associate; CredSails named regulatory roles + DLA-matrix routing), what is captured, and how. NOT for generic CI/CD gates, PR-review process, or service authz — that is SDLC; see the `reviewer` and `architect` skills instead.
---

# HITL gate design (CovIQ & CredSails)

One of the six reusable primitives shared by both products: **agents draft and analyse; humans decide.** A HITL gate is not "a human glances at it" — it is a *judgment point* with a **named approver**, a captured **rationale**, and a **version stamp**.

## When to use / when not
- **Use** when placing or reviewing an approval gate in a CovIQ or CredSails agent workflow.
- **Not** for engineering gates (CI checks, PR review, deploy approvals) — those are SDLC concerns.

## How to design a gate
1. **Locate the judgment point** — anywhere a decision is irreversible or externally visible (send, pass/proceed, override, waiver, sign-off).
2. **Name the approver** — encode *who* approves, not merely *that* a human approves. The role is part of the gate.
3. **Capture rationale + version** — every approve/reject/modify records a reason and a version stamp (feeds the audit trail and provenance primitive).
4. **Default to deny** for anything outward-facing: no send / no decision without explicit sign-off.

## CovIQ example
CovIQ's HITL philosophy is absolute: *no outreach is ever sent, and no pass/proceed decision is ever made, without explicit human sign-off.* Concretely, outreach gates read **"NONE sent without sign-off"** — the VP approves each email before send; the Associate approves briefs. Gates map to fund roles (Associate executes, VP makes pass/proceed, MD signs high-priority).

## CredSails example
Here gates map to **named regulatory roles** — the HITL gates map to **named regulatory roles**, not a generic reviewer. The Compliance Officer owns *sanctions/PEP, document-validation failures, Sanctions Clearance Certificate*; the **Senior Credit Officer reviews each flagged override**; and the memo stage will *set DLA approval routing* (Delegated Lending Authority — who can approve what size/risk). Escalation paths are explicit.

## Pitfalls
- A gate with no named owner is decoration — it won't hold up in a regulator-facing review.
- Auto-approving "low-risk" outward actions breaks the no-send-without-sign-off invariant.
- Forgetting rationale capture severs the gate from the audit trail (`provenance-and-confidence`).

## Sources
- section_path: 2. How the two products compare
  quote: "HITL gates at every judgment point"
- section_path: 3.1 Intended users & audience
  quote: "no outreach is ever sent, and no pass/proceed decision is ever made, without explicit human sign-off"
- section_path: Step 1.6 — Target Outreach & Management Meetings
  quote: "NONE sent without sign-off"
- section_path: 5. What I'd flag for your onboarding
  quote: "the HITL gates map to **named regulatory roles**"
- section_path: 4.1 Intended users & audience
  quote: "sanctions/PEP, document-validation failures, Sanctions Clearance Certificate"
- section_path: Stage 6 — Credit Rating Scorecard (6 agents)
  quote: "Senior Credit Officer reviews each flagged override"
- section_path: Stage 7 — Underwriting Memo / CAM (5 agents)
  quote: "set DLA approval routing"
