# Agent Skills Index

This index provides metadata for all available skills. Skills are loaded on-demand to optimize context use.

## Invocation Model

All workflows support two equivalent invocation styles:

- Slash-command tools: `/name`
- Skill-invocation tools: `$name`

Behavior is canonical in `.claude/skills/<name>/SKILL.md`. Command files in `.claude/commands/`
are thin entrypoints that forward to same-name skills.

## Workflow Skills

### adr

**Purpose**: Create architecture decision records (ADRs)
**Invoke as**: `/adr` or `$adr`
**Skill file**: `.claude/skills/adr/SKILL.md`

### pull-ticket

**Purpose**: Pull a Jira ticket into local artifact context
**Invoke as**: `/pull-ticket` or `$pull-ticket`
**Skill file**: `.claude/skills/pull-ticket/SKILL.md`

### spec

**Purpose**: Create ticket-level implementation specs (`spec.md`)
**Invoke as**: `/spec` or `$spec`
**Skill file**: `.claude/skills/spec/SKILL.md`

### plan

**Purpose**: Convert `spec.md` into executable `plan.md`
**Invoke as**: `/plan` or `$plan`
**Skill file**: `.claude/skills/plan/SKILL.md`

### implement

**Purpose**: Execute plan steps with validation and progress tracking
**Invoke as**: `/implement` or `$implement`
**Skill file**: `.claude/skills/implement/SKILL.md`

### prd

**Purpose**: Create product requirements documents
**Invoke as**: `/prd` or `$prd`
**Skill file**: `.claude/skills/prd/SKILL.md`

### blueprint

**Purpose**: Create project-level technical blueprints (HLD)
**Invoke as**: `/blueprint` or `$blueprint`
**Skill file**: `.claude/skills/blueprint/SKILL.md`

### blueprint-to-tickets

**Purpose**: Decompose a blueprint into epics and ticket files
**Invoke as**: `/blueprint-to-tickets` or `$blueprint-to-tickets`
**Skill file**: `.claude/skills/blueprint-to-tickets/SKILL.md`

### ticket-to-jira

**Purpose**: Export blueprint-derived tickets to Jira via MCP
**Invoke as**: `/ticket-to-jira` or `$ticket-to-jira`
**Skill file**: `.claude/skills/ticket-to-jira/SKILL.md`

### pr-review

**Purpose**: Review pull requests against intent and standards
**Invoke as**: `/pr-review` or `$pr-review`
**Skill file**: `.claude/skills/pr-review/SKILL.md`

### generate-agents

**Purpose**: Generate `AGENTS.md` from `AGENTS-template.md`
**Invoke as**: `/generate-agents` or `$generate-agents`
**Skill file**: `.claude/skills/generate-agents/SKILL.md`

### update-context

**Purpose**: Maintain `.claude/context/` structure and indexes
**Invoke as**: `/update-context` or `$update-context`
**Skill file**: `.claude/skills/update-context/SKILL.md`

## Supporting Skills

### coding-standards

**Purpose**: Entry point to coding standards and anti-patterns catalogs
**Skill file**: `.claude/skills/coding-standards/SKILL.md`

### managing-git

**Purpose**: Branch/commit/push/PR operations for workflow automation
**Skill file**: `.claude/skills/managing-git/SKILL.md`

### managing-jira

**Purpose**: Jira operations via Atlassian MCP
**Skill file**: `.claude/skills/managing-jira/SKILL.md`

### gh-cli

**Purpose**: Safe and reliable GitHub CLI patterns
**Skill file**: `.claude/skills/gh-cli/SKILL.md`
