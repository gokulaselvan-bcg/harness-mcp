---
name: python-standards
description: Activates when reading or editing Python files (.py) or working in a Python service. Loads Python-specific decisions, standards, and anti-patterns from MCP. Use alongside the active role skill.
---

# Python standards

In effect whenever Python files are being read or edited.

## Query MCP first

- `query("", tags=["python"])` — every Python decision, pattern, and standard
- `query("", tags=["anti-overengineering", "python"])` — the Python ban list
- `query("testing", tags=["python"])` — pytest standards

## Working rules (high-level — MCP holds the substance)

- Pydantic v2 at every external or cross-module boundary. No raw dicts crossing module lines.
- Type hints on every function signature. `Any` requires a comment explaining why.
- Async only where there is real I/O. Never `async` without `await`.
- pytest functions (not classes). Tests fail first. Mock at the boundary only.

## If MCP is unreachable

Stop work and tell the developer. See CLAUDE.md.
