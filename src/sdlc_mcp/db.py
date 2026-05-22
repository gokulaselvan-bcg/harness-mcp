"""SQLite connection helper and migration runner."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def _applied_versions(conn: sqlite3.Connection) -> set[int]:
    try:
        rows = conn.execute("SELECT version FROM schema_version").fetchall()
    except sqlite3.OperationalError:
        return set()
    return {r[0] for r in rows}


def run_migrations(conn: sqlite3.Connection, migrations_dir: Path) -> list[int]:
    """Apply any pending .sql files from migrations_dir, ordered by numeric prefix.

    Returns list of versions newly applied.
    """
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory missing: {migrations_dir}")

    files = sorted(migrations_dir.glob("*.sql"))
    applied: list[int] = []
    existing = _applied_versions(conn)

    for f in files:
        try:
            version = int(f.name.split("_", 1)[0])
        except ValueError:
            log.warning("Skipping migration with non-numeric prefix: %s", f.name)
            continue
        if version in existing:
            continue
        log.info("Applying migration %s", f.name)
        sql = f.read_text(encoding="utf-8")
        conn.executescript("BEGIN;\n" + sql + "\nCOMMIT;")
        conn.execute(
            "INSERT OR REPLACE INTO schema_version(version, applied_at) VALUES (?, ?)",
            (version, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        applied.append(version)
    return applied
