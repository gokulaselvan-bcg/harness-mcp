# /implement - Execute plan.md

Execute a ticket plan step-by-step with validation and progress tracking.

## Usage

```bash
/implement [PROJ-123|123|#123|$001|TICKET-DIR|PLAN-PATH]
```

## Forwarding

Invoke the `implement` skill and follow `.claude/skills/implement/SKILL.md`.

## Inputs

- Ticket identifier, ticket directory, or `plan.md` path

## Outputs

- Implemented code and tests
- Updated `artifacts/tickets/{ID}/plan.md`
