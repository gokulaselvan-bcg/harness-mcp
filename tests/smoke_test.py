"""Smoke test: exercise every read and write tool against a fresh database.

Run with:  python -m tests.smoke_test
Exits non-zero on any failed assertion.
"""
from __future__ import annotations

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

# Ensure src/ is on the path when run as a script.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sdlc_mcp.config import Config  # noqa: E402
from sdlc_mcp.db import connect, run_migrations  # noqa: E402
from sdlc_mcp.seed import load as seed_from_yaml  # noqa: E402
from sdlc_mcp.server import build_server  # noqa: E402
from sdlc_mcp.store import Store, daily_snapshot  # noqa: E402


def banner(msg: str) -> None:
    print(f"\n=== {msg} ===")


async def call(mcp, name, **kwargs):
    """Invoke a registered FastMCP tool with no conversion to content blocks."""
    return await mcp._tool_manager.call_tool(name, kwargs, context=None, convert_result=False)


async def run_smoke() -> None:
    work = Path(tempfile.mkdtemp(prefix="sdlc-mcp-smoke-"))
    db = work / "smoke.sqlite3"
    backups = work / "backups"
    logs = work / "smoke.log"
    migrations = ROOT / "migrations"

    cfg = Config(db_path=db, backup_dir=backups, log_path=logs, migrations_dir=migrations)

    # Pre-seed before starting the server, against a fresh schema.
    banner("Initial migrate + seed")
    conn = connect(db)
    run_migrations(conn, migrations)
    seed_file = ROOT / "seed.example.yaml"
    if not seed_file.exists():
        raise SystemExit(f"seed.example.yaml missing at {seed_file}; cannot run smoke test")
    inserted = seed_from_yaml(seed_file, Store(conn))
    print(f"seeded: {inserted} entries from {seed_file.name}")
    conn.close()

    banner("Build server")
    mcp = build_server(cfg)

    # --- Read tools ----------------------------------------------------
    banner("query (search for 'Pydantic')")
    results = await call(mcp, "query", search_string="Pydantic")
    assert any(e["id"].startswith("DEC-") for e in results), results
    print(f"got {len(results)} results; first id = {results[0]['id']}")

    banner("query filtered by type=agent")
    agents = await call(mcp, "query", search_string="", types=["agent"])
    assert all(e["type"] == "agent" for e in agents)
    print(f"agent count = {len(agents)}")

    banner("query filtered by tag")
    tagged = await call(mcp, "query", search_string="", tags=["python"])
    assert tagged, "expected at least one entry tagged python"
    print(f"python-tagged count = {len(tagged)}")

    banner("get(DEC-001)")
    one = await call(mcp, "get", id="DEC-001")
    assert one is not None and one["id"] == "DEC-001"
    print("title:", one["title"])

    banner("list_recent(days=1)")
    recent = await call(mcp, "list_recent", days=1)
    assert recent, "expected seeded entries to be recent"
    print(f"recent count = {len(recent)}")

    # --- Write tools: draft -> submit ----------------------------------
    banner("draft -> submit a new decision")
    draft_resp = await call(
        mcp,
        "draft",
        type="decision",
        content={
            "title": "Structured logging only",
            "tags": ["logging", "observability"],
            "body": {
                "rule": "All log records are emitted as structured key=value JSON.",
                "reasoning": "Structured logs are the only logs we can index and query later.",
                "alternatives_considered": "Free-form text (rejected: unparseable at scale).",
            },
        },
    )
    draft_id = draft_resp["draft_id"]
    print("draft_id:", draft_id)
    submit_resp = await call(mcp, "submit", draft_id=draft_id, author="smoke@test")
    new_entry = submit_resp["entry"]
    print("new entry:", new_entry["id"], "status:", new_entry["status"])
    assert new_entry["status"] == "accepted"
    assert new_entry["id"].startswith("DEC-")

    # --- supersede -----------------------------------------------------
    banner("supersede the new decision with a tightened rule")
    sup_resp = await call(
        mcp,
        "supersede",
        old_id=new_entry["id"],
        new_content={
            "title": "Structured JSON logging at INFO and above",
            "tags": ["logging", "observability"],
            "body": {
                "rule": "All log records at INFO and above are emitted as JSON.",
                "reasoning": "Same as predecessor; clarified that DEBUG can stay free-form for local dev.",
                "alternatives_considered": "Apply to all levels (rejected: too noisy locally).",
            },
        },
        reason="Refined scope after team feedback",
        author="smoke@test",
    )
    chain_root = sup_resp["new_entry"]["id"]
    print("new id:", chain_root)

    banner("get_supersession_chain on the new id")
    chain = await call(mcp, "get_supersession_chain", id=chain_root)
    assert len(chain) == 2, chain
    assert chain[0]["id"] == chain_root
    assert chain[1]["id"] == new_entry["id"]
    print("chain ids:", [c["id"] for c in chain])

    old_after = await call(mcp, "get", id=new_entry["id"])
    assert old_after["status"] == "superseded"
    assert old_after["superseded_by"] == chain_root

    # --- deprecate -----------------------------------------------------
    banner("deprecate an agent entry")
    agt = (await call(mcp, "query", search_string="", types=["agent"]))[0]
    dep = await call(mcp, "deprecate", id=agt["id"], reason="example", author="smoke@test")
    assert dep["status"] == "deprecated"
    re_get = await call(mcp, "get", id=agt["id"])
    assert re_get["status"] == "deprecated"
    print("deprecated:", agt["id"])

    # --- conflict warning surfaces -------------------------------------
    # Submit a near-duplicate of the post-supersession entry we just created
    # (DEC-040 in the chain). Same tags, overlapping title tokens.
    banner("submit a near-duplicate decision and confirm conflict warning")
    dup_draft = await call(
        mcp,
        "draft",
        type="decision",
        content={
            "title": "Structured JSON logs everywhere at INFO",
            "tags": ["logging", "observability"],
            "body": {
                "rule": "All logs at INFO and above are emitted as JSON.",
                "reasoning": "Duplicate of the existing logging rule.",
                "alternatives_considered": "Free-form text (rejected).",
            },
        },
    )
    dup_submit = await call(mcp, "submit", draft_id=dup_draft["draft_id"], author="smoke@test")
    print("conflicts found:", [c["id"] for c in dup_submit["conflicts"]])
    assert dup_submit["conflicts"], "expected conflict warning against the structured-logging entry we just submitted"

    # --- validation failure path ---------------------------------------
    banner("submit with missing alternatives_considered should fail")
    bad = await call(
        mcp,
        "draft",
        type="decision",
        content={
            "title": "Bad decision",
            "tags": ["bad"],
            "body": {
                "rule": "rule",
                "reasoning": "reason",
                "alternatives_considered": "",
            },
        },
    )
    try:
        await call(mcp, "submit", draft_id=bad["draft_id"], author="smoke@test")
    except Exception as e:
        print("expected validation failure:", e)
    else:
        raise AssertionError("submit should have failed validation")

    # --- reference counters --------------------------------------------
    banner("reference counter increments")
    before = await call(mcp, "get", id="DEC-001")
    await call(mcp, "query", search_string="Pydantic")
    after = await call(mcp, "get", id="DEC-001")
    assert after["reference_count"] > before["reference_count"], (
        before["reference_count"], after["reference_count"]
    )
    print(f"refcount {before['reference_count']} -> {after['reference_count']}")

    # --- daily snapshot ------------------------------------------------
    banner("daily_snapshot writes a dated file")
    snap = daily_snapshot(db, backups)
    assert snap.exists(), snap
    print("snapshot at:", snap)

    # --- audit log populated -------------------------------------------
    banner("audit log content")
    conn = connect(db)
    rows = conn.execute(
        "SELECT tool, entry_id, author, reason FROM audit_log ORDER BY id"
    ).fetchall()
    conn.close()
    tools_called = {r["tool"] for r in rows}
    print(f"audit rows: {len(rows)}; tools: {sorted(tools_called)}")
    for required in ("draft", "submit", "supersede", "deprecate"):
        assert required in tools_called, f"missing audit entry for {required}"

    banner("ALL SMOKE CHECKS PASSED")
    shutil.rmtree(work)


def main() -> int:
    asyncio.run(run_smoke())
    return 0


if __name__ == "__main__":
    sys.exit(main())
