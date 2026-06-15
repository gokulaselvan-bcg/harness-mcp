# /plan - Create plan.md from spec.md

Convert a ticket spec into an executable implementation plan.

## Usage

```bash
/plan [PROJ-123|123|#123|$001|TICKET-DIR|SPEC-PATH]
```

## Forwarding

Invoke the `plan` skill and follow `.claude/skills/plan/SKILL.md`.

## Inputs

- Ticket identifier, ticket directory, or `spec.md` path

## Output

- `artifacts/tickets/{ID}/plan.md`
