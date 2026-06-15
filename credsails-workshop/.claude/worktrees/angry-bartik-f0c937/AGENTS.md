# Agent Instructions

This file provides high-level instructions for AI agents working on the BCG X Agentic Coding Field Guide
repository.

## Project Overview

The **BCG X Agentic Coding Field Guide** is a practical resource designed to help
teams adopt agentic coding workflows with modern AI-assisted development tools (for example: Claude Code,
Cursor, and GitHub Copilot).

This repository serves as:

1. **Reference Implementation**: An example of best practices for AI-friendly development
2. **Template Repository**: Scaffolding that teams can use to start new projects
3. **Guidebook Resource**: Documentation and examples you can adapt to your project
4. **Automation Toolkit**: Workflow skills that improve AI-assisted development


### What Agents Working on This Repository Are Maintaining

Agents working on **this repository** (agentic-coding) are maintaining:
- The template and scaffolding structure itself
- Skills in `.claude/skills/`
- Documentation site content
- Pattern library
- Templates inside owning skills (e.g. `.claude/skills/*/`)

This is a **meta-project** - the workflow skills are designed to be used in OTHER projects that adopt this template.

## Technology Stack

### Core Technologies

- **Documentation**: Astro with Starlight (Node.js-based static site generator)
- **Node.js Version**: 18+ (managed via nvm or system Node)
- **Package Manager**: npm or pnpm
- **Markdown**: MDX (Astro's markdown processor with component support)
- **Pre-commit Hooks**: pre-commit (for markdown and YAML validation)

### Note on Python Skills

The `.claude/skills/` directory contains Python coding standards (Y100-Y800 series) and anti-patterns (Z100-Z600 series). These are **for teams using this template**, not for this repository itself. This repository is primarily documentation and does not contain Python application code.

## Project Structure

```
agentic-coding/
├── .claude/              # Claude/Cursor configuration
│   ├── skills/           # Reusable agent skills
│   └── rules             # Project rules and standards
├── .github/              # GitHub workflows and templates
├── artifacts/            # Design and planning documents (created when workflows are used)
│   ├── architecture/     # Architecture decisions (ADRs)
│   ├── requirements/     # Product Requirements Documents (PRDs)
│   ├── blueprints/       # Project-level technical blueprints (HLD)
│   └── tickets/          # Ticket-based planning and designs
│       └── TICKET-*/     # Per-ticket: design.md, plan.md, research/
├── docs/                 # Astro/Starlight documentation site
│   ├── astro.config.mjs  # Astro configuration
│   ├── package.json      # Node.js dependencies
│   ├── src/
│   │   └── content/docs/ # Documentation pages (MDX/Markdown)
│   └── public/           # Static assets
├── contributions/        # Optional/extra documentation (not core)
│   └── pattern-library/  # Pattern library and guidebook (contribution)
│       ├── documents/    # Pattern documentation
│       └── site/         # Pattern library site (standalone)
├── AGENTS.md             # This file - agent instructions
├── .claude/skills/generate-agents/AGENTS-template.md # Template used by generate-agents
├── CLAUDE.md             # Project context for Claude
├── QUICK-START.md        # Link to Setup Guide
└── README.md             # Main project documentation
```

### Important Notes

- **`artifacts/` directory**: Does not exist initially in the repository. It is created when workflow skills are used (by projects that adopt this template). The structure shown above represents what gets created during workflow usage.

- **Contributions in the docs site**: Contributions (for example the Pattern Library) live under `contributions/`, and are synced into the `docs/` content tree at dev/build time (no repo-committed symlinks required).

## Documentation Standards

### Markdown Style

- **Follow Markdown best practices**: Use consistent formatting
- **Headers**: Use proper heading hierarchy (H1 for page title, H2 for sections, etc.)
- **Links**: Use relative links for internal documentation
- **Code blocks**: Specify language for syntax highlighting
- **Line Length**: Keep lines under 100 characters where possible for readability

### Astro Site Structure

- **Pages**: Place markdown/MDX files in `docs/src/content/docs/` directory
- **Navigation**: Update `astro.config.mjs` sidebar configuration
- **Assets**: Place images in `docs/src/assets/`, static files in `docs/public/`
- **Front Matter**: All pages should include YAML front matter with title and description

### Example Page Structure

```markdown
---
title: "Page Title"
description: "Brief description of this page"
---

# Page Title

Content goes here...
```

### Documentation Rules

1. **Update documentation** when making changes to workflows, skills, or templates
2. **Test locally** before committing: `npm run dev` (in docs/ directory)
3. **Check for broken links** and formatting issues
4. **Keep `dist/` and `.astro/` directories** in `.gitignore` (generated files)
5. **Follow consistent formatting** across all markdown files
6. **Use proper heading hierarchy** (H1 for page title, H2 for sections)
7. **Include front matter** in Astro pages (title and description)
8. **Update navigation** in `astro.config.mjs` when adding new pages

### Pre-commit Hooks

Pre-commit hooks automatically check for:
- Trailing whitespace
- End of file newlines
- YAML validity
- Large files
- Merge conflicts

Run before committing:
```bash
pre-commit run --all-files
```

## Common Tasks

### Adding New Documentation

1. **Create the document**:
   ```bash
   # Create new markdown file in appropriate directory
   touch docs/src/content/docs/new-page.md
   ```

2. **Add front matter**:
   ```markdown
   ---
   title: "Page Title"
   description: "Brief description of this page"
   ---
   ```

3. **Update navigation** (if needed):
   ```javascript
   // Edit docs/astro.config.mjs sidebar configuration
   sidebar: [
     { label: 'New Page', slug: 'new-page' },
   ]
   ```

4. **Test locally**:
   ```bash
   cd docs
   npm run dev
   # Visit http://localhost:4321 to preview
   ```

5. **Commit and push**:
   ```bash
   git add docs/src/content/docs/new-page.md docs/astro.config.mjs
   git commit -m "docs: add new documentation page"
   ```

### Updating Existing Documentation

1. **Edit the markdown file** in `docs/src/content/docs/`
2. **Test locally** with Astro: `npm run dev`
3. **Check for broken links**
4. **Run pre-commit hooks**:
   ```bash
   pre-commit run --all-files
   ```
5. **Commit changes**:
   ```bash
   git add docs/src/content/docs/updated-page.md
   git commit -m "docs: update page content"
   ```

### Updating Workflow Skills

When modifying workflow skills in `.claude/skills/`:

1. **Edit the canonical skill** under `.claude/skills/<name>/SKILL.md`
2. **Keep workflow logic in the skill directory**, including any helper scripts or templates
3. **Update related documentation** in `docs/src/content/docs/workflows/skills.md`
4. **Update `docs/src/content/docs/setup.md`** if invocation/setup instructions change
5. **Commit changes**:
   ```bash
   git add .claude/skills/spec/SKILL.md docs/src/content/docs/workflows/skills.md
   git commit -m "feat: update spec workflow skill"
   ```

### Updating Skills

When modifying skills in `.claude/skills/`:

1. **Edit the skill file** (e.g., `.claude/skills/creating-designs/SKILL.md`)
2. **Update SKILLS.md** if adding new skills
3. **Test the skill** with relevant invocations
4. **Commit changes**:
   ```bash
   git add .claude/skills/creating-designs/SKILL.md
   git commit -m "feat: update creating-designs skill"
   ```

### Updating Templates

Templates live inside their owning skills (e.g., `.claude/skills/spec/SPEC-TEMPLATE.md`,
`.claude/skills/blueprint/BLUEPRINT-TEMPLATE.md`, `.claude/skills/adr/ADR-TEMPLATE.md`,
`.claude/skills/prd/PRD-TEMPLATE.md`). When modifying a template:

1. **Edit the template file** in the owning skill directory (e.g.,
   `.claude/skills/blueprint/BLUEPRINT-TEMPLATE.md`)
2. **Update related documentation** if template structure changes
3. **Test with workflow skills** that use the template (e.g., `/blueprint`, `/spec`)
4. **Commit changes**:
   ```bash
   git add .claude/skills/blueprint/BLUEPRINT-TEMPLATE.md
   git commit -m "feat: update blueprint template structure"
   ```

### Running Quality Checks

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Run Python tests (uses uv for dependency management)
uv run pytest tests/ -v

# Test Astro site locally
cd docs
npm run dev

# Build site to check for errors
cd docs
npm run build
```

## Default Variables

These variables are used as defaults across workflow skills. Skills should reference these values from this file.


### Jira Configuration

- **Default Jira Project Key**: `BOXWRBTWPO`
  - Used as a default/suggested project key in Jira workflows
  - Teams replace this with their actual project key (e.g., `PROJ`, `MYAPP`)
  - Can be overridden by user selection during workflow execution

- **Jira Issue Type IDs**:
  - Epic: `13328`
  - Task: `13327`
  - Subtask: `13329`
  - Used in ticket creation workflows for specifying issue types
  - Teams may need to update these based on their Jira instance configuration

- **Jira Transition ID**:
  - "In Progress" transition: `21`
  - Used when moving tickets to In Progress status
  - Teams may need to update this based on their Jira workflow configuration

### Git Configuration

- **Default Git Branch**: `main`
  - Used as the target branch for pull requests in implementation workflows
  - Can be overridden by user selection during workflow execution
  - Teams using `master` or other default branches should update this value

---

*Agent instructions for BCG X Agentic Coding Field Guide*
*Last updated: 2026-02-19*
