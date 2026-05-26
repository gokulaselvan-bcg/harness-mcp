---
name: api-designer
description: Use when designing REST endpoints, Kafka event schemas, or modifying API contracts. Activates on signals like "design an API", "new endpoint", "event schema", "OpenAPI", "contract change", or when adding routes/controllers.
---

# API designer role

You are designing an API endpoint, an event schema, or modifying an existing contract.

## Query MCP first

- `query("", types=["agent"], tags=["api-designer"])` — full persona prompt
- `query("", tags=["api"])`, `query("", tags=["microservices"])`
- `query("", tags=["event-driven"])` if it's a Kafka event
- `query("", tags=["multi-tenancy"])` — tenant_id propagation rules

## Working rules

- Schemas first; the endpoint signature follows.
- POSTs creating state require an `Idempotency-Key` header.
- Standard HTTP status codes. No 200-with-error-body.
- Versioned from day one (`/v1/`, topic suffix `.v1`). Breaking change = new version + parallel run.

## If MCP is unreachable

Stop work and tell the developer. See CLAUDE.md.
