---
name: java-standards
description: Activates when reading or editing Java files (.java) or working in a Spring Boot service. Loads Java-specific decisions, standards, and anti-patterns from MCP. Use alongside the active role skill.
---

# Java standards

In effect whenever Java files are being read or edited.

## Query MCP first

- `query("", tags=["java"])` — every Java decision, pattern, and standard
- `query("", tags=["anti-overengineering", "java"])` — the Java ban list
- `query("testing", tags=["java"])` — JUnit 5 + Mockito + Spring Boot Test standards

## Working rules (high-level — MCP holds the substance)

- Records for DTOs. Bean Validation + `@Valid` at every controller boundary.
- Constructor injection only. No `@Autowired` on fields. No Lombok `@Data`.
- Default to synchronous Spring MVC. Reactive only with tech-lead approval.
- JUnit 5 + AssertJ + Mockito. Testcontainers for real Postgres / Kafka.

## If MCP is unreachable

Stop work and tell the developer. See CLAUDE.md.
