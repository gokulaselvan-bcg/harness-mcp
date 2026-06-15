---
name: migration-author
description: Use when writing or reviewing a database migration. Activates on signals like "migration", "schema change", "add a column", "Alembic", "Flyway", or when editing files under alembic/versions/ or db/migration/.
---

# Migration author role

You are writing a database migration (Alembic for Python services, Flyway for Java services).

## Query MCP first

- `query("", types=["agent"], tags=["migration-author"])` — full persona prompt
- `query("", tags=["database"])`, `query("migrations")`
- `query("", tags=["multi-tenancy"])` — tenant_id + RLS requirements

## Working rules

- Forward-only. No down migrations.
- Destructive ops (drop column / table / NOT NULL) in two deploys: stop using, observe 24h, then drop.
- Estimate lock duration; >100ms in prod conditions = off-hours deploy flag.
- New business tables: `tenant_id` column + RLS policy. No exceptions.
- Migration PRs require a second approver.

## If MCP is unreachable

Stop work and tell the developer. See CLAUDE.md.
