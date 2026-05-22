"""YAML-driven seed loader.

The seed has NO hardcoded content. It reads a YAML file describing entries and
converts each one into a database insert. Validation runs per-entry; the load
aborts with a clear error pointing at the offending entry if anything is wrong.

YAML schema (top-level is a list, or a dict with key `entries: [...]`):

    entries:
      - type: decision           # one of: decision, failure, pattern, context, exception, agent
        title: "..."
        tags: [..., ...]         # at least one
        author: "seed"           # optional; defaults to `--author` arg or "seed"
        status: accepted         # optional; defaults to "accepted"
        evidence_links: [..]     # optional
        body:
          # shape depends on `type`. See models.py.

Example invocation:

    python seed.py --input seed.example.yaml --db data/harness.db
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from .config import Config
from .db import connect, run_migrations
from .models import BODY_MODELS
from .store import Store
from .validation import ValidationError, validate_for_submit
from .models import DraftIn


class SeedError(RuntimeError):
    """Raised when a seed entry fails to load. Includes locator (index/title)."""


def _load_yaml(path: Path) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raise SeedError(f"{path} is empty.")
    if isinstance(raw, dict):
        if "entries" not in raw or not isinstance(raw["entries"], list):
            raise SeedError(
                f"{path} top-level dict must contain key 'entries' with a list."
            )
        entries = raw["entries"]
    elif isinstance(raw, list):
        entries = raw
    else:
        raise SeedError(f"{path} must be a YAML list or a dict with 'entries'.")

    for idx, item in enumerate(entries):
        if not isinstance(item, dict):
            raise SeedError(f"Entry #{idx} is not a mapping.")
    return entries


def _validate_entry(idx: int, item: dict[str, Any]) -> tuple[str, DraftIn]:
    """Validate a parsed YAML entry. Returns (entry_type, DraftIn)."""
    loc = f"#{idx} (title={item.get('title', '<missing>')!r})"
    entry_type = item.get("type")
    if entry_type not in BODY_MODELS:
        raise SeedError(
            f"Entry {loc}: unknown or missing 'type'. "
            f"Expected one of {sorted(BODY_MODELS)}."
        )
    try:
        draft = DraftIn(
            title=item.get("title", ""),
            tags=item.get("tags") or [],
            body=item.get("body") or {},
            evidence_links=item.get("evidence_links") or [],
            supersedes=item.get("supersedes"),
        )
    except Exception as e:
        raise SeedError(f"Entry {loc}: shape error — {e}") from e
    try:
        validate_for_submit(entry_type, draft)
    except ValidationError as e:
        raise SeedError(f"Entry {loc}: validation failed — {e}") from e
    return entry_type, draft


def load(path: Path, store: Store, default_author: str = "seed") -> int:
    """Validate all entries first, then insert in order. Returns count loaded."""
    raw_entries = _load_yaml(path)

    # Validate everything before touching the database. Fail fast and noisy.
    validated: list[tuple[str, DraftIn, str, str]] = []
    for idx, item in enumerate(raw_entries):
        entry_type, draft = _validate_entry(idx, item)
        author = item.get("author") or default_author
        status = item.get("status") or "accepted"
        if status not in ("proposed", "accepted", "superseded", "deprecated"):
            raise SeedError(f"Entry #{idx}: invalid status {status!r}.")
        validated.append((entry_type, draft, author, status))

    # Skip duplicates by (type, title) so re-runs are idempotent.
    existing: set[tuple[str, str]] = set()
    for r in store.conn.execute("SELECT type, title FROM entries").fetchall():
        existing.add((r["type"], r["title"]))

    loaded = 0
    for entry_type, draft, author, status in validated:
        if (entry_type, draft.title) in existing:
            continue
        store.insert_entry(
            entry_type=entry_type,
            title=draft.title,
            tags=draft.tags,
            author=author,
            body=draft.body,
            evidence_links=draft.evidence_links,
            supersedes=draft.supersedes,
            status=status,
        )
        store.audit(
            tool="seed",
            entry_id=None,
            author=author,
            reason=f"seed::{entry_type}::{draft.title}",
        )
        loaded += 1
    return loaded


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Load SDLC entries from YAML into the database.")
    p.add_argument("--input", required=True, type=Path, help="Path to seed YAML file.")
    p.add_argument("--db", type=Path, help="Override database path.")
    p.add_argument("--author", default="seed", help="Default author when an entry omits one.")
    args = p.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input file does not exist: {args.input}", file=sys.stderr)
        return 2

    cfg = Config.from_env()
    db_path = args.db.resolve() if args.db else cfg.db_path
    conn = connect(db_path)
    run_migrations(conn, cfg.migrations_dir)
    store = Store(conn)

    try:
        loaded = load(args.input, store, default_author=args.author)
    except SeedError as e:
        print(f"ERROR: seed aborted — {e}", file=sys.stderr)
        return 1

    print(json.dumps({"db": str(db_path), "input": str(args.input), "loaded": loaded}, indent=2))
    print(f"Loaded {loaded} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
