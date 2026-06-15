# Worktree and Environment Setup

Setup guide for git worktrees and Python environments before implementing tasks.

---

## Detecting a Git Worktree

Before starting any implementation, detect if running in a worktree:

```bash
# .git is a FILE in worktrees, DIRECTORY in main repos
[ -f .git ] && echo "WORKTREE" || echo "MAIN_REPO"
```

**Why this matters:** Each worktree needs its own virtual environment. The parent repo's `.venv` is not shared with worktrees.

---

## Python Environment Setup

**When worktree detected OR `.venv` missing:**

### 1. Check for Python project indicators
- `requirements.txt` at root
- `backend/requirements.txt`
- `pyproject.toml`
- `.py` files in source directories

### 2. Create virtual environment with `uv` (preferred - 10-100x faster)

```bash
# Install uv if not available
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv
uv venv .venv
```

### 3. Install dependencies

```bash
# Standard requirements.txt
uv pip install -r requirements.txt

# Backend-specific (common in monorepos)
uv pip install -r backend/requirements.txt

# With pyproject.toml
uv pip install -e .

# Development dependencies
uv pip install -e ".[dev]"
```

### 4. Verify setup

```bash
uv run python --version
uv run python -c "import sys; print(sys.executable)"
```

---

## Environment Verification Checklist

Before proceeding with tasks:
- [ ] Worktree status known (worktree or main repo)
- [ ] `.venv` directory exists
- [ ] Dependencies installed
- [ ] `uv run python` works
- [ ] `uv run pytest --collect-only` succeeds (if tests exist)

---

## Running Python Commands

**Always use `uv run` for Python execution in worktrees:**

```bash
# Run tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_feature.py -v

# Quick Python verification
uv run python -c "import mymodule; print('OK')"

# Run scripts
uv run python scripts/verify.py
```

---

## Environment Error Handling

| Error | Action |
|-------|--------|
| `uv` not found | Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| venv missing | Create: `uv venv .venv` |
| Dependencies missing | Install: `uv pip install -r requirements.txt` |
| Import errors | Check venv activated, reinstall deps |
| Wrong Python version | Use `uv venv --python 3.11` (specify version) |

---

## Quick Reference Commands

```bash
# Detect worktree
[ -f .git ] && echo "WORKTREE" || echo "MAIN"

# Setup environment (run once per worktree)
uv venv .venv
uv pip install -r requirements.txt
# OR
uv pip install -r backend/requirements.txt

# Run Python commands
uv run python script.py
uv run pytest tests/ -v
uv run python -c "print('hello')"

# Check environment
uv run python --version
uv run pip list
```
