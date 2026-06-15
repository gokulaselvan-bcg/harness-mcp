---
name: implement
description: Executes plan steps (P###) using a test-driven development workflow with validation and progress tracking. Use when the user runs /implement or needs to execute a plan step-by-step.
---

# Implement Skill

Executes a unified `plan.md` (P/W/K/X format) step-by-step with validation, progress tracking, and optional automation.

---

## Pre-Implementation Setup

Before starting execution, verify environment is ready. See [WORKTREE-SETUP.md](WORKTREE-SETUP.md) for:
- Git worktree detection
- Python virtual environment setup with `uv`
- Dependency installation
- Environment verification checklist

Coding standards and anti-patterns are canonical under `.claude/context/coding-standards.md`

---

## Workflow

### 1. Identify Starting Point

**Parse plan to find current state:**

1. Read `artifacts/tickets/{ID}/plan.md`
2. Identify all **P###** steps and checkbox states (`- [ ]` / `- [x]`)
   - Ignore any `### Work Package: ...` headings (grouping only; no execution semantics)
3. Identify all **K###** checkpoints and **X###** commit points (if present)
4. Determine the next step:
   - First unchecked P### step whose declared dependencies (if any) are completed
   - If dependencies are unclear, stop and ask the user to resolve the ambiguity in the plan
5. Display summary:
   ```
   Plan: artifacts/tickets/{ID}/plan.md
   Completed steps: [X] / [N]
   Next step: P00?-... (depends on: ...)

   Environment: [worktree/main] - [venv status]
   ```

### 2. Implement Step

**For each P### step:**

#### 2a. Start Step
1. Display: step ID, purpose, dependencies
2. List affected files (W###) and the spec IDs being implemented (F/C/M/E/U/I)
3. Review cited **Y###** guidelines and **Z###** anti-patterns (via `.claude/context/`)
   - If the code is Python or Java, also review the language pack IDs (PY/PZ or JY/JZ)

#### 2b. Execute Implementation
1. Implement the code changes for the step
2. Add/adjust tests as required by the step's validation plan

#### 2c. Validate
See [VALIDATION-REFERENCE.md](VALIDATION-REFERENCE.md).

1. Run the concrete validation commands referenced by the step
2. If passing, proceed
3. If failing, stop, triage, fix, and re-run validation

### 3. Update Plan File

**After step completion:**

1. Mark the step checkbox as complete: `- [ ]` -> `- [x]`
2. Update `Progress Summary` (Completed Steps count and Last Updated)
3. Record any deviations/notes in the plan (keep traceability to spec IDs)

### 4. Step Completion Flow

**When a P### step is complete:**
1. Display completion confirmation
2. Identify next incomplete P### step
3. Ask whether to continue to the next step

If the user wants to stop:
- Save current progress in `plan.md`
- Stop at a documented safe point (preferably after a checkpoint/commit point)

### 5. Final Verification

**When all steps complete:**

1. Verify all P### steps are checked
2. Verify all K### checkpoints are complete
3. Ensure final validation section is executed (tests, typecheck/lint if applicable)
4. Mark plan status as `Completed` and update `Last Updated`

---

## Human Intervention Triggers

**Only prompt user when:**

1. Software installation required
2. Validation cannot execute (missing tools, environment issues)
3. Validation failure beyond agent capabilities
4. Technical blocker identified (architectural decision, scope change, missing Q### decisions)
5. Environment setup fails

**Key Principle:** Human intervention is exception, not rule. Routine passing validations proceed automatically.

---

## Verification Checklist

**Before marking a P### step complete:**
- [ ] All step validations pass
- [ ] Affected files match the plan (W###)
- [ ] Step remains consistent with cited Y/Z standards
- [ ] Code follows project conventions
- [ ] No linter errors
- [ ] Ad-hoc scripts removed

---

## Error Handling

| Error | Action |
|-------|--------|
| Plan not found | List available plans |
| Step implementation fails | Troubleshoot, ask user |
| Acceptance criteria can't verify | Document, ask user |
| Dependencies incomplete | List missing, ask preference |

For environment-specific errors, see [WORKTREE-SETUP.md](WORKTREE-SETUP.md).

---

## Optional Automation

Only perform automation when tools are available and configured:

- **Commits**: At each X### commit point, use the `managing-git` skill to commit the intended changes.
- **PR creation**: If `gh` is available and authenticated, use `managing-git` to open a PR.
- **Jira transitions**: If Atlassian MCP is available, use `managing-jira` to transition tickets.
