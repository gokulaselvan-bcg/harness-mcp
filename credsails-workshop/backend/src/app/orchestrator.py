"""Stage orchestration for the 8-step spine.

Framework-agnostic: raises StepError / GateBlocked / NotFound which main.py maps to
HTTP 409/404. The CAM compile is deterministic (slots stamped with their source
record + citation first); only the per-slot prose is a hero Claude call.
"""
from __future__ import annotations

import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import audit, citations, llm_client, models, retrieval, store
from .agents import cam_editor, cam_writer, extractor, rag_chat
from .canned import diligence, financials, monitor, scorecard
from .config import settings
from .db import reset_database

CAM_SECTIONS = [
    "Borrower Overview",
    "Financial Profile",
    "Credit Rating",
    "Due Diligence",
    "Risks & Mitigants",
    "Recommendation",
]


class StepError(Exception):
    """Step called out of order (-> 409)."""


class GateBlocked(Exception):
    """A HITL gate refused (-> 409)."""


class NotFound(Exception):
    """Referenced row not found (-> 404)."""


def require_step(deal: models.Deal, n: int) -> None:
    if deal.current_step < n:
        raise StepError(f"step requires current_step >= {n}, deal is at {deal.current_step}")


# ---- helpers ----------------------------------------------------------------

_PAGE_RE = re.compile(r"^===PAGE (\d+)===\s*$", re.MULTILINE)


def _load_pages(path) -> list[tuple[int, str]]:
    text = open(path, encoding="utf-8").read()
    parts = _PAGE_RE.split(text)
    # parts = ["", "1", body1, "2", body2, ...]
    pages: list[tuple[int, str]] = []
    for i in range(1, len(parts), 2):
        pages.append((int(parts[i]), parts[i + 1].strip()))
    return pages


def _ten_k(session: Session, deal: models.Deal) -> models.Document:
    return session.execute(
        select(models.Document).where(
            models.Document.deal_id == deal.id, models.Document.doc_type == "10k"
        )
    ).scalars().first()


def _sentinel(session: Session, deal: models.Deal) -> models.Document:
    return session.execute(
        select(models.Document).where(
            models.Document.deal_id == deal.id, models.Document.doc_type == "reference_data"
        )
    ).scalars().first()


def _chunks(session: Session, doc_id: int) -> list[models.DocChunk]:
    return list(
        session.execute(
            select(models.DocChunk).where(models.DocChunk.document_id == doc_id).order_by(models.DocChunk.page)
        ).scalars().all()
    )


def _doc_text(session: Session, ten_k: models.Document) -> str:
    return "\n\n".join(c.text for c in _chunks(session, ten_k.id))


# ---- step 0: seed -----------------------------------------------------------

def seed_deal(session: Session) -> models.Deal:
    reset_database()
    deal = models.Deal(
        borrower_name="Cleveland-Cliffs Inc.",
        naics_code="331110",
        status="in_progress",
        current_step=0,
        agency_grade="BB",
        agency_grade_as_of="2026-01-15",
        agency_grade_source_url="https://disclosure.spglobal.com/ratings/  (illustrative)",
    )
    session.add(deal)
    session.flush()
    ten_k = models.Document(deal_id=deal.id, doc_type="10k", path=str(settings.data_dir / "clf_10k.txt"))
    session.add(ten_k)
    sentinel = models.Document(deal_id=deal.id, doc_type="reference_data")
    session.add(sentinel)
    session.flush()
    pages = _load_pages(settings.data_dir / "clf_10k.txt")
    ten_k.page_count = len(pages)
    for pageno, body in pages:
        session.add(
            models.DocChunk(document_id=ten_k.id, page=pageno, char_start=0, char_end=len(body), text=body)
        )
    audit.record(
        session, deal_id=deal.id, actor="system:seed", actor_type="system",
        action="seed_deal", new_value=deal.borrower_name,
    )
    session.commit()
    return deal


# ---- step 1: extraction -----------------------------------------------------

def run_extraction(session: Session, deal: models.Deal) -> list[models.ExtractionField]:
    require_step(deal, 0)
    ten_k = _ten_k(session, deal)
    result = extractor.run(_doc_text(session, ten_k))
    prov = llm_client.provenance("extractor")
    current = store.field_map(session, deal.id)
    for ef in result.fields:
        hitl = ef.reliability_tier == "management_prepared"
        row = models.ExtractionField(
            deal_id=deal.id, key=ef.key, value=ef.value, source_doc_id=ten_k.id,
            source_page=ef.source_page, confidence=ef.confidence, reliability_tier=ef.reliability_tier,
            confidence_threshold=0.99 if hitl else 0.0, hitl_required=1 if hitl else 0,
            status="proposed", version=(current[ef.key].version + 1 if ef.key in current else 1), **prov,
        )
        if ef.key in current:
            store.supersede(session, current[ef.key], row)
        else:
            session.add(row)
            session.flush()
    audit.record(
        session, deal_id=deal.id, actor="agent:extractor", actor_type="agent", action="extract",
        target_table="extraction_field", new_value=f"{len(result.fields)} fields",
    )
    deal.current_step = max(deal.current_step, 1)
    session.commit()
    return store.current_fields(session, deal.id)


# ---- step 2: HITL gate ------------------------------------------------------

def edit_field(session: Session, deal: models.Deal, field_id: int, value: str) -> models.ExtractionField:
    f = session.get(models.ExtractionField, field_id)
    if not f or f.deal_id != deal.id or f.superseded_by is not None:
        raise NotFound("field is not current")
    old = str(f.value)
    new = store.new_field_version(session, f, value)
    audit.record(
        session, deal_id=deal.id, actor="human:analyst", actor_type="human", action="edit_field",
        target_table="extraction_field", target_row_id=new.id, target_version=new.version,
        old_value=old, new_value=str(value),
    )
    session.commit()
    return new


def approve_fields(session: Session, deal: models.Deal) -> None:
    require_step(deal, 1)
    fields = store.current_fields(session, deal.id)
    pending = [f for f in fields if f.hitl_required and (f.produced_by or "").startswith("agent")]
    if pending:
        raise GateBlocked(
            "HITL-mandatory fields must be reviewed before approval: " + ", ".join(f.key for f in pending)
        )
    for f in fields:
        f.status = "approved"
    audit.record(
        session, deal_id=deal.id, actor="human:analyst", actor_type="human",
        action="approve_fields", new_value=f"{len(fields)} fields approved",
    )
    deal.current_step = max(deal.current_step, 2)
    session.commit()


# ---- step 3: model + score --------------------------------------------------

def _rebuild_ratios(session: Session, deal: models.Deal) -> None:
    fields = store.field_map(session, deal.id)
    existing = {r.name: r for r in store.current_ratios(session, deal.id)}
    for spec in financials.compute(fields):
        row = models.Ratio(
            deal_id=deal.id, name=spec["name"], value=spec["value"],
            source_field_ids_json=spec["source_field_ids"],
            version=(existing[spec["name"]].version + 1 if spec["name"] in existing else 1),
        )
        if spec["name"] in existing:
            store.supersede(session, existing[spec["name"]], row)
        else:
            session.add(row)
            session.flush()


def run_score(session: Session, deal: models.Deal) -> models.Scorecard:
    require_step(deal, 2)
    _rebuild_ratios(session, deal)
    fields = store.field_map(session, deal.id)
    ten_k, sentinel = _ten_k(session, deal), _sentinel(session, deal)
    ratios = [{"name": r.name, "value": r.value} for r in store.current_ratios(session, deal.id)]
    data = scorecard.compute(fields, ratios, ten_k.id, sentinel.id)
    existing = store.current_scorecard(session, deal.id)
    sc = models.Scorecard(
        deal_id=deal.id, status="approved",
        version=(existing.version + 1 if existing else 1), **data,
    )
    if existing:
        store.supersede(session, existing, sc)
    else:
        session.add(sc)
        session.flush()
    audit.record(
        session, deal_id=deal.id, actor="system:scorecard", actor_type="system", action="score",
        target_table="scorecard", target_row_id=sc.id, new_value=sc.internal_grade,
    )
    deal.current_step = max(deal.current_step, 3)
    session.commit()
    return sc


# ---- step 4: due diligence --------------------------------------------------

def run_diligence(session: Session, deal: models.Deal) -> list[models.DDFinding]:
    require_step(deal, 3)
    sentinel = _sentinel(session, deal)
    existing = store.dd_findings(session, deal.id)
    if existing:
        audit.record(
            session, deal_id=deal.id, actor="system:diligence", actor_type="system",
            action="diligence_replace", old_value=f"{len(existing)} findings replaced",
        )
        for e in existing:
            session.delete(e)
        session.flush()
    for f in diligence.findings(sentinel.id):
        session.add(models.DDFinding(deal_id=deal.id, finding_type=f["finding_type"], result=f["result"], citation=f["citation"]))
    audit.record(
        session, deal_id=deal.id, actor="system:diligence", actor_type="system",
        action="diligence", new_value="OFAC/PEP, adverse-media, UCC-1",
    )
    deal.current_step = max(deal.current_step, 4)
    session.commit()
    return store.dd_findings(session, deal.id)


# ---- step 5: compile CAM ----------------------------------------------------

def _build_slots(session: Session, deal: models.Deal) -> list[dict]:
    fields = store.field_map(session, deal.id)
    ten_k, sentinel = _ten_k(session, deal), _sentinel(session, deal)
    sc = store.current_scorecard(session, deal.id)
    dds = store.dd_findings(session, deal.id)

    def fval(k):
        return fields[k].value if k in fields else None

    bn = fields.get("borrower_name")
    cn = fields.get("collateral_note")
    agency_cite = citations.external_url(deal.agency_grade_source_url, deal.agency_grade_as_of)
    snapshot = {"grade": deal.agency_grade, "as_of": deal.agency_grade_as_of, "source_url": deal.agency_grade_source_url}
    return [
        {
            "section": "Borrower Overview", "source_table": "extraction_field",
            "source_id": bn.id if bn else None, "source_version": bn.version if bn else None,
            "citation": citations.doc_page(ten_k.id, 1),
            "facts": {k: fval(k) for k in ("borrower_name", "state_of_incorporation", "naics_code")},
        },
        {
            "section": "Financial Profile", "source_table": "scorecard",
            "source_id": sc.id, "source_version": sc.version,
            "citation": citations.doc_page(ten_k.id, 3),
            "facts": {"ratios": sc.ratios_json, "revenue": fval("total_revenue"),
                      "adjusted_ebitda": fval("adjusted_ebitda"), "total_debt": fval("total_debt"),
                      "total_equity": fval("total_equity")},
        },
        {
            "section": "Credit Rating", "source_table": "scorecard",
            "source_id": sc.id, "source_version": sc.version,
            "citation": agency_cite, "agency_grade_snapshot": snapshot,
            "facts": {"internal_grade": sc.internal_grade, "agency_grade": deal.agency_grade, "pd": sc.pd, "lgd": sc.lgd},
        },
        {
            "section": "Due Diligence", "source_table": "dd_finding",
            "source_id": dds[0].id if dds else None, "source_version": None,
            "citation": citations.reference_data(sentinel.id),
            "facts": {"findings": [{"type": d.finding_type, "result": d.result} for d in dds]},
        },
        {
            "section": "Risks & Mitigants", "source_table": "extraction_field",
            "source_id": cn.id if cn else None, "source_version": cn.version if cn else None,
            "citation": citations.doc_page(ten_k.id, 4),
            "facts": {"collateral": cn.value if cn else None, "qualitative": sc.qualitative_dims_json},
        },
        {
            "section": "Recommendation", "source_table": "scorecard",
            "source_id": sc.id, "source_version": sc.version, "citation": agency_cite,
            "facts": {"internal_grade": sc.internal_grade, "ratios": sc.ratios_json},
        },
    ]


def _build_and_commit_cam(session: Session, deal: models.Deal) -> models.CAM:
    ten_k = _ten_k(session, deal)
    slots = _build_slots(session, deal)
    skeleton = [{"section": s["section"], "facts": s["facts"]} for s in slots]
    prov = llm_client.provenance("cam_writer")
    write = cam_writer.run(_doc_text(session, ten_k), skeleton)
    prose_by_section = {sec.section: sec.prose for sec in write.sections}

    lines = [f"# Credit Application Memo — {deal.borrower_name}", ""]
    for s in slots:
        s["prose"] = prose_by_section.get(s["section"], "")
        s.pop("facts", None)  # slots_json keeps source pins + citation + prose, not the raw inputs
        lines += [f"## {s['section']}", s["prose"], ""]
    content = "\n".join(lines)

    existing = store.current_cam(session, deal.id)
    cam = models.CAM(
        deal_id=deal.id, version=(existing.version + 1 if existing else 1),
        content_markdown=content, slots_json=slots, status="committed", **prov,
    )
    if existing:
        store.supersede(session, existing, cam)
    else:
        session.add(cam)
        session.flush()
    audit.record(
        session, deal_id=deal.id, actor="agent:cam_writer", actor_type="agent", action="compile_cam",
        target_table="cam", target_row_id=cam.id, target_version=cam.version,
    )
    audit.record(
        session, deal_id=deal.id, actor="system:orchestrator", actor_type="system", action="commit_cam",
        target_table="cam", target_row_id=cam.id, target_version=cam.version,
    )
    return cam


def compile_cam(session: Session, deal: models.Deal) -> models.CAM:
    require_step(deal, 4)
    cam = _build_and_commit_cam(session, deal)
    deal.status = "committed"
    deal.current_step = max(deal.current_step, 5)
    session.commit()
    return cam


# ---- step 6: CAM edit gate --------------------------------------------------

def propose_cam_edit(session: Session, deal: models.Deal, instruction: str) -> models.CAMEdit:
    require_step(deal, 5)
    cam = store.current_cam(session, deal.id)
    if not cam:
        raise NotFound("no committed CAM")
    res = cam_editor.run(cam.content_markdown, instruction)
    edit = models.CAMEdit(
        deal_id=deal.id, cam_id=cam.id, instruction=instruction,
        proposed_diff=res.proposed_diff, status="proposed", **llm_client.provenance("cam_editor"),
    )
    session.add(edit)
    session.flush()
    audit.record(
        session, deal_id=deal.id, actor="agent:cam_editor", actor_type="agent", action="propose_cam_edit",
        target_table="cam_edit", target_row_id=edit.id, new_value=res.proposed_diff[:200],
    )
    session.commit()
    return edit


def _apply_diff(md: str, diff: str) -> str:
    minus = [ln[2:] for ln in diff.splitlines() if ln.startswith("- ")]
    plus = [ln[2:] for ln in diff.splitlines() if ln.startswith("+ ")]
    for old, new in zip(minus, plus):
        md = md.replace(old, new)
    return md


def resolve_cam_edit(session: Session, deal: models.Deal, edit_id: int, decision: str) -> models.CAMEdit:
    require_step(deal, 5)
    edit = session.get(models.CAMEdit, edit_id)
    if not edit or edit.deal_id != deal.id:
        raise NotFound("edit not found")
    if edit.status != "proposed":
        raise GateBlocked("edit already resolved")
    if decision == "approve":
        cam = store.current_cam(session, deal.id)
        new_cam = models.CAM(
            deal_id=deal.id, version=cam.version + 1,
            content_markdown=_apply_diff(cam.content_markdown, edit.proposed_diff),
            slots_json=cam.slots_json, status="committed", **llm_client.provenance("cam_editor"),
        )
        store.supersede(session, cam, new_cam)
        edit.status = "approved"
        edit.approved_by = "human:analyst"
        audit.record(
            session, deal_id=deal.id, actor="human:analyst", actor_type="human", action="approve_cam_edit",
            target_table="cam", target_row_id=new_cam.id, target_version=new_cam.version,
            new_value=edit.proposed_diff[:200],
        )
    elif decision == "reject":
        edit.status = "rejected"
        edit.approved_by = "human:analyst"
        audit.record(
            session, deal_id=deal.id, actor="human:analyst", actor_type="human", action="reject_cam_edit",
            target_table="cam_edit", target_row_id=edit.id,
        )
    else:
        raise GateBlocked("decision must be 'approve' or 'reject'")
    session.commit()
    return edit


# ---- step 7: RAG chat -------------------------------------------------------

def _resolve_citations(session: Session, deal: models.Deal, keys: list[str]) -> list[dict]:
    fmap = store.field_map(session, deal.id)
    rmap = {r.name: r for r in store.current_ratios(session, deal.id)}
    seen: set = set()
    out: list[dict] = []

    def add_field(f: models.ExtractionField | None) -> None:
        if not f or not f.source_doc_id or not f.source_page:
            return
        key = (f.source_doc_id, f.source_page)
        if key not in seen:
            seen.add(key)
            out.append(citations.doc_page(f.source_doc_id, f.source_page))

    for k in keys:
        if k in fmap:
            add_field(fmap[k])
        elif k in rmap:
            for fid in rmap[k].source_field_ids_json or []:
                add_field(session.get(models.ExtractionField, fid))
    return out


def run_chat(session: Session, deal: models.Deal, question: str) -> dict:
    require_step(deal, 5)
    chunks = retrieval.search(session, deal.id, question, limit=3)
    res = rag_chat.run(question, chunks)
    cites = _resolve_citations(session, deal, res.cited_keys)
    session.add(models.ChatMessage(deal_id=deal.id, role="user", content=question, citations_json=[]))
    session.add(
        models.ChatMessage(
            deal_id=deal.id, role="assistant", content=res.answer,
            citations_json=cites, **llm_client.provenance("rag_chat"),
        )
    )
    audit.record(
        session, deal_id=deal.id, actor="agent:rag_chat", actor_type="agent", action="chat",
        new_value=question[:200],
    )
    session.commit()
    return {"answer": res.answer, "citations": cites, "context_pages": [c.page for c in chunks]}


# ---- step 8: monitor + re-trigger -------------------------------------------

def fire_monitor(session: Session, deal: models.Deal) -> dict:
    if deal.current_step < 5:
        raise StepError("commit the CAM before monitoring")
    if deal.status == "re_review":
        return {"status": "noop", "detail": "a re-review is already open"}
    sig = monitor.downgrade_signal()
    payload = sig["payload"]
    me = models.MonitorEvent(
        deal_id=deal.id, signal_type=sig["signal_type"], payload_json=payload, re_review_triggered=1
    )
    session.add(me)
    session.flush()
    audit.record(
        session, deal_id=deal.id, actor="system:monitor", actor_type="system", action="monitor_signal",
        target_table="monitor_event", target_row_id=me.id, new_value=json.dumps(payload),
    )
    old = f"{deal.agency_grade}|{deal.agency_grade_as_of}|{deal.agency_grade_source_url}"
    deal.agency_grade = payload["agency_grade"]
    deal.agency_grade_as_of = payload["as_of"]
    deal.agency_grade_source_url = payload["source_url"]
    new = f"{deal.agency_grade}|{deal.agency_grade_as_of}|{deal.agency_grade_source_url}"
    audit.record(
        session, deal_id=deal.id, actor="system:monitor", actor_type="system", action="agency_regrade",
        target_table="deal", target_row_id=deal.id, old_value=old, new_value=new,
    )
    sc = store.current_scorecard(session, deal.id)
    new_sc = models.Scorecard(
        deal_id=deal.id, ratios_json=sc.ratios_json, pd=(sc.pd * 1.5 if sc.pd else None),
        lgd=sc.lgd, ead=sc.ead, internal_grade="B+", qualitative_dims_json=sc.qualitative_dims_json,
        status="proposed", version=sc.version + 1,
    )
    store.supersede(session, sc, new_sc)
    audit.record(
        session, deal_id=deal.id, actor="system:monitor", actor_type="system", action="rescore_pending",
        target_table="scorecard", target_row_id=new_sc.id, target_version=new_sc.version,
    )
    deal.status = "re_review"
    session.commit()
    return {"status": "re_review", "scorecard_id": new_sc.id, "agency_grade": deal.agency_grade}


def reapprove(session: Session, deal: models.Deal) -> models.CAM:
    """Close the loop: approve the re-scored card, recompute ratios, recommit CAM v2."""
    if deal.status != "re_review":
        raise GateBlocked("no open re-review")
    sc = store.current_scorecard(session, deal.id)
    sc.status = "approved"
    audit.record(
        session, deal_id=deal.id, actor="human:analyst", actor_type="human", action="approve_rescore",
        target_table="scorecard", target_row_id=sc.id, target_version=sc.version,
    )
    _rebuild_ratios(session, deal)
    cam = _build_and_commit_cam(session, deal)
    deal.status = "committed"
    session.commit()
    return cam
