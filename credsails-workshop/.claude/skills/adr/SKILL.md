---
name: adr
description: Creates Architecture Decision Records (ADRs) under artifacts/architecture using the ADR template.
---

# ADR Skill

Creates an Architecture Decision Record for project-wide or cross-cutting decisions.

## Output Location

- `artifacts/architecture/ADR-<NNN>-<short-title>.md`

## Workflow

1. **Gather decision context**
   - Decision title, problem statement, constraints, and alternatives.
   - Related specs/plans or tickets that triggered the decision.

2. **Determine ADR number and filename**
   - Scan `artifacts/architecture/` for existing `ADR-<NNN>-*.md` files.
   - Use the next sequential 3-digit number (e.g., 001, 002).
   - Create a short, lowercase, hyphenated slug (3-7 words).

3. **Write the ADR**
   - Use the template at `.claude/skills/adr/ADR-TEMPLATE.md`.
   - Keep it concise: context, decision, rationale, consequences.
   - Avoid implementation details (those belong in specs/plans).

4. **Cross-reference**
   - Link related ADRs and specs/plans in the ADR.
   - Reference the ADR from any relevant spec using the "Related ADRs" section.

5. **Update the ADR index**
   - Scan `artifacts/architecture/` for all `ADR-<NNN>-*.md` files.
   - If no ADR files exist, skip this step (nothing to index).
   - For each ADR file, extract the **Status** and **Date** fields from the header.
     If a field is missing or unparseable, use defaults and warn the user:
       - Status: `Unknown`
       - Date (in priority order, first available wins):
         1. Git add date for the file (e.g., `git log --diff-filter=A --follow --format=%cs -1 <file>`).
         2. Filesystem modification time (mtime) of the ADR file.
         3. Literal fallback value `Unknown`.
   - Build a flat list sorted by ADR number ascending:

     ```markdown
     - **ADR-001-short-title** | Accepted | 2026-03-20
     - **ADR-002-another-decision** | Proposed | 2026-03-25
     ```

   - Write (or overwrite) `artifacts/architecture/README.md` with:
     1. Title: `# Architecture Decision Records`
     2. Introductory text referencing `architecture.md` for the system overview
     3. The ADR index as a flat bullet list (one ADR per line, as shown above)
     4. Footer: `*Auto-maintained by the /adr skill. Last updated: YYYY-MM-DD.*`
   - Always do a **full rebuild** (scan all files) rather than an incremental update.
     This keeps the index idempotent and self-healing if it drifts out of sync.

## Conventions

- ADRs live under `artifacts/architecture/`.
- File naming follows `ADR-<NNN>-<short-title>.md`.
- Prefer one decision per ADR.
- The ADR index in `artifacts/architecture/README.md` is auto-maintained by step 5.
  Other skills (`spec`, `plan`) use it as the entry point for ADR discovery.

## Related Standards

If the decision establishes or constrains coding practices, cite relevant Y/Z IDs in
"Related Guidelines" and use the `coding-standards` skill for reference.

## Authoring Guidance

### When to Write an ADR

Create an ADR when any of the following apply:

- A significant architectural decision is being made.
- Multiple viable options are being weighed.
- The decision will be hard to reverse.
- The decision affects multiple parts of the system.
- The decision sets a precedent for future similar work.

### Best Practices

1. **Keep it concise** — ADRs should be readable in 5–10 minutes.
2. **Be specific** — include enough detail to understand the decision.
3. **Document alternatives** — show what options were considered (see `### Options Considered (Optional)` in `ADR-TEMPLATE.md`).
4. **Explain trade-offs** — be honest about negative consequences.
5. **Date the decision** — include when it was made.
6. **Update status** — mark as `Superseded` if a new ADR replaces it.
7. **Link related ADRs** — create a web of decisions.
8. **Review periodically** — set review dates for important decisions.

### ADR Statuses

- **Proposed** — decision is being discussed; not yet accepted.
- **Accepted** — decision has been made and approved.
- **Rejected** — proposal was considered but not accepted.
- **Deprecated** — decision is no longer relevant.
- **Superseded** — replaced by a new ADR (link to it).
