# /pull-ticket - Pull Jira ticket into local context

Pull a specific Jira ticket and prepare implementation context.

## Usage

```bash
/pull-ticket PROJ-123
/pull-ticket 123
```

## Forwarding

Invoke the `pull-ticket` skill and follow `.claude/skills/pull-ticket/SKILL.md`.

## Inputs

- Ticket key (`PROJ-123`) or shorthand ID (`123`)

## Outputs

- `artifacts/tickets/{TICKET-ID}/ticket.md`
- Ticket branch from default base branch
