"""Full-spine integration tests over the HTTP API (stub mode)."""
from __future__ import annotations

from conftest import drive_to_cam, review_and_approve


def test_full_spine_closes_the_loop(client):
    drive_to_cam(client)
    # step 6: reject one edit, approve another
    e1 = client.post("/api/deal/cam/edit", json={"instruction": "soften risk"}).json()
    assert client.post(f"/api/deal/cam/edit/{e1['id']}/resolve", json={"decision": "reject"}).status_code == 200
    e2 = client.post("/api/deal/cam/edit", json={"instruction": "add mitigant"}).json()
    assert client.post(f"/api/deal/cam/edit/{e2['id']}/resolve", json={"decision": "approve"}).status_code == 200
    # step 7: chat citation lands on the persisted pages
    ch = client.post("/api/deal/chat", json={"question": "where did the leverage figure come from?"}).json()
    assert sorted(c["page"] for c in ch["citations"]) == [2, 3]
    # step 8: monitor -> re_review -> reapprove -> committed (loop closes)
    assert client.post("/api/deal/monitor/fire").json()["status"] == "re_review"
    assert client.post("/api/deal/monitor/fire").json()["status"] == "noop"  # replay-safe
    assert client.post("/api/deal/monitor/reapprove").status_code == 200
    st = client.get("/api/deal/state").json()
    assert st["deal"]["status"] == "committed"
    assert st["deal"]["agency_grade"] == "B+"
    assert st["cam"]["version"] >= 2
    assert st["audit_verified"] is True


def test_step_order_returns_409(client):
    assert client.post("/api/deal/seed").status_code == 200
    # compile before extraction/approval
    assert client.post("/api/deal/cam/compile").status_code == 409


def test_hitl_gate_blocks_until_reviewed(client):
    client.post("/api/deal/seed")
    client.post("/api/deal/extract")
    assert client.post("/api/deal/fields/approve").status_code == 409  # management_prepared unreviewed
    review_and_approve(client)
    assert client.get("/api/deal/state").json()["deal"]["current_step"] >= 2


def test_extraction_replay_is_idempotent(client):
    client.post("/api/deal/seed")
    a = client.post("/api/deal/extract").json()
    b = client.post("/api/deal/extract").json()  # re-run supersedes, no duplicates
    assert len(a) == len(b) == 14
    keys = [f["key"] for f in b]
    assert len(keys) == len(set(keys))  # one current row per key


def test_ratios_and_grade(client):
    drive_to_cam(client)
    st = client.get("/api/deal/state").json()
    ratios = {r["name"]: r["value"] for r in st["ratios"]}
    assert ratios["leverage_net_debt_ebitda"] == "3.11x"
    assert ratios["dscr"] == "4.00x"
    assert ratios["current_ratio"] == "2.00x"
    assert st["scorecard"]["internal_grade"] == "BB-"
    assert st["deal"]["agency_grade"] == "BB"  # one notch apart


def test_cam_reconstructs_from_slots(client):
    drive_to_cam(client)
    cam = client.get("/api/deal/state").json()["cam"]
    sections = [s["section"] for s in cam["slots"]]
    assert sections == ["Borrower Overview", "Financial Profile", "Credit Rating",
                        "Due Diligence", "Risks & Mitigants", "Recommendation"]
    for s in cam["slots"]:
        assert s["source_table"] and s["source_id"]  # every slot pins a source
        assert s["citation"]["kind"] in {"doc_page", "external_url", "reference_data"}
