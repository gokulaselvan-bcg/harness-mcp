---
name: update-context
description: Update and extend .claude/context with agent-friendly structure, size limits, and navigable indexes.
---

# Update Context

This skill updates `.claude/context/` files to keep them concise, navigable, and
safe for selective loading by agents.

## Source of Truth

- General rules: `.claude/context/README.md`
- XML format + validation rules: `.claude/context/AGENTS.md`
- Coding standards structure: `.claude/context/coding-standards/overview.md`

## Workflow

1. **Locate entrypoints** for the target area (root index, domain overview, and
   topic indexes).
2. **Apply size/split rules** (target <=80 lines per file).
   - `.claude/context/**` is primarily **XML** (manifests + rulesets), with a few
     Markdown entrypoints (e.g. `README.md`, `coding-standards.md`, `overview.md`).
   - **Coding standards** under `.claude/context/coding-standards/**`:
     - Only `overview.md` is Markdown (human entrypoint)
     - All indexes + rule content are XML (`*.xml`)
     - Hundreds metadata: `<language>/index.xml` with `<entry kind="hundreds" ... desc="...">`
     - Tens metadata: `<language>/<hundreds>/index.xml` with `<entry kind="tens" ... desc="...">`
     - Rule files: `<rules><rule id="..."><desc>...</desc>...</rule></rules>`
     - References: `<related><ref id="..."/></related>` (never comma-separated text)
     - Code blocks: `<code lang="..."><![CDATA[...]]></code>` (never backticks)
     - No anchors: do not add `anchor` attributes (ids are link targets)
     - Manifests use `<doc_ref path="..."/>` nodes (not `path="..."` attributes)
3. **Write/refresh index summaries** so each entry has a 1-line "when to load" description.
   - For coding standards, the source of truth is:
     - `index.xml`: `<entry ... desc="...">`
     - rule XML: `<rule><desc>...</desc></rule>`
4. **Regenerate full catalogs** if you changed any coding standards rule files:
   - `python .claude/tools/context/generate_catalog.py`
   - (Optional) `python .claude/tools/context/generate_catalog.py --check`
5. **Update references** (index links and any root entrypoints).
6. **Format + validate XML + references (mandatory)**:
   - `make format-context` (idempotent; required)
   - `make validate-context` (required; must pass)
7. **Validate catalogs** with the strict checker (coding standards only):
   - `python .claude/tools/context/generate_catalog.py --check`

## Guardrails

- Keep files short and minimal; avoid large appendices.
- Prefer splitting over expanding single files.
- Do not duplicate standards in commands or skills; reference canonical files.
- Keep filenames and IDs stable unless structure changes require renaming.
- When editing XML, follow `.claude/context/AGENTS.md` and the schema at
  `.claude/context/schema/context.xsd`.
