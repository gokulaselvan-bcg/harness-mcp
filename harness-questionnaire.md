GraphQL# Harness Seed Questionnaire

**Purpose:** Capture the SDLC standards for this project in a structured form. Claude generates `seed.yaml` from your answers. You review, edit, and run the seed script.

**Time required:** ~3-4 hours with the tech lead. Best done in one sitting.

**Scope reminder:** This questionnaire is for **SDLC discipline only** — how code is written, tested, reviewed, deployed. Business logic, domain rules, and product requirements go elsewhere (BRD, PRD, Confluence).

**How to use:**

1. Answer every question. "We haven't decided yet" is a valid answer — it becomes a `proposed` entry instead of `accepted`.
2. For each numbered question, the bracketed `[TYPE: TAGS]` shows what kind of MCP entry it becomes.
3. Skip questions marked `OPTIONAL` if not relevant.
4. At the end, hand to Claude with: "Generate seed.yaml from this."

---

## Section A: Tech Stack & Versions

A1. **Primary language(s) and exact versions?** (e.g., Python 3.11.7, Node 20.11.0)
[DECISION: tech-stack, language]

A2. **Backend framework(s) and version?** (e.g., FastAPI 0.110, Spring Boot 3.2)
[DECISION: tech-stack, framework, backend]

A3. **Frontend framework(s) and version, if applicable?**
[DECISION: tech-stack, framework, frontend]

A4. **Database(s) — primary, cache, search, analytics?** Include versions.
[DECISION: tech-stack, database]

A5. **Message broker / event bus, if any?**
[DECISION: tech-stack, messaging]

A6. **ORM / data access layer?**
[DECISION: tech-stack, data-access]

A7. **Approved library list — any libraries pre-approved or pre-banned?** (e.g., "use httpx not requests"; "no left-pad-style micro-deps")
[DECISION: dependencies, libraries]

A8. **Package manager and lockfile policy?** (e.g., "uv with uv.lock committed"; "npm with package-lock.json committed, no yarn")
[DECISION: dependencies, package-manager]

---

## Section B: Code Structure & Organization

B1. **Directory structure standard for a service?** (Provide the canonical layout.)
[PATTERN: code-organization, structure]

B2. **Module boundaries — what determines a module split?** (e.g., "one module per bounded context"; "max 500 lines per file")
[DECISION: code-organization, modules]

B3. **Naming conventions — files, classes, functions, constants, DB columns?**
[DECISION: code-standards, naming]

B4. **Where do shared utilities live?** (e.g., "`/common` package; nothing app-specific allowed")
[PATTERN: code-organization, shared-code]

---

## Section C: Type Safety & Data Handling

C1. **Type safety stance?** (e.g., "Pydantic v2 models for all I/O boundaries"; "mypy strict mode")
[DECISION: type-safety, data-validation]

C2. **Raw dicts allowed anywhere?** If yes, where; if no, what's the replacement pattern?
[DECISION: type-safety, data-validation]

C3. **DTO / domain model separation policy?**
[PATTERN: data-modeling, type-safety]

C4. **Date/time handling — UTC everywhere? Timezone-aware always?**
[DECISION: data-handling, datetime]

---

## Section D: Configuration & Secrets

D1. **Configuration storage?** (env vars, YAML, TOML, hybrid)
[DECISION: config, environment]

D2. **Configuration access pattern?** (e.g., "single `Settings` class via Pydantic Settings; no `os.getenv` in app code")
[PATTERN: config, environment]

D3. **Hardcoding policy — what counts as hardcoding, what doesn't?**
[DECISION: config, no-hardcoding]

D4. **Secrets storage?** (Vault, AWS Secrets Manager, env-only, .env file gitignored)
[DECISION: secrets, security]

D5. **Secrets in repo — what happens if a secret is committed?**
[CONTEXT: secrets, incident-response]

---

## Section E: Testing

E1. **Test framework(s)?**
[DECISION: testing, framework]

E2. **Test pyramid target — unit / integration / E2E ratio?**
[DECISION: testing, strategy]

E3. **Coverage target and exemptions?** (e.g., "100% on business logic; UI glue exempt; migrations exempt")
[DECISION: testing, coverage]

E4. **Tests-first policy — strictly TDD, or tests-before-merge?**
[DECISION: testing, workflow]

E5. **Mocking policy — what may be mocked, what must be real?**
[DECISION: testing, mocking]

E6. **Test data — fixtures, factories, snapshots?**
[PATTERN: testing, test-data]

E7. **Performance test approach?** OPTIONAL
[DECISION: testing, performance]

---

## Section F: Async, Concurrency, Error Handling

F1. **Async stance?** (e.g., "async-first in Python; sync only for CPU-bound")
[DECISION: async, concurrency]

F2. **Threading / multiprocessing policy?**
[DECISION: concurrency, threading]

F3. **Error handling pattern?** (exceptions vs result types, where to catch, where to bubble)
[PATTERN: error-handling]

F4. **Custom exception hierarchy — required, banned, optional?**
[DECISION: error-handling, exceptions]

F5. **Retry / backoff policy for external calls?**
[PATTERN: resilience, retries]

F6. **Timeout policy — every external call must have one?**
[DECISION: resilience, timeouts]

---

## Section G: Logging, Observability

G1. **Logging library and format?** (e.g., "structlog, JSON output to stdout")
[DECISION: logging, observability]

G2. **Log levels — when to use each?**
[CONTEXT: logging, observability]

G3. **PII redaction in logs — what gets redacted, how enforced?**
[DECISION: logging, security, pii]

G4. **Correlation ID propagation pattern?**
[PATTERN: logging, tracing]

G5. **Metrics — what every service must expose?** (e.g., RED metrics, health endpoint)
[DECISION: observability, metrics]

G6. **Tracing — OpenTelemetry? Sampling rate?**
[DECISION: observability, tracing]

---

## Section H: Linting, Formatting, Pre-commit

H1. **Linter(s) and config location?**
[DECISION: code-standards, linting]

H2. **Formatter(s) and config?**
[DECISION: code-standards, formatting]

H3. **Type checker config?** (strict / non-strict, ignore patterns)
[DECISION: code-standards, type-checking]

H4. **Pre-commit hooks — what runs?**
[DECISION: pre-commit, workflow]

H5. **Pre-commit bypass policy — when, if ever, is `--no-verify` acceptable?**
[DECISION: pre-commit, discipline]

---

## Section I: Git & PR Workflow

I1. **Branching strategy?** (trunk-based, GitFlow, GitHub Flow)
[DECISION: git, workflow]

I2. **Branch naming convention?**
[DECISION: git, naming]

I3. **Commit message convention?** (Conventional Commits, freeform with prefix, etc.)
[DECISION: git, commit-messages]

I4. **One change per PR — what does "one change" mean operationally?**
[CONTEXT: git, pr-discipline]

I5. **PR description requirements — what must every PR include?**
[DECISION: git, pr-template]

I6. **PR review policy — how many approvers, who can self-merge?**
[DECISION: git, code-review]

I7. **Merge strategy — squash, rebase, merge commit?**
[DECISION: git, merge-strategy]

I8. **CODEOWNERS strategy — who owns what paths?**
[CONTEXT: git, ownership]

---

## Section J: Environment & Local Setup

J1. **Local dev environment — Docker, devcontainer, native?**
[DECISION: environment, local-dev]

J2. **Virtual environment / isolation tool?** (uv, venv, conda, nvm)
[DECISION: environment, isolation]

J3. **Per-project IDE config — committed or gitignored?** (.vscode, .idea)
[DECISION: ide, workflow]

J4. **Standard IDE — required, recommended, or developer choice?**
[DECISION: ide, tooling]

J5. **AI coding assistant — Claude Code, Copilot, Cursor — approved and how used?**
[DECISION: ai-tools, workflow]

J6. **Onboarding setup — single script, document, or both?**
[CONTEXT: onboarding, environment]

---

## Section K: CI/CD

K1. **CI platform?**
[DECISION: ci-cd, platform]

K2. **Pipeline stages — exact sequence?**
[PATTERN: ci-cd, pipeline]

K3. **What blocks a merge?** (failing tests, coverage drop, lint, security scan)
[DECISION: ci-cd, gates]

K4. **What blocks a deploy?**
[DECISION: ci-cd, deployment-gates]

K5. **Deployment strategy?** (blue-green, canary, rolling)
[DECISION: deployment, strategy]

K6. **Rollback procedure — who, how, time-to-rollback target?**
[CONTEXT: deployment, rollback]

---

## Section L: API & Data Contracts

L1. **API style — REST, gRPC, GraphQL, mixed?**
[DECISION: api, style]

L2. **API versioning strategy?**
[DECISION: api, versioning]

L3. **OpenAPI / Protobuf source-of-truth — handwritten or generated?**
[DECISION: api, contracts]

L4. **Breaking change policy — how communicated, what notice period?**
[DECISION: api, compatibility]

L5. **Request/response validation — where it lives?**
[PATTERN: api, validation]

---

## Section M: Database & Migrations

M1. **Migration tool?**
[DECISION: database, migrations]

M2. **Migration policy — forward-only or reversible?**
[DECISION: database, migrations]

M3. **Migration review — does every migration need an extra approver?**
[DECISION: database, code-review]

M4. **Destructive migration handling — dropping columns/tables?**
[CONTEXT: database, safety]

M5. **Local dev DB — shared, per-developer, ephemeral?**
[DECISION: database, local-dev]

---

## Section N: Security Baseline

N1. **Auth model for services?** (JWT, OAuth, mTLS, API keys)
[DECISION: security, auth]

N2. **Authorization model?** (RBAC, ABAC, custom)
[DECISION: security, authz]

N3. **Input validation policy — where, how?**
[PATTERN: security, validation]

N4. **Dependency scanning — tool and cadence?**
[DECISION: security, dependencies]

N5. **SAST tool?**
[DECISION: security, sast]

N6. **Vulnerability patch SLA by severity?**
[DECISION: security, patching]

N7. **PII handling — fields catalogued? Masking in non-prod?**
[DECISION: security, pii]

---

## Section O: Performance & Resource Use

O1. **Performance budget — any hard latency / memory targets per request?** OPTIONAL
[DECISION: performance, budget]

O2. **N+1 query policy — how detected and prevented?**
[PATTERN: performance, database]

O3. **Caching strategy — what's cached, where, how invalidated?**
[PATTERN: performance, caching]

O4. **Resource cleanup — context managers, defer/finally requirements?**
[DECISION: performance, resources]

---

## Section P: Documentation

P1. **Docstring format?** (Google, NumPy, JSDoc, freeform)
[DECISION: docs, code-comments]

P2. **README expectations per service — what sections required?**
[PATTERN: docs, readme]

P3. **ADR (Architecture Decision Record) location and template?**
[DECISION: docs, adr]

P4. **API documentation — auto-generated or handwritten?**
[DECISION: docs, api]

---

## Section Q: Role Agents

For each role below, articulate the persona prompt — how Claude should behave when adopting this role. Include: what they prioritize, what they push back on, what they refuse to do.

Q1. **test-writer** — Claude when writing tests. What's their stance on coverage, mocking, test naming?
[AGENT: role, testing]

Q2. **reviewer** — Claude when reviewing a PR or diff. What do they look for, what do they reject, what's their tone?
[AGENT: role, code-review]

Q3. **migration-author** — Claude when writing a DB migration. What's their stance on reversibility, destructive ops, locking?
[AGENT: role, database]

Q4. **debugger** — Claude when diagnosing a failure. What's their method, what evidence do they require before proposing a fix?
[AGENT: role, debugging]

Q5. **refactorer** — Claude when restructuring existing code. What's their stance on behavior preservation, test coverage prereqs, scope creep?
[AGENT: role, refactoring]

Q6. **api-designer** — Claude when designing a new endpoint or contract. What's their stance on versioning, naming, idempotency?
[AGENT: role, api-design]

---

## Section R: Boundary & Exception Policy

R1. **SDLC vs business-logic boundary — articulate it.** This is the single most important context entry. Used by Claude to decide whether a failure goes into MCP or stays in the PR description.
[CONTEXT: harness-discipline, scope]

R2. **What is the standing exception policy?** When can a developer legitimately ask for an exception, and what's the process?
[CONTEXT: exceptions, process]

R3. **Are there known standing exceptions on Day 1?** (e.g., "test coverage exemption for `/scripts/`")
[EXCEPTION: as applicable]

---

## Section S: Harness Usage Discipline

S1. **When must Claude query MCP?** (Restate from CLAUDE.md so it's discoverable in the MCP too.)
[CONTEXT: harness-discipline, usage]

S2. **When must a developer review and submit a Claude-drafted entry?** (Same.)
[CONTEXT: harness-discipline, capture-flow]

S3. **Who owns MCP entry quality?** (Tech lead? Rotating? Each author?)
[CONTEXT: harness-discipline, ownership]

S4. **Supersession criteria — when is an entry superseded vs amended vs deprecated?**
[CONTEXT: harness-discipline, lifecycle]

---

## After You Finish

1. Hand this completed questionnaire to Claude with: *"Generate seed.yaml from this questionnaire per the template structure."*
2. Claude produces `seed.yaml`.
3. Review every entry. Edit anything that doesn't match your intent.
4. Run: `python seed.py --input seed.yaml --db data/harness.db`
5. Verify count: should be 60-80 entries spread across the six types.
6. Smoke check: `query("testing")`, `query("git")`, `get("AGT-001")` should all return sensible content.

If the seed script aborts with a validation error, fix the named entry and re-run. The script does not partial-load.
