# /blueprint-to-tickets - Decompose Blueprint to Tickets

Decompose a blueprint into epics and implementation tickets.

## Usage

```bash
/blueprint-to-tickets [optional blueprint path]
```

## Forwarding

Invoke the `blueprint-to-tickets` skill and follow
`.claude/skills/blueprint-to-tickets/SKILL.md`.

## Inputs

- Blueprint file under `artifacts/blueprints/`

## Outputs

- `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets.md`
- `artifacts/blueprints/{id}--{name}/tickets/{id}-tickets/EPIC-*.md`
