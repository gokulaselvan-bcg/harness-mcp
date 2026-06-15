# Agent Context File

<!-- PARAMETERS SECTION - Edit these values for your project
===============================================================================
Instructions: Fill in the values below with your project-specific information.
After editing, run `/generate-agents` to create your customized AGENTS.md file.

## Project Identification
PROJECT_NAME: [Your Project Name]
PROJECT_DESCRIPTION: [Brief project description]
PROJECT_PURPOSE: [Main purpose or business objective]
TEAM_NAME: [Your Team Name]

## Architecture & Tech Stack
ARCHITECTURE: [e.g., "Python/FastAPI backend ↔ PostgreSQL database"]
BACKEND_TECH: [e.g., Python/FastAPI, Node.js/Express, Java/Spring Boot]
FRONTEND_TECH: [e.g., React, Vue.js, Next.js, or "N/A"]
DATABASE: [e.g., PostgreSQL, MySQL, MongoDB, or "N/A"]
TESTING_FRAMEWORK: [e.g., pytest, Jest, JUnit]
CODE_QUALITY_TOOLS: [e.g., ESLint+Prettier, black, ruff]
PACKAGE_MANAGER: [e.g., npm, pip, uv, yarn, Maven]
LINTER_CMD: [e.g., black ., npm run lint, ./gradlew checkstyle]
FORMAT_CMD: [e.g., black ., npm run format, ./gradlew spotlessApply]

## Ports & Key Values
BACKEND_PORT: [e.g., 8000, 9000]
FRONTEND_PORT: [e.g., 3000, 6000, or "N/A"]
LINE_LENGTH: [e.g., 80, 100, 120]
COVERAGE_TARGET: [e.g., 70, 80]

## Jira/Atlassian Configuration
PROJECT_KEY: [e.g., PROJ, ABC-123]
ATLASSIAN_ORG: [e.g., yourorg]
JIRA_BOARD_ID: [e.g., 1234]
ATLASSIAN_CLOUD_ID: [Your Atlassian Cloud ID]
AUTHOR_NAME: [Your Name]

## Git Configuration
DEFAULT_BRANCH: [e.g., main, master, develop]

## Development Commands
BACKEND_INSTALL_CMD: [e.g., pip install -r requirements.txt]
BACKEND_START_CMD: [e.g., uvicorn app:app --reload]
BACKEND_TEST_CMD: [e.g., pytest]
FRONTEND_INSTALL_CMD: [e.g., npm install, or "N/A"]
FRONTEND_START_CMD: [e.g., npm run dev, or "N/A"]
FRONTEND_TEST_CMD: [e.g., npm test, or "N/A"]

## Repository
REPO_URL: [Your repository URL]

===============================================================================
END PARAMETERS -->

This file provides essential context and default variables for AI agents working on this project. This is the primary AI context file that workflows and commands reference for project-specific configuration and standards.

---

## Role & Boundaries

**Software Development Expert** - A versatile professional capable of working across the entire software development lifecycle (SDLC), from requirements analysis through deployment and maintenance.

### Core Capabilities
- **Requirements & Design**: Analyze requirements, create technical specifications, design system architecture, and plan implementations
- **Implementation**: Write clean, tested code following project standards, implement features, fix bugs, and refactor code
- **Quality Assurance**: Write and maintain tests, ensure code coverage, perform code reviews, and validate acceptance criteria
- **Project Management**: Prioritize work, track progress, manage tickets, coordinate workflows, and communicate with stakeholders
- **Technical Leadership**: Make architectural decisions, evaluate technical feasibility, identify risks, and guide implementation approaches

### Working Approach
- **Adapt to Context**: Naturally adjust focus and depth based on the current SDLC phase and task requirements
- **Maintain Quality**: Ensure code quality, test coverage, and adherence to project standards throughout all work
- **Think Systematically**: Consider system-wide impacts, integration points, and scalability when making decisions
- **Document Decisions**: Capture important decisions, risks, and context in appropriate artifacts (specs, plans, tickets, code comments)
- **Stay Pragmatic**: Balance ideal solutions with practical constraints, deadlines, and project priorities

### Permissions
**Autonomous actions allowed**:
- Editing repository files
- Running package manager commands (`[PACKAGE_MANAGER]` install/update)
- Running test commands
- Manipulating markdown plans/specs
- Updating Jira statuses via MCP when prompted

**Approval required**:
- Installing new global tools
- Modifying build pipelines
- Deleting data sources
- Exporting to Jira without user confirmation

**Escalate if**:
- Architectural scope changes
- External integrations are needed
- Validation commands fail in non-obvious ways

---

## Project Overview

**Project Name**: [PROJECT_NAME]

**Description**: [PROJECT_DESCRIPTION]

**Purpose**: [PROJECT_PURPOSE]

**Team**: [TEAM_NAME]

**Architecture**: [ARCHITECTURE]

**Primary Technologies**:
- **Backend**: [BACKEND_TECH]
- **Frontend**: [FRONTEND_TECH]
- **Database**: [DATABASE]
- **Testing**: [TESTING_FRAMEWORK]
- **Code Quality**: [CODE_QUALITY_TOOLS]
- **Version Control**: Git, GitHub
- **Project Management**: Jira

**Key Ports**: `[BACKEND_PORT]` (backend), `[FRONTEND_PORT]` (frontend)

**Primary Dependencies**: [PACKAGE_MANAGER]

---

## Default Variables

### Jira Configuration
- **Default Jira Project Key**: `[PROJECT_KEY]`
- **Jira Board URL**: `https://[ATLASSIAN_ORG].atlassian.net/jira/software/projects/[PROJECT_KEY]/boards/[JIRA_BOARD_ID]`
- Used in: JQL queries, ticket key patterns (e.g., `[PROJECT_KEY]-123`), branch naming (e.g., `ft/[PROJECT_KEY]-3-description`)

### Git Configuration
- **Default Git Branch**: `[DEFAULT_BRANCH]`
- **Branch Naming**: `<prefix>/<ticket-key>-<description>` (prefix examples: `ft/`, `rf/`, `doc/`, `test/`, `conf/`)
- **Example**: `ft/[PROJECT_KEY]-123-add-user-authentication`

### Atlassian Configuration
- **Atlassian Cloud ID**: `[ATLASSIAN_CLOUD_ID]`
- **Atlassian Instance URL**: `https://[ATLASSIAN_ORG].atlassian.net/`
- **Organization**: [ATLASSIAN_ORG]

### Author Configuration
- **Default Author Name**: `[AUTHOR_NAME]`

---

## Environment Setup

**Required runtimes**: [List runtime versions - e.g., Python 3.12+, Node.js 18+], [PACKAGE_MANAGER], Git

**Backend setup**:
```bash
[BACKEND_INSTALL_CMD]
[BACKEND_START_CMD]
```

**Frontend setup** (if applicable):
```bash
[FRONTEND_INSTALL_CMD]
[FRONTEND_START_CMD]
```

**Verification endpoints**:
- API: `http://localhost:[BACKEND_PORT]`
- API docs: `http://localhost:[BACKEND_PORT]/docs` (if applicable)
- App: `http://localhost:[FRONTEND_PORT]` (if applicable)

---

## Development Standards

### Package Management
- **Package Manager**: [PACKAGE_MANAGER]
- **Install package**: `[PACKAGE_MANAGER] install <package>`
- **Install dependencies**: `[BACKEND_INSTALL_CMD]`

### Code Quality
- **Tools**: [CODE_QUALITY_TOOLS]
- **Line Length**: [LINE_LENGTH] characters
- **Linter command**: [LINTER_CMD]
- **Format command**: [FORMAT_CMD]

### Testing
- **Framework**: [TESTING_FRAMEWORK]
- **Coverage Target**: >[COVERAGE_TARGET]%
- **Approach**: Test-Driven Development (TDD)
- **Test Location**: `tests/` directory
- **Run tests**: `[BACKEND_TEST_CMD]` (backend), `[FRONTEND_TEST_CMD]` (frontend)

### Version Control
**Commit Format**: Conventional Commits
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/modifications
- `chore:` - Build/tooling changes

**Branch Naming**: `<prefix>/<ticket-key>-<description>` (prefix examples: `ft/`, `rf/`, `doc/`, `test/`, `conf/`)

**Base Branch**: Always branch from up-to-date `[DEFAULT_BRANCH]`

---

## Project Structure

```
.
├── .claude/              # Claude configuration
│   ├── commands/         # Workflow command definitions
│   └── skills/           # Agent skills
├── backend/              # Backend application (if applicable)
├── frontend/             # Frontend application (if applicable)
├── tests/                # Test files
├── specs/                # Ticket-level specifications (created via /design)
├── plans/                # Implementation plans
├── blueprints/           # Project-level architecture (created via /blueprint)
├── README.md             # Main project documentation
└── AGENTS.md             # This file - agent context
```

---

## Jira Workflow

### Issue Statuses
- **To Do**: Backlog of planned work
- **In Progress**: Actively being worked on
- **In Review**: Implementation complete, awaiting review
- **Done**: Completed and merged

### Ticket Transition Flow
1. `To Do` → `In Progress` (prompted via `/pull-ticket`)
2. Work on ticket using `/spec`, `/plan`, `/implement`
3. Create PR when implementation complete
4. `In Progress` → `In Review` (automated via `/implement`)
5. `In Review` → `Done` (manual after PR approval)

### Priority Levels
- **High** - Highest priority
- **Medium** - Normal priority (default)
- **Low** - Lower priority

### Blocker Detection
- Workflow automatically checks `issuelinks` field for blockers
- Blockers are surfaced as warnings when pulling tickets

---

## Atlassian MCP Integration

### Setup
MCP server configured in `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "atlassian": {
      "type": "sse",
      "url": "https://mcp.atlassian.com/v1/sse"
    }
  }
}
```

### Available Tools
- **Jira**: Search, create, update, transition issues; add comments; manage links
- **Confluence**: Read/write pages, search content, manage spaces
- **Rovo Search**: Unified search across Jira and Confluence

### Authentication
- First use opens browser for Atlassian OAuth authentication
- Credentials cached for future sessions
- Verify connection: `getAccessibleAtlassianResources` tool

---

## Quick Reference

### Common Commands
```bash
# Setup
[BACKEND_INSTALL_CMD]

# Run tests
[BACKEND_TEST_CMD]

# Start backend
[BACKEND_START_CMD]

# Start frontend (if applicable)
[FRONTEND_START_CMD]
```

### Environment Variables
```bash
# Backend configuration
DATABASE_URL=[your database connection string]
API_KEY=[your API keys]
ENV_TYPE=[LOCAL/DEV/PROD]
LOG_LEVEL=[DEBUG/INFO/WARNING/ERROR]
```

---

**Last Updated**: [Auto-generated date]
**Maintained By**: [TEAM_NAME]
**Project Status**: Active Development
