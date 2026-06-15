---
name: plan
description: Converts ticket specs (spec.md) into test-driven implementation plans (plan.md) with ordered steps, traceability, and validation. Use when the user runs /plan or needs an actionable implementation plan.
---

# Plan Skill

Converts a ticket `spec.md` into a test-driven implementation plan (`plan.md`) using the unified P/W/K/X format.

---

## Workflow

### 1. Determine Input Source

**Preferred input:** `artifacts/tickets/{ID}/spec.md`

If no spec is provided, ask for the spec path or ticket ID, or recommend running `/spec` first.

### 1b. Consult ADR Index

Read `artifacts/architecture/README.md` if it exists. Identify ADRs relevant to the spec's
domain. Reference them in the Implementation Strategy and Related Documentation sections
of the plan.

- *Fallback:* If `README.md` is absent, or if it is empty, contains only a placeholder
  (e.g., "No ADRs recorded yet"), or yields no parseable ADR entries, and `ADR-<NNN>-*.md`
  files exist in `artifacts/architecture/`, scan those ADR files directly to discover
  relevant ADRs. If ADR files exist but are not reflected in the index, you may briefly
  note in the plan that the ADR index appears out of date or incomplete.
- If neither an ADR index nor any `ADR-<NNN>-*.md` files exist, skip this step and proceed
  normally.

### 2. Parse Spec File

**Read and extract:**

1. **Traceability anchors:** S###, F###, N###, E###, C###, A###, M###, U###, I###
2. **Open questions:** Q### that must be resolved before committing to plan steps
3. **Interfaces and contracts:** APIs, models, validation rules to reflect in P### steps
   - If a step introduces/changes an API/model/validation, include brief interface/contract notes in the
     P### step (do not defer this to execution; it drives correct implementation and tests).

### 3. Generate Plan Document (Unified Format)

Use the template from:
- [PLAN-TEMPLATE.md](PLAN-TEMPLATE.md) - Canonical P/W/K/X plan structure

**Work Packages (optional)**

If the plan has many steps or spans multiple areas, group related P### steps using headings:

```markdown
### Work Package: [NAME]
```

Work Packages are for readability only. Execution remains P###-driven (checkboxes, dependencies,
K### checkpoints, X### commit points). Do not introduce a second task ID scheme (e.g., `T01`), and do not
reference a separate task template.

---

## Output Location

**Save plan to:**
- Ticket: `artifacts/tickets/PROJ-123/plan.md` (optionally `artifacts/tickets/PROJ-123-short-slug/plan.md`)
- Ad-hoc: `artifacts/tickets/$001/plan.md` (optionally `artifacts/tickets/$001-short-slug/plan.md`)

The plan must live next to its corresponding `spec.md`.

---

## Validation Checklist

Before finalizing plan, verify:

- [ ] All success criteria (S###) and functional requirements (F###) are covered by P### steps
- [ ] Each P### step references spec IDs and includes concrete validation
- [ ] Each step cites relevant coding standards IDs via `.claude/context/coding-standards.md`
  - General: Y### / Z###
  - Language-specific (as applicable): PY### / PZ### or JY### / JZ###
- [ ] Dependencies correctly mapped
- [ ] Test coverage is comprehensive (U### and I### coverage)
