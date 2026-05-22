"""Storage layer: CRUD over entries, drafts, audit log."""
from __future__ import annotations

import json
import logging
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from .models import ID_PREFIX, Entry, utcnow_iso
from .validation import find_conflicts

log = logging.getLogger(__name__)


def _row_to_entry(row: sqlite3.Row) -> Entry:
    return Entry(
        id=row["id"],
        type=row["type"],
        title=row["title"],
        tags=json.loads(row["tags"]),
        author=row["author"],
        created_at=row["created_at"],
        status=row["status"],
        supersedes=row["supersedes"],
        superseded_by=row["superseded_by"],
        last_referenced_at=row["last_referenced_at"],
        reference_count=row["reference_count"] or 0,
        evidence_links=json.loads(row["evidence_links"]),
        body=json.loads(row["body"]),
    )


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return _row_to_entry(row).model_dump()


class Store:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # -- ID generation ------------------------------------------------------

    def _next_id(self, entry_type: str) -> str:
        prefix = ID_PREFIX[entry_type]
        row = self.conn.execute(
            "SELECT id FROM entries WHERE type = ? ORDER BY id DESC LIMIT 1",
            (entry_type,),
        ).fetchone()
        next_num = 1
        if row is not None:
            try:
                next_num = int(row["id"].split("-", 1)[1]) + 1
            except (IndexError, ValueError):
                next_num = self.conn.execute(
                    "SELECT COUNT(*) FROM entries WHERE type = ?", (entry_type,)
                ).fetchone()[0] + 1
        return f"{prefix}-{next_num:03d}"

    # -- Drafts -------------------------------------------------------------

    def create_draft(self, entry_type: str, content: dict[str, Any]) -> str:
        draft_id = f"DRAFT-{secrets.token_hex(4)}"
        self.conn.execute(
            "INSERT INTO drafts(id, type, content, created_at) VALUES (?, ?, ?, ?)",
            (draft_id, entry_type, json.dumps(content), utcnow_iso()),
        )
        return draft_id

    def get_draft(self, draft_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM drafts WHERE id = ?", (draft_id,)
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "type": row["type"],
            "content": json.loads(row["content"]),
            "created_at": row["created_at"],
        }

    def delete_draft(self, draft_id: str) -> None:
        self.conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))

    # -- Entries ------------------------------------------------------------

    def insert_entry(
        self,
        *,
        entry_type: str,
        title: str,
        tags: list[str],
        author: str,
        body: dict[str, Any],
        evidence_links: list[str] | None = None,
        supersedes: str | None = None,
        status: str = "accepted",
        entry_id: str | None = None,
    ) -> Entry:
        entry_id = entry_id or self._next_id(entry_type)
        created_at = utcnow_iso()
        evidence_links = evidence_links or []
        self.conn.execute(
            """INSERT INTO entries (
                id, type, title, tags, author, created_at, status,
                supersedes, superseded_by, last_referenced_at, reference_count,
                evidence_links, body
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                entry_id,
                entry_type,
                title,
                json.dumps(tags),
                author,
                created_at,
                status,
                supersedes,
                None,
                None,
                0,
                json.dumps(evidence_links),
                json.dumps(body),
            ),
        )
        # FTS row mirrors title/body/tags.
        self.conn.execute(
            "INSERT INTO entries_fts(id, title, body, tags) VALUES (?, ?, ?, ?)",
            (entry_id, title, json.dumps(body), " ".join(tags)),
        )
        return self.get(entry_id)  # type: ignore[return-value]

    def get(self, entry_id: str) -> Entry | None:
        row = self.conn.execute(
            "SELECT * FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()
        return _row_to_entry(row) if row else None

    def get_many(self, ids: Iterable[str]) -> list[Entry]:
        ids = list(ids)
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        rows = self.conn.execute(
            f"SELECT * FROM entries WHERE id IN ({placeholders})", ids
        ).fetchall()
        return [_row_to_entry(r) for r in rows]

    def mark_referenced(self, ids: Iterable[str]) -> None:
        ids = list(ids)
        if not ids:
            return
        now = utcnow_iso()
        self.conn.executemany(
            "UPDATE entries SET last_referenced_at = ?, reference_count = reference_count + 1 WHERE id = ?",
            [(now, eid) for eid in ids],
        )

    # -- Query --------------------------------------------------------------

    def query(
        self,
        search_string: str | None,
        types: list[str] | None,
        tags: list[str] | None,
        status_filter: list[str] | None,
    ) -> list[Entry]:
        where: list[str] = []
        params: list[Any] = []

        if status_filter:
            where.append(f"status IN ({','.join('?' * len(status_filter))})")
            params.extend(status_filter)

        if types:
            where.append(f"type IN ({','.join('?' * len(types))})")
            params.extend(types)

        if search_string and search_string.strip():
            # FTS match; quote the query to handle special chars/spaces safely.
            safe = search_string.replace('"', '""')
            ids = [
                r["id"] for r in self.conn.execute(
                    'SELECT id FROM entries_fts WHERE entries_fts MATCH ?',
                    (f'"{safe}"',),
                ).fetchall()
            ]
            if not ids:
                return []
            where.append(f"id IN ({','.join('?' * len(ids))})")
            params.extend(ids)

        sql = "SELECT * FROM entries"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY created_at DESC"
        rows = self.conn.execute(sql, params).fetchall()
        entries = [_row_to_entry(r) for r in rows]

        if tags:
            tag_set = {t.lower() for t in tags}
            entries = [
                e for e in entries
                if tag_set & {t.lower() for t in e.tags}
            ]
        return entries

    def list_recent(self, days: int, types: list[str] | None) -> list[Entry]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(
            timespec="seconds"
        )
        params: list[Any] = [cutoff]
        sql = "SELECT * FROM entries WHERE created_at >= ?"
        if types:
            sql += f" AND type IN ({','.join('?' * len(types))})"
            params.extend(types)
        sql += " ORDER BY created_at DESC"
        return [_row_to_entry(r) for r in self.conn.execute(sql, params).fetchall()]

    def supersession_chain(self, entry_id: str) -> list[Entry]:
        chain: list[Entry] = []
        current = self.get(entry_id)
        if current is None:
            return chain
        chain.append(current)
        seen = {current.id}
        # Walk backwards via `supersedes`.
        cursor = current.supersedes
        while cursor and cursor not in seen:
            row = self.get(cursor)
            if row is None:
                break
            chain.append(row)
            seen.add(row.id)
            cursor = row.supersedes
        return chain

    # -- Status mutations ---------------------------------------------------

    def set_superseded(self, old_id: str, new_id: str) -> None:
        self.conn.execute(
            "UPDATE entries SET status = 'superseded', superseded_by = ? WHERE id = ?",
            (new_id, old_id),
        )

    def deprecate(self, entry_id: str) -> None:
        self.conn.execute(
            "UPDATE entries SET status = 'deprecated' WHERE id = ?", (entry_id,)
        )

    # -- Conflict detection -------------------------------------------------

    def find_conflicts_for(self, title: str, tags: list[str]) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, title, tags, status FROM entries WHERE status = 'accepted'"
        ).fetchall()
        existing = [
            {
                "id": r["id"],
                "title": r["title"],
                "tags": json.loads(r["tags"]),
                "status": r["status"],
            }
            for r in rows
        ]
        return find_conflicts(title, tags, existing)

    # -- Audit log ----------------------------------------------------------

    def audit(
        self,
        *,
        tool: str,
        entry_id: str | None,
        author: str | None,
        reason: str | None,
    ) -> None:
        self.conn.execute(
            "INSERT INTO audit_log(timestamp, tool, entry_id, author, reason) VALUES (?, ?, ?, ?, ?)",
            (utcnow_iso(), tool, entry_id, author, reason),
        )


# --- Backup -----------------------------------------------------------------

def daily_snapshot(db_path: Path, backup_dir: Path) -> Path:
    """Create a SQLite backup file dated today. Idempotent for a given date."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    target = backup_dir / f"{db_path.stem}-{date_str}.sqlite3"
    src = sqlite3.connect(db_path)
    try:
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    log.info("Snapshot written to %s", target)
    return target
