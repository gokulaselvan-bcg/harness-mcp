---
name: typescript-standards
description: Activates when reading or editing TypeScript files (.ts, .tsx) or working in a React/Vite project. Loads TypeScript-specific decisions, standards, and anti-patterns from MCP. Use alongside the active role skill.
---

# TypeScript standards

In effect whenever TypeScript or TSX files are being read or edited.

## Query MCP first

- `query("", tags=["typescript"])` — every TypeScript decision, pattern, and standard
- `query("", tags=["anti-overengineering", "typescript"])` — the TS ban list
- `query("testing", tags=["typescript"])` — Vitest + React Testing Library standards

## Working rules (high-level — MCP holds the substance)

- `strict: true` in tsconfig. `any` is banned; use `unknown` and narrow.
- Zod at every fetch boundary. Types inferred from schemas via `z.infer`.
- Function components only. No useEffect for derived state. No useMemo / useCallback without a measured reason.
- Vitest + React Testing Library. msw for network mocks. No Enzyme. Test from the user's perspective.

## If MCP is unreachable

Stop work and tell the developer. See CLAUDE.md.
