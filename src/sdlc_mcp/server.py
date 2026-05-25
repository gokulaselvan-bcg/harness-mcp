"""FastMCP server exposing SDLC discipline tools.

Read tools:  query, get, get_supersession_chain, list_recent
Write tools: draft, submit, supersede, deprecate

All write tools record an audit log entry. All tool invocations are
logged with timestamp and caller identity (best-effort from MCP context).
"""
from __future__ import annotations

import logging
import sqlite3
import threading
import time
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import Config
from .db import connect, run_migrations
from .models import DraftIn, parse_body
from .store import Store, daily_snapshot
from .validation import ValidationError, validate_for_submit

log = logging.getLogger("sdlc_mcp")


def _configure_logging(log_path) -> None:
    handler = logging.FileHandler(log_path)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s :: %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Avoid duplicate handlers when reloaded.
    if not any(getattr(h, "baseFilename", None) == handler.baseFilename for h in root.handlers if isinstance(h, logging.FileHandler)):
        root.addHandler(handler)


def _entry_to_dict(entry) -> dict[str, Any]:
    return entry.model_dump()


def build_server(cfg: Config | None = None) -> FastMCP:
    cfg = cfg or Config.from_env()
    _configure_logging(cfg.log_path)
    conn = connect(cfg.db_path)
    applied = run_migrations(conn, cfg.migrations_dir)
    if applied:
        log.info("Applied migrations: %s", applied)
    store = Store(conn)

    mcp = FastMCP(
        name="sdlc-discipline",
        instructions=(
            "Single-project SDLC discipline server. Holds decisions, failure "
            "patterns, structural patterns, codebase context notes, scoped "
            "exceptions, and agent personas. Query before designing; submit "
            "only after explicit human approval in chat.\n\n"
            "Tool selection:\n"
            "  - Searching by topic or keywords?            -> query\n"
            "  - Already have an ID (from a prior query, a cross-reference\n"
            "    like `overrides_id` / `supersedes` / `superseded_by`, an\n"
            "    `evidence_links` entry, or the user)?      -> get\n"
            "  - Tracing an entry's full history?           -> get_supersession_chain\n"
            "  - Catching up on what was added lately?      -> list_recent\n\n"
            "Prefer `get` over re-querying for a known ID: it is cheaper, "
            "is a point lookup, and returns the entry regardless of status. "
            "When an entry's body references another entry by ID (notably "
            "`exception.overrides_id`), follow the link with `get`."
        ),
    )

    def _log_call(tool: str, **fields: Any) -> None:
        log.info(
            "tool=%s %s",
            tool,
            " ".join(f"{k}={v!r}" for k, v in fields.items()),
        )

    # --- Read tools --------------------------------------------------------

    @mcp.tool(description=(
        "Full-text search over title + body. Filter by entry types and tags. "
        "By default only `accepted` entries are returned. Each returned entry "
        "has its reference count and last-referenced timestamp updated. "
        "For revisiting an entry whose ID you already have, prefer `get(id)` "
        "-- it is cheaper and returns superseded/deprecated entries that "
        "`query` filters out."
    ))
    def query(
        search_string: str = "",
        types: list[str] | None = None,
        tags: list[str] | None = None,
        status_filter: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        _log_call("query", search=search_string, types=types, tags=tags, status=status_filter)
        statuses = status_filter or ["accepted"]
        results = store.query(search_string, types, tags, statuses)
        store.mark_referenced([e.id for e in results])
        return [_entry_to_dict(e) for e in results]

    @mcp.tool(description=(
        "Fetch a single entry by its ID. Use this when you already have an "
        "ID in hand -- from a prior query result, from an entry's "
        "`supersedes` / `superseded_by` / `overrides_id` field, from an "
        "`evidence_links` entry, or from the user. Cheaper than re-running "
        "query and returns the entry even if it has been superseded or "
        "deprecated."
    ))
    def get(id: str) -> dict[str, Any] | None:
        _log_call("get", id=id)
        e = store.get(id)
        if e is None:
            return None
        store.mark_referenced([e.id])
        return _entry_to_dict(e)

    @mcp.tool(description=(
        "Return the supersession chain rooted at the given entry, walking "
        "backwards through every predecessor it replaces. Most-recent first."
    ))
    def get_supersession_chain(id: str) -> list[dict[str, Any]]:
        _log_call("get_supersession_chain", id=id)
        chain = store.supersession_chain(id)
        store.mark_referenced([e.id for e in chain])
        return [_entry_to_dict(e) for e in chain]

    @mcp.tool(description=(
        "List entries created within the last N days, optionally filtered "
        "by entry types."
    ))
    def list_recent(days: int = 14, types: list[str] | None = None) -> list[dict[str, Any]]:
        _log_call("list_recent", days=days, types=types)
        results = store.list_recent(days, types)
        return [_entry_to_dict(e) for e in results]

    # --- Write tools -------------------------------------------------------

    @mcp.tool(description=(
        "Stage a candidate entry as a draft. The draft is NOT yet canonical "
        "and will not be returned by query/get. Call submit() to promote. "
        "`content` must contain: title (str), tags (list[str]), body (dict "
        "matching the type), optional evidence_links and supersedes."
    ))
    def draft(type: str, content: dict[str, Any]) -> dict[str, Any]:
        _log_call("draft", type=type)
        try:
            DraftIn(**content)  # surface obvious shape errors early
            parse_body(type, content.get("body", {}))
        except Exception as e:
            raise ValueError(f"Invalid draft content: {e}") from e
        draft_id = store.create_draft(type, content)
        store.audit(tool="draft", entry_id=draft_id, author=None, reason=None)
        return {"draft_id": draft_id, "type": type}

    @mcp.tool(description=(
        "Promote a draft to status `accepted`. Generates the formal ID, "
        "runs strict validation, records an audit entry, and returns the new "
        "canonical entry. The response also surfaces any potentially "
        "conflicting existing entries (overlapping tags + similar title)."
    ))
    def submit(draft_id: str, author: str) -> dict[str, Any]:
        _log_call("submit", draft_id=draft_id, author=author)
        d = store.get_draft(draft_id)
        if d is None:
            raise ValueError(f"Draft not found: {draft_id}")
        draft_in = DraftIn(**d["content"])
        try:
            validate_for_submit(d["type"], draft_in)
        except ValidationError as e:
            raise ValueError(str(e)) from e
        conflicts = store.find_conflicts_for(draft_in.title, draft_in.tags)
        entry = store.insert_entry(
            entry_type=d["type"],
            title=draft_in.title,
            tags=draft_in.tags,
            author=author,
            body=draft_in.body,
            evidence_links=draft_in.evidence_links,
            supersedes=draft_in.supersedes,
            status="accepted",
        )
        # If submit declares supersession, close the loop on the old entry.
        if draft_in.supersedes:
            store.set_superseded(draft_in.supersedes, entry.id)
        store.delete_draft(draft_id)
        store.audit(tool="submit", entry_id=entry.id, author=author, reason=None)
        return {"entry": _entry_to_dict(entry), "conflicts": conflicts}

    @mcp.tool(description=(
        "Atomically supersede an existing entry. Validates the new content, "
        "creates a new accepted entry that points back at the old one, marks "
        "the old entry as `superseded` and sets its `superseded_by` link. "
        "`new_content` shape matches draft content (title, tags, body, "
        "optional evidence_links). `reason` is recorded in the audit log."
    ))
    def supersede(
        old_id: str,
        new_content: dict[str, Any],
        reason: str,
        author: str,
    ) -> dict[str, Any]:
        _log_call("supersede", old_id=old_id, author=author)
        old = store.get(old_id)
        if old is None:
            raise ValueError(f"Entry not found: {old_id}")
        draft_in = DraftIn(**{**new_content, "supersedes": old_id})
        try:
            validate_for_submit(old.type, draft_in)
        except ValidationError as e:
            raise ValueError(str(e)) from e

        conflicts = store.find_conflicts_for(draft_in.title, draft_in.tags)
        try:
            store.conn.execute("BEGIN")
            new_entry = store.insert_entry(
                entry_type=old.type,
                title=draft_in.title,
                tags=draft_in.tags,
                author=author,
                body=draft_in.body,
                evidence_links=draft_in.evidence_links,
                supersedes=old_id,
                status="accepted",
            )
            store.set_superseded(old_id, new_entry.id)
            store.conn.execute("COMMIT")
        except sqlite3.Error:
            store.conn.execute("ROLLBACK")
            raise
        store.audit(tool="supersede", entry_id=new_entry.id, author=author, reason=reason)
        store.audit(tool="supersede.old", entry_id=old_id, author=author, reason=reason)
        return {"new_entry": _entry_to_dict(new_entry), "conflicts": conflicts}

    @mcp.tool(description=(
        "Mark an entry as `deprecated`. The reason is recorded in the audit "
        "log. Deprecated entries are excluded from default query results."
    ))
    def deprecate(id: str, reason: str, author: str) -> dict[str, Any]:
        _log_call("deprecate", id=id, author=author)
        entry = store.get(id)
        if entry is None:
            raise ValueError(f"Entry not found: {id}")
        store.deprecate(id)
        store.audit(tool="deprecate", entry_id=id, author=author, reason=reason)
        return {"id": id, "status": "deprecated"}

    # Kick off daily snapshot loop in a background thread. Idempotent per day.
    _start_snapshot_thread(cfg)
    return mcp


# --- Daily snapshot scheduler ----------------------------------------------

def _start_snapshot_thread(cfg: Config) -> None:
    def loop() -> None:
        last_snapshot_date: str | None = None
        while True:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if today != last_snapshot_date:
                try:
                    daily_snapshot(cfg.db_path, cfg.backup_dir)
                    last_snapshot_date = today
                except Exception:
                    log.exception("Daily snapshot failed")
            time.sleep(3600)  # check hourly

    t = threading.Thread(target=loop, name="sdlc-snapshot", daemon=True)
    t.start()
