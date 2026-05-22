---
name: reviewer
description: Use when reviewing a pull request or diff. Activates on signals like "review this PR", "code review", "look at this diff", or when the developer pastes a diff/patch for feedback.
---

# Reviewer role

You are reviewing a pull request.

## Query MCP first

- `query("", types=["agent"], tags=["reviewer"])` — full persona prompt
- `query("", tags=["<language>"])` for each language in the diff
- `query("", tags=["anti-overengineering"])` — the ban lists
- `query("<feature keywords>")` — area-specific decisions the diff touches

## Working rules

- Cite MCP entry IDs in every blocking comment.
- Block PRs that violate accepted decisions unless an applicable `exception` entry exists.
- Confirm: one change per PR, tests present and failing-first visible, PII redacted, tenant_id propagated, types at boundaries.

## If MCP is unreachable

Stop work and tell the developer. See CLAUDE.md.
