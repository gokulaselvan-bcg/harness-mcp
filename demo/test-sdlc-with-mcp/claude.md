# CLAUDE.md — SDLC Discipline Contract

This file is auto-loaded by Claude Code. It is the contract for how code is written in this repo. **Read fully before any work.**

This contract governs **HOW** code is written. The MCP server below holds the standards, patterns, and known failures. The skills in `.claude/skills/` provide role personas and language-specific guidance, all of which delegate to MCP for current content. Both this file and MCP are authoritative. When in doubt, MCP wins on specifics; this file wins on procedure.

---

## MCP server

This project has an MCP server holding SDLC standards, design decisions,
failure patterns, and agent personas. Querying it is mandatory.

- Server name (as registered with Claude Code): `sdlc-discipline`
- Transport: stdio (no URL, no auth token — Claude Code spawns the process)
- Launch command: `python -m sdlc_mcp`
- Configured via `.mcp.json` at the project root. If `/mcp` does not list
  `sdlc-discipline`, fix the configuration before doing any work.
- Server unavailable: work stops. Do not proceed without MCP access.
  No fallback. No guessing from memory. Tell the developer.
  
---

## Skills Layer

Skills in `.claude/skills/` auto-activate based on the work being done. They are thin pointers — actual content lives in MCP.

Three categories:

1. **Role skills** (`developer`, `tester`, `architect`, `reviewer`, `debugger`, `refactorer`, `migration-author`, `api-designer`) — activate based on the kind of work happening.
2. **Language skills** (`python-standards`, `java-standards`, `typescript-standards`) — activate based on file extensions.
3. **Concern skills** (added incrementally as the team encounters them) — multi-tenancy, AI orchestration, event messaging, etc.

Multiple skills can activate at once. When writing a Python test in a multi-tenant feature, `tester` + `python-standards` + `multi-tenancy` all apply.

---

## Non-Negotiable Rules

### Before writing code

1. **Query MCP first.** For any non-trivial task (anything beyond a typo or one-line change), run `query()` with relevant tags and search terms. Read returned `decision`, `pattern`, `context`, and `failure` entries before proposing an approach.
2. **Plan before code.** Any change touching more than one file requires a written plan stating: files affected, approach, tests to add, MCP entries consulted. Show the plan and wait for developer approval before editing.
3. **Adopt the relevant role persona.** When a role skill activates, query MCP for the persona's `agent` entry (e.g., `query("tester role persona", types=["agent"])`) and follow it.
4. **Apply language standards.** When touching files in a specific language, query MCP for that language's tagged decisions and patterns (`query("", tags=["python"])`).

### While writing code

5. **Tests first.** Write failing tests before implementation. 100% coverage on business logic. No exceptions without an `exception` entry covering the case.
6. **No hardcoding.** All configuration in files. No magic numbers, no inline credentials, no hardcoded paths.
7. **Type-safe data.** Pydantic in Python, Bean Validation + records in Java, Zod or equivalent in TypeScript. Equivalent typed structures on every boundary.
8. **Lint and format on every save.** Match the repo's configured tooling. Unformatted or lint-failing code is not submittable.
9. **One change per PR — procedural enforcement.**

   **At plan time** (before writing any plan):
   - Count the logically separable units in the request. A unit is anything that could ship and be reviewed on its own (e.g. *DB infra*, *backend feature*, *frontend scaffold*, *frontend feature*, *docs*).
   - If the count is > 1, your plan **must open with this exact question** — verbatim, not paraphrased — and wait for an answer before continuing:
     > *"I count N separable units: [list each one]. Per rule #9 these should be separate PRs. Confirm: bundle on one branch with incremental commits, or structure as stacked PRs?"*
   - You may not proceed to write the rest of the plan until the user has answered.

   **Mid-implementation** (after the plan is approved):
   - If a fix, refactor, or change surfaces that is **not in the approved plan** — even one that feels small or "needed to make the planned work compile/run" — STOP.
   - Your next message must begin with the literal phrase **`SCOPE TRIPWIRE:`** followed by:
     - what surfaced,
     - why you think it needs doing now,
     - and the explicit ask: *bundle into the current commit, split into its own commit on this branch, or open a separate PR?*
   - You may not touch any file related to the surfaced fix until the user has answered.
   - Justifying the bundling to yourself ("it's needed for my tests to run") is the failure mode this rule exists to catch. The rule does not have an "unless it's convenient" clause.

   **Why these specific phrases:** the exact strings *"I count N separable units"* and *"SCOPE TRIPWIRE:"* are machine-greppable in transcripts, so a later audit can detect when the procedure was skipped. Paraphrasing defeats the audit and counts as a violation.

### Gates and review

10. **Stop at gates.** Gates: plan approval, tests passing, lint clean, MCP standards satisfied. Do not proceed past a failing gate. Surface the failure to the developer.
11. **No self-approval.** Code review by another team member required before merge.

### Capturing learnings

12. **Failure capture (SDLC-level only).** When a failure surfaces during work, triage it:
    - **Business-logic / domain-specific** (wrong column, wrong join, miscalculated metric): do **not** prompt, do **not** capture. Fix and move on.
    - **SDLC / infrastructure-level** (library quirks, framework gotchas, concurrency restrictions, deployment surprises, anything another team would also hit): prompt the developer:
        - If the failure relates to an existing `decision` or `pattern`: *"This relates to `<ID>`. Update that entry, or capture as new `failure` linked to it? (update / new / skip)"*
        - Otherwise: *"This looks like a reusable SDLC failure. Capture as `failure`? (y/n)"*
    - Claude drafts via `draft()`. Developer submits via `submit()`. Never autonomous.

13. **All other entry types are tech-lead initiated.** Do not propose new `decision`, `pattern`, `context`, `exception`, or `agent` entries unsolicited. If a developer asks, draft and let them submit.

---

## MCP Usage Cheat Sheet

```
query(search_string, types?, tags?, status_filter?)   # default excludes superseded/deprecated
get(id)                                                # retrieve a specific entry
get_supersession_chain(id)                             # full history of an entry
list_recent(days, types?)                              # what's changed lately
find_related(search_terms, types?)                     # lightweight ID lookup for triage

draft(type, content)                                   # Claude drafts; returns draft_id
submit(draft_id, author)                               # developer submits
supersede(old_id, new_content, reason, author)         # replace an existing entry
deprecate(id, reason, author)                          # retire without replacement
```

**Default task start sequence:**

1. `query(<task keywords>)` — get applicable decisions/patterns
2. Query for active role persona — `query("<role> role persona", types=["agent"])`
3. Query for language tags relevant to files being touched
4. Plan → confirm with developer → code.

---

## Failure Modes Where This Contract Binds Hardest

- "Just this once" hardcoding → no.
- Skipping the failing-test-first step because the change is small → no.
- Proceeding when MCP is down → no.
- Self-approving a PR because the reviewer is slow → no.
- Capturing business-logic bugs in MCP → no, they go in the PR description.
- "It's only in one language so the rule doesn't apply" → no, principles cross languages.
