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
        # Compute MAX numerically in SQL. A pure ORDER BY id uses lexical
        # ordering, which gets `DEC-999` > `DEC-1000` and would produce a
        # colliding "next" ID once any type passes 1000 entries.
        prefix = ID_PREFIX[entry_type]
        row = self.conn.execute(
            "SELECT MAX(CAST(SUBSTR(id, INSTR(id, '-') + 1) AS INTEGER)) AS max_num "
            "FROM entries WHERE type = ?",
            (entry_type,),
        ).fetchone()
        max_num = (row["max_num"] if row and row["max_num"] is not None else 0) or 0
        return f"{prefix}-{max_num + 1:04d}"

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
        created_at = utcnow_iso()
        evidence_links = evidence_links or []
        explicit_id = entry_id is not None
        # _next_id + INSERT is a read-then-write race: two concurrent submits
        # can compute the same next ID. Retry with a fresh ID on UNIQUE
        # collision unless the caller pinned the ID explicitly.
        attempts = 1 if explicit_id else 5
        last_err: sqlite3.IntegrityError | None = None
        for _ in range(attempts):
            this_id = entry_id if explicit_id else self._next_id(entry_type)
            try:
                self.conn.execute(
                    """INSERT INTO entries (
                        id, type, title, tags, author, created_at, status,
                        supersedes, superseded_by, last_referenced_at,
                        reference_count, evidence_links, body
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        this_id, entry_type, title, json.dumps(tags), author,
                        created_at, status, supersedes, None, None, 0,
                        json.dumps(evidence_links), json.dumps(body),
                    ),
                )
                self.conn.execute(
                    "INSERT INTO entries_fts(id, title, body, tags) "
                    "VALUES (?, ?, ?, ?)",
                    (this_id, title, json.dumps(body), " ".join(tags)),
                )
                return self.get(this_id)  # type: ignore[return-value]
            except sqlite3.IntegrityError as e:
                last_err = e
                continue
        raise last_err  # type: ignore[misc]

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
        limit: int = 20,
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
        # When there are no Python-side filters, push LIMIT into SQL. With
        # tag filtering we must filter first, then truncate.
        if not tags and limit and limit > 0:
            sql += f" LIMIT {int(limit)}"
        rows = self.conn.execute(sql, params).fetchall()
        entries = [_row_to_entry(r) for r in rows]

        if tags:
            tag_set = {t.lower() for t in tags}
            entries = [
                e for e in entries
                if tag_set & {t.lower() for t in e.tags}
            ]
            if limit and limit > 0:
                entries = entries[:limit]
        return entries

    def list_recent(
        self,
        days: int,
        types: list[str] | None,
        limit: int = 50,
    ) -> list[Entry]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(
            timespec="seconds"
        )
        params: list[Any] = [cutoff]
        sql = "SELECT * FROM entries WHERE created_at >= ?"
        if types:
            sql += f" AND type IN ({','.join('?' * len(types))})"
            params.extend(types)
        sql += " ORDER BY created_at DESC"
        if limit and limit > 0:
            sql += f" LIMIT {int(limit)}"
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
