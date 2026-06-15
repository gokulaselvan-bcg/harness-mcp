"""ORM -> plain dict serializers for the JSON API."""
from __future__ import annotations

from . import citations, models


def deal(d: models.Deal) -> dict:
    return {
        "id": d.id,
        "borrower_name": d.borrower_name,
        "naics_code": d.naics_code,
        "status": d.status,
        "current_step": d.current_step,
        "agency_grade": d.agency_grade,
        "agency_grade_as_of": d.agency_grade_as_of,
        "agency_grade_source_url": d.agency_grade_source_url,
    }


def field(f: models.ExtractionField) -> dict:
    cite = citations.doc_page(f.source_doc_id, f.source_page) if f.source_doc_id and f.source_page else None
    return {
        "id": f.id,
        "key": f.key,
        "value": f.value,
        "citation": cite,
        "confidence": f.confidence,
        "reliability_tier": f.reliability_tier,
        "hitl_required": bool(f.hitl_required),
        "status": f.status,
        "version": f.version,
        "produced_by": f.produced_by,
        "model": f.model,
        "llm_mode": f.llm_mode,
    }


def ratio(r: models.Ratio) -> dict:
    return {"id": r.id, "name": r.name, "value": r.value, "source_field_ids": r.source_field_ids_json, "version": r.version}


def scorecard(sc: models.Scorecard | None) -> dict | None:
    if sc is None:
        return None
    return {
        "id": sc.id,
        "ratios": sc.ratios_json,
        "pd": sc.pd,
        "lgd": sc.lgd,
        "ead": sc.ead,
        "internal_grade": sc.internal_grade,
        "qualitative_dims": sc.qualitative_dims_json,
        "status": sc.status,
        "version": sc.version,
    }


def dd_finding(d: models.DDFinding) -> dict:
    return {"id": d.id, "finding_type": d.finding_type, "result": d.result, "citation": d.citation}


def cam(c: models.CAM | None) -> dict | None:
    if c is None:
        return None
    return {
        "id": c.id,
        "version": c.version,
        "status": c.status,
        "content_markdown": c.content_markdown,
        "slots": c.slots_json,
        "produced_by": c.produced_by,
        "llm_mode": c.llm_mode,
    }


def cam_edit(e: models.CAMEdit) -> dict:
    return {
        "id": e.id,
        "instruction": e.instruction,
        "proposed_diff": e.proposed_diff,
        "status": e.status,
        "approved_by": e.approved_by,
        "produced_by": e.produced_by,
        "llm_mode": e.llm_mode,
    }


def audit_row(a: models.AuditLog) -> dict:
    return {
        "id": a.id,
        "actor": a.actor,
        "actor_type": a.actor_type,
        "action": a.action,
        "target_table": a.target_table,
        "target_row_id": a.target_row_id,
        "target_version": a.target_version,
        "old_value": a.old_value,
        "new_value": a.new_value,
        "timestamp": a.timestamp.isoformat() if a.timestamp else None,
        "row_hash": a.row_hash,
    }


def chat_message(m: models.ChatMessage) -> dict:
    return {
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "citations": m.citations_json,
        "produced_by": m.produced_by,
        "llm_mode": m.llm_mode,
    }
