# SDLC Discipline MCP Server

## What is this?

An [MCP](https://modelcontextprotocol.io/) server that gives any MCP-capable AI assistant — Claude Code, Claude Desktop, Cursor, Continue, Cody, custom clients — a persistent memory of **how this project builds software**: design decisions, failure patterns, structural patterns, codebase context, scoped exceptions, and agent personas. The assistant queries it before designing or coding so the same rules apply to every change — including changes made by new contributors, new agents, or after long gaps between sessions.

**The problem it solves.** Without a shared standards memory, every AI-assisted coding session re-invents conventions, re-litigates settled debates, and re-discovers failures you already paid for. Static rule files (`CLAUDE.md`, `.cursorrules`, system prompts) help but don't scale past a page or two, can't be queried by tags, and don't record *why* a decision was made or what was rejected. This server holds that institutional memory in a queryable form.

**Scope.** One project per server (no multi-tenancy). SDLC content only — no business logic, no domain data. When the server is unreachable, the consuming assistant is expected to stop work; there's no fallback cache by design.

## How developers use it

Day-to-day, you barely touch the server directly — the assistant does. The mental model:

| When you… | The assistant calls… | You do… |
| --- | --- | --- |
| Start a new feature or refactor | `query` + `get_supersession_chain` | Nothing. The assistant pulls relevant decisions/patterns before designing. |
| Hit a sharp edge worth recording | `draft` then asks for approval | **Approve or reject in chat.** On approval the assistant calls `submit`. |
| Settle a debate that overturns an old decision | `supersede` (after approval) | Review the new content and reason in chat before approving. |
| Retire something with no replacement | `deprecate` | Approve and provide the reason. |
| Catch up after time away | `list_recent(days=14)` | Skim what's been added. |

The discipline is: **writes happen only after explicit human approval in chat.** The assistant never silently records a "lesson learned" — every entry has an author and an audit log line tying it to a real conversation. Reads are free and automatic.

A typical session looks like:

1. You ask the assistant to implement something. It `query`s for the relevant standards/patterns first, frames the proposal accordingly, and shows you what it found.
2. If the work surfaces a new decision (e.g. "we'll use library X over Y") or a new failure pattern (e.g. "this is the third time the cache stampede bit us"), the assistant proposes a draft.
3. You either approve, edit, or reject. Approved drafts get submitted with you as the author.
4. Old decisions get superseded (not edited in place) so the supersession chain stays auditable.

## Entry model

Every entry shares the same metadata envelope:

| field | notes |
| --- | --- |
| `id` | auto-generated, immutable. `DEC-001`, `FAIL-001`, `PAT-001`, `CTX-001`, `EXC-001`, `AGT-001`. |
| `type` | `decision` \| `failure` \| `pattern` \| `context` \| `exception` \| `agent` |
| `title`, `tags`, `author`, `created_at`, `status` | self-explanatory |
| `status` | `proposed` \| `accepted` \| `superseded` \| `deprecated` |
| `supersedes`, `superseded_by` | link the supersession chain |
| `last_referenced_at`, `reference_count` | auto-updated whenever a query returns the entry |
| `evidence_links` | URLs (PRs, commits, tests, runbooks) |
| `body` | type-specific shape, see below |

Type-specific bodies:

- **decision** — `{rule, reasoning, alternatives_considered}` (all three are required and must be non-empty)
- **failure** — `{symptom, root_cause, detection, prevention}`
- **pattern** — `{use_case, structure, when_to_apply, when_not_to_apply}`
- **context** — `{area, content}`
- **exception** — `{overrides_id, scope, reason}`
- **agent** — `{role, prompt, applies_to}`

## MCP tools

**Read** (safe; updates reference counters):

- `query(search_string, types?, tags?, status_filter?)` — full-text search over title + body. Default filter returns only `accepted` entries.
- `get(id)` — fetch by ID, regardless of status.
- `get_supersession_chain(id)` — entry plus the full chain of predecessors it replaced.
- `list_recent(days, types?)` — entries created in the last N days.

**Write** (intended to be called only after explicit human approval in the developer's chat session):

- `draft(type, content)` — stage a candidate. Returns a `draft_id`. The draft is not visible to read tools yet.
- `submit(draft_id, author)` — promote a draft to `accepted`. Runs strict validation. Includes any conflict warnings (overlapping tags + similar title) in the response — informational, not blocking.
- `supersede(old_id, new_content, reason, author)` — atomic: validates new content, creates a new accepted entry, marks the old one `superseded` and links them both ways.
- `deprecate(id, reason, author)` — marks an entry `deprecated`. Reason goes to the audit log.

Every write call is recorded in the `audit_log` table. Every read and write call is logged to disk with the calling tool's identity.

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Run the server

The server speaks MCP over stdio (the standard transport used by Claude Code, Claude Desktop, Cursor, Continue, and most other MCP clients):

```bash
sdlc-mcp
# or
python -m sdlc_mcp
```

It will:

1. Connect to (or create) the SQLite database.
2. Apply any pending migrations from `migrations/`.
3. Start a background thread that takes one snapshot of the database per day into the backup directory.
4. Open the MCP stdio transport.

### Configuration

All paths are configurable via environment variables:

| env var | default | purpose |
| --- | --- | --- |
| `SDLC_MCP_DB` | `./data/harness.db` | SQLite database file |
| `SDLC_MCP_BACKUP_DIR` | `./backups` | Daily snapshot destination |
| `SDLC_MCP_LOG` | `./sdlc_mcp.log` | Tool-call log file |
| `SDLC_MCP_MIGRATIONS` | `<repo>/migrations` | Migrations directory |

## Point your MCP client at the server

Configuration shape varies by client, but every MCP-capable client needs the same three things: a name for the server, the command to launch it (`sdlc-mcp`), and any env vars you want to override.

**Claude Code / Claude Desktop** — add to `.mcp.json` (project-scoped) or `~/.claude.json` (user-scoped):

```json
{
  "mcpServers": {
    "sdlc-discipline": {
      "command": "sdlc-mcp",
      "env": {
        "SDLC_MCP_DB": "/abs/path/to/project/data/harness.db",
        "SDLC_MCP_BACKUP_DIR": "/abs/path/to/project/backups",
        "SDLC_MCP_LOG": "/abs/path/to/project/sdlc_mcp.log"
      }
    }
  }
}
```

**Cursor** — add to `~/.cursor/mcp.json` (or the project's `.cursor/mcp.json`) using the same `mcpServers` shape.

**Continue, Cody, custom clients** — follow each client's MCP server registration docs; the launch command and env vars are identical.

After registering, restart the client. Verify the tools appear (in Claude clients: `/mcp`; in others: the equivalent server-list view). Each tool is described inline so the assistant can decide when to call it.

## Seed a fresh database

The seed is **YAML-driven**. There is no hardcoded seed content — `seed.py` reads a YAML file and turns each entry into a database insert.

### Two files, one workflow

- [seed.example.yaml](seed.example.yaml) — schema reference. A filled multi-stack example documenting every entry type and body shape. **Do not edit for your project.**
- `seed.yaml` — this project's canonical seed. Tracked in git (it's project-specific, not user-specific). **Must be named exactly `seed.yaml`** at the repo root.

Why `seed.yaml` specifically:

- It's the project's single source of truth for what gets loaded into the DB on a fresh setup — one canonical name, one canonical file.
- The seed script invocations in this README, in [harness-questionnaire.md](harness-questionnaire.md), and in the example file's header all assume `seed.yaml` for the real file. Diverge and the docs lie.
- Keeps the schema reference (`seed.example.yaml`) cleanly separated from this project's actual content (`seed.yaml`).

### Producing your seed.yaml

1. Open [harness-questionnaire.md](harness-questionnaire.md) and answer every section with your tech lead. "We haven't decided yet" is valid — it becomes a `proposed` entry instead of `accepted`.
2. Hand the completed questionnaire to an AI assistant with the prompt:
   > Generate `seed.yaml` from this questionnaire, following the structure of `seed.example.yaml`.
3. Review the generated `seed.yaml` and commit any corrections — to the file, not to git.

### Loading it

```bash
python seed.py --input seed.yaml --db data/harness.db
```

What the script does:

1. Parses `seed.yaml`.
2. Validates every entry up-front. Decisions require non-empty `rule`, `reasoning`, and `alternatives_considered`. All entries require at least one tag. Body shapes must match the type.
3. **On any failure**: aborts with `ERROR: seed aborted — Entry #N (title=...): validation failed — ...`. Fix the offending entry and rerun.
4. **On success**: inserts every entry in order, prints a JSON summary, and a line like `Loaded 66 entries`.

The loader is idempotent on `(type, title)`: re-running against the same database skips entries that already exist by those keys. Add or supersede entries with the MCP `draft`/`submit`/`supersede` tools, not by editing existing entries in YAML.

`sdlc-mcp-seed --input seed.yaml --db data/harness.db` is the equivalent console script when the package is installed.

## Back up the database

A daily snapshot is taken automatically once the server is running. The file is named `<dbstem>-YYYY-MM-DD.sqlite3` and lives in `SDLC_MCP_BACKUP_DIR`. Point your existing git-watched backup process at that directory.

A manual snapshot is also available:

```bash
python -c "from sdlc_mcp.config import Config; from sdlc_mcp.store import daily_snapshot; cfg=Config.from_env(); print(daily_snapshot(cfg.db_path, cfg.backup_dir))"
```

## Add a new role agent

A role agent is just an `agent` entry. Submit one through any MCP client like any other entry:

1. Ask the assistant to draft an agent entry. Body needs `role`, `prompt`, `applies_to`.
2. Review the draft in chat. Approve it explicitly.
3. The assistant calls `submit(draft_id, author=<your name>)`.
4. The server validates and returns the new `AGT-NNN` ID.

To add one directly (e.g. during bootstrap), append to `AGENT_ENTRIES` in [src/sdlc_mcp/seed.py](src/sdlc_mcp/seed.py) and rerun `sdlc-mcp-seed`. The seed skips duplicates so this is safe on an existing database.

## Smoke test

```bash
python -m tests.smoke_test
```

Creates a temp database, seeds it, then exercises every read and write tool plus the snapshot path. Exits non-zero on any assertion failure. Use it before declaring a change ready.

## Repository layout

From the repo root:

```text
src/sdlc_mcp/          # The MCP server itself
tests/                 # Smoke test for the server
migrations/            # SQL schema
data/                  # Runtime SQLite DB (gitkeeped, contents ignored)
backups/               # Daily DB snapshots (gitignored)
.claude/skills/        # Starter skills for projects that CONSUME this server
seed.example.yaml      # Schema reference (committed)
seed.yaml              # This project's canonical seed (committed once produced)
harness-questionnaire.md   # Template for capturing a project's SDLC standards
seed.py                # CLI entry: load a seed YAML into the DB
pyproject.toml         # Package metadata + console scripts
README.md
```

### Folders

| Path | What's in it | Why it's there |
| --- | --- | --- |
| [src/sdlc_mcp/](src/sdlc_mcp/) | `server.py` (FastMCP tools), `store.py` (SQLite + FTS5 + audit + snapshot), `models.py` (Pydantic shapes), `validation.py` (submit-time rules), `db.py` (connect + migrate), `seed.py` (YAML loader), `config.py` (env-driven paths) | The server's source code. |
| [tests/](tests/) | `smoke_test.py` | End-to-end exercise of every tool. |
| [migrations/](migrations/) | `001_initial.sql` and any future migrations | Applied in lexical order on server startup. |
| [data/](data/) | `harness.db` + WAL/SHM at runtime | Default location for the live SQLite database (override with `SDLC_MCP_DB`). |
| [backups/](backups/) | `harness-YYYY-MM-DD.sqlite3` files | Daily snapshots written by the background thread. |
| [.claude/skills/](.claude/skills/) | `developer/`, `reviewer/`, `tester/`, `debugger/`, `architect/`, `refactorer/`, `api-designer/`, `migration-author/`, plus `*-standards/` skills | **See below.** |

### What `.claude/skills/` is (and isn't)

These are **role skills for the projects that consume this MCP server** — not skills used to develop the harness-mcp server itself. Each skill (e.g. `developer`, `reviewer`, `debugger`) tells a consumer's AI assistant how to act in that role: *query MCP first, cite entry IDs, fail-test-then-implementation, stop if MCP is unreachable, etc.*

The intent is **copy-paste**: drop the folder into your own project's `.claude/skills/` (or the equivalent skill directory for your client) so the assistant working in that project picks up the discipline immediately. The skills are deliberately generic — they reference MCP queries by tag, not by hardcoded content, so they keep working as your `seed.yaml` evolves.

You *can* also use them while developing harness-mcp itself (e.g. when adding a new tool or migration), but that's a secondary use. The primary value is bootstrapping the consumer side of the contract.

## Out of scope (v1)

- No CI integration.
- No web UI.
- No automatic learning capture. Every write requires an explicit human-initiated tool call.
- No business logic, no domain rules, no product-specific data. SDLC content only.
- No cross-server federation. This server is self-contained.
