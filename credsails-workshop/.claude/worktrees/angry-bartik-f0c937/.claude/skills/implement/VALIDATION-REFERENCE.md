# Validation Reference

Patterns for validating acceptance criteria during task implementation.

---

## Validation Process

**For each acceptance criterion:**

1. **Run validation command** (as specified in criterion)
   ```bash
   uv run pytest tests/test_feature.py -v
   uv run python -c "from module import func; assert func()"
   ```

2. **Display result with status:**
   - `✓ Acceptance Criterion: [Description]`
   - `  Status: [X] out of [X] tests passed`

3. **If validation passes:**
   - Mark checkbox ✅ automatically
   - Continue to next criterion (NO user interaction)

4. **If validation fails:**
   - Display: `✗ Acceptance Criterion: [Description]`
   - Display error output
   - **STOP immediately**
   - **Triage the problem**
   - **Attempt to fix** if within capabilities
   - **Escalate to user** if beyond capabilities

---

## Testing Requirements

### Write Proper Tests
- Create test files in appropriate directory (`tests/` for Python)
- Use project's testing framework (e.g., `pytest`)
- Tests should be permanent and repeatable
- Follow project naming conventions

### CLI Verification (Using uv)

**Always use `uv run` for Python commands:**
```bash
# Run pytest
uv run pytest tests/test_module.py -v

# Quick verification
uv run python -c "from mymodule import func; print(func())"

# Run script
uv run python scripts/verify.py
```

Use `curl`, `git status`, etc. for non-Python verification.

### Cleanup
- Remove any ad-hoc verification scripts
- Verify no temporary files remain

---

## Troubleshooting Workflow

When validation fails:

1. **Document issue** - Capture exact error
2. **Analyze causes** - List possibilities
3. **Create plan** - For each cause: verify, solution
4. **Present to user** - Ask before proceeding
5. **Execute with approval** - Work through systematically
6. **Verify fix** - Re-run failing command

---

## Test Script Management

**Permanent scripts:**
- Place in `tests/` directory (or project-specific location)
- Follow project testing framework conventions
- Named appropriately, organized by feature

**Ad-hoc scripts:**
- Remove after verification
- Document in task that cleanup needed

**Prefer CLI with uv:**
- Use `uv run python -c "..."` for one-time checks
- Avoid creating temporary files when possible

---

## Status Indicators

| Status | Indicator | Meaning |
|--------|-----------|---------|
| Complete | ✅ | All criteria pass |
| In Progress | 🔄 | Currently working |
| Not Started | ⬜ | Waiting or not begun |
| Blocked | ⚠️ | Cannot proceed |
