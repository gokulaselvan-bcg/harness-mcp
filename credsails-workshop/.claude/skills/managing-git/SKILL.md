---
name: managing-git
description: Git operations for ticket-based development including branch creation, commits, pushes, and pull requests. Use when the user needs to create branches, commit changes, push to remote, or create PRs during implementation workflows.
---

# Managing Git Skill

Provides Git operations for ticket-based development, including branch management, commits, and pull
requests.

## Default Variables

Retrieve from `AGENTS.md` (see "Default Variables" section):
- **Default Git Branch**: Base branch for ticket branches (e.g., `main` or `develop`)

---

## Operations

### 1. Create Ticket Branch

**Generate branch name from ticket:**

**Format:** `<prefix>/<ticket-key>-<ticket-name-slug>`

**Prefix selection (choose one):**

| Prefix | Use for |
|--------|---------|
| `ft/` | Feature / new capability |
| `rf/` | Refactor (no functional change) |
| `doc/` | Documentation |
| `test/` | Tests |
| `conf/` | Configuration / tooling |

If unclear, ask the user which prefix they want. Default to `ft/` if they prefer not to decide.

**Sanitization rules:**
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep only alphanumeric and hyphens)
4. Limit to 50 characters (including ticket key prefix)
5. Remove common prefixes like "DEV-SETUP-001:", "EPIC-01-", etc.

**Examples:**
- Ticket: "DEV-SETUP-001: Backend Development Environment Setup"
  - Branch: `conf/proj-3-backend-dev-env-setup`
- Ticket: "Frontend Project Initialization (React + TypeScript)"
  - Branch: `ft/proj-6-frontend-project-init`

**Branch Creation Process:**

```bash
# 1. Check if branch already exists
git branch --list "[BRANCH_PREFIX]/[BRANCH_NAME]"

# If exists: Checkout existing branch
git checkout [BRANCH_PREFIX]/[BRANCH_NAME]

# If not exists:
# 2. Checkout base branch (from AGENTS.md)
git checkout [DEFAULT_GIT_BRANCH]

# 3. Pull latest changes
git pull origin [DEFAULT_GIT_BRANCH]

# 4. Create and checkout new branch
git checkout -b [BRANCH_PREFIX]/[BRANCH_NAME]

# 5. Verify branch was created
git branch --show-current
```

**If branch creation fails:**
- If base branch doesn't exist, try alternative common branches (main/develop)
- If both fail, ask user which branch to use as base
- Ask if they want to proceed without creating a branch

**When in a worktree:**
- Pull from git with full permission
- Handle worktree-specific branch operations

---

### 2. Commit Changes

**Conventional Commit Format:**

```
<type>: <description> (<TICKET-ID>)

- Brief bullet point of key changes
- Another key change
- Reference any fixes or important notes
```

**Commit Types:**

| Type | Description |
|------|-------------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation changes |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Test additions/modifications |
| `chore` | Build/tooling changes |

**Commit Process:**

```bash
# 1. Stage all changes
git add -A

# 2. Check status
git status

# 3. Create commit
git commit -m "feat: description of changes (PROJ-123)

- Key change 1
- Key change 2
- Key change 3"
```

---

### 3. Push to Remote

**Push Process:**

```bash
# 1. Get current branch name
git branch --show-current

# 2. Push to remote
# If branch has upstream:
git push

# If no upstream (new branch):
git push --set-upstream origin <branch-name>
```

**Display push confirmation after successful push.**

---

### 4. Create Pull Request

**Prerequisites:**
1. Check if GitHub CLI is installed: `gh --version`
2. Check if authenticated: `gh auth status`
3. Check for uncommitted changes: `git status --short`

**Important:** `gh` auth and related operations may fail in sandboxed execution. Run `gh` with
sandboxing disabled (full system access) if authentication-related commands fail.
For more `gh` patterns, invoke the **gh-cli** skill.

**If GitHub CLI is available and authenticated:**

```bash
template_path="$(
  find .github -maxdepth 2 -type f -iname '*pull*request*template*' 2>/dev/null | head -n 1
)"

if [ -n "$template_path" ]; then
  cp "$template_path" /tmp/pr-body.md
else
  cat > /tmp/pr-body.md <<'EOF'
## Summary
- ...

## Changes
- ...

## Testing
- ...
EOF
fi

# Edit /tmp/pr-body.md to fill in the sections

gh pr create \
  --base [DEFAULT_GIT_BRANCH] \
  --title "feat: description of changes ([TICKET-ID])" \
  --body-file /tmp/pr-body.md
```

**If GitHub CLI not available or not authenticated:**
- Skip PR creation step
- Display note: "GitHub CLI not available or not authenticated - PR creation skipped."
- Do NOT attempt to create PR or provide manual links - simply skip

---

## Error Handling

**If base branch doesn't exist:**
- Try `main` first, then `develop`
- If both fail, ask user which branch to use

**If push fails:**
- Check if remote is configured
- Check for authentication issues
- Display error and ask user to resolve

**If PR creation fails:**
- Display error message
- Suggest creating PR manually via web interface
- Do not block workflow completion

---

## Cleanup Operations

**After implementation is complete:**

```bash
# Remove legacy root-level ticket.md if it exists (ticket context should live under artifacts/)
rm -f ticket.md

# Remove legacy gap files if content is in plan
rm -f backend/GAPS.md
```

**Verify no temporary files remain before final commit.**
