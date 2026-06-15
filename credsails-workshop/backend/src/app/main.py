"""FastAPI app for the CredSails demo.

Sync handlers (FastAPI runs them in a threadpool, so a multi-second live Claude call
never blocks the loop). API routes are registered FIRST; the SPA is served by a
StaticFiles mount at "/" LAST so it can't shadow /api/*. Same-origin, so no CORS.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import audit, orchestrator as orch, serializers, store
from .agents import schema_extractor
from .schemas import BSTemplateRow
from .config import settings
from .db import get_session
from .llm_client import LLMError
from .models import AuditLog, ChatMessage

app = FastAPI(title="CredSails Demo", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent / "static"


# ---- exception mapping ------------------------------------------------------

@app.exception_handler(orch.StepError)
def _step_error(_request, exc: orch.StepError):
    return JSONResponse(status_code=409, content={"error": "step_order", "detail": str(exc)})


@app.exception_handler(orch.GateBlocked)
def _gate_blocked(_request, exc: orch.GateBlocked):
    return JSONResponse(status_code=409, content={"error": "gate_blocked", "detail": str(exc)})


@app.exception_handler(orch.NotFound)
def _not_found(_request, exc: orch.NotFound):
    return JSONResponse(status_code=404, content={"error": "not_found", "detail": str(exc)})


@app.exception_handler(LLMError)
def _llm_error(_request, exc: LLMError):
    return JSONResponse(status_code=502, content={"error": "llm_error", "detail": str(exc)})


# ---- request bodies ---------------------------------------------------------

class EditFieldReq(BaseModel):
    value: str


class ProposeEditReq(BaseModel):
    instruction: str


class ResolveReq(BaseModel):
    decision: str  # approve | reject


class ChatReq(BaseModel):
    question: str


class BSExtractReq(BaseModel):
    pdf_path: str
    template: list[BSTemplateRow]


# ---- deal dependency --------------------------------------------------------

def _deal_or_404(session: Session) -> "object":
    deal = store.get_deal(session)
    if deal is None:
        raise orch.NotFound("no deal seeded; POST /api/deal/seed first")
    return deal


# ---- routes -----------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"ok": True, "llm_mode": settings.llm_mode, "model": settings.anthropic_model}


@app.post("/api/deal/seed")
def seed(session: Session = Depends(get_session)):
    deal = orch.seed_deal(session)
    return serializers.deal(deal)


@app.get("/api/deal/state")
def state(session: Session = Depends(get_session)):
    deal = store.get_deal(session)
    if deal is None:
        return {"deal": None, "llm_mode": settings.llm_mode}
    chats = (
        session.execute(
            select(ChatMessage).where(ChatMessage.deal_id == deal.id).order_by(ChatMessage.id.asc())
        ).scalars().all()
    )
    audits = (
        session.execute(
            select(AuditLog).where(AuditLog.deal_id == deal.id).order_by(AuditLog.id.asc())
        ).scalars().all()
    )
    return {
        "deal": serializers.deal(deal),
        "llm_mode": settings.llm_mode,
        "model": settings.anthropic_model,
        "fields": [serializers.field(f) for f in store.current_fields(session, deal.id)],
        "ratios": [serializers.ratio(r) for r in store.current_ratios(session, deal.id)],
        "scorecard": serializers.scorecard(store.current_scorecard(session, deal.id)),
        "dd_findings": [serializers.dd_finding(d) for d in store.dd_findings(session, deal.id)],
        "cam": serializers.cam(store.current_cam(session, deal.id)),
        "chat": [serializers.chat_message(m) for m in chats],
        "audit": [serializers.audit_row(a) for a in audits],
        "audit_verified": audit.verify_chain(session, deal.id),
    }


@app.post("/api/deal/extract")
def extract(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    fields = orch.run_extraction(session, deal)
    return [serializers.field(f) for f in fields]


@app.get("/api/deal/fields")
def fields(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return [serializers.field(f) for f in store.current_fields(session, deal.id)]


@app.patch("/api/deal/fields/{field_id}")
def patch_field(field_id: int, body: EditFieldReq, session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return serializers.field(orch.edit_field(session, deal, field_id, body.value))


@app.post("/api/deal/fields/approve")
def approve(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    orch.approve_fields(session, deal)
    return {"ok": True, "current_step": deal.current_step}


@app.post("/api/deal/score")
def score(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return serializers.scorecard(orch.run_score(session, deal))


@app.post("/api/deal/diligence")
def diligence(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return [serializers.dd_finding(d) for d in orch.run_diligence(session, deal)]


@app.post("/api/deal/cam/compile")
def cam_compile(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return serializers.cam(orch.compile_cam(session, deal))


@app.post("/api/deal/cam/edit")
def cam_edit_propose(body: ProposeEditReq, session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return serializers.cam_edit(orch.propose_cam_edit(session, deal, body.instruction))


@app.post("/api/deal/cam/edit/{edit_id}/resolve")
def cam_edit_resolve(edit_id: int, body: ResolveReq, session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    edit = orch.resolve_cam_edit(session, deal, edit_id, body.decision)
    return {"edit": serializers.cam_edit(edit), "cam": serializers.cam(store.current_cam(session, deal.id))}


@app.post("/api/deal/chat")
def chat(body: ChatReq, session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return orch.run_chat(session, deal, body.question)


@app.post("/api/deal/monitor/fire")
def monitor_fire(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return orch.fire_monitor(session, deal)


@app.post("/api/deal/monitor/reapprove")
def monitor_reapprove(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    return serializers.cam(orch.reapprove(session, deal))


@app.get("/api/deal/audit")
def get_audit(session: Session = Depends(get_session)):
    deal = _deal_or_404(session)
    rows = (
        session.execute(
            select(AuditLog).where(AuditLog.deal_id == deal.id).order_by(AuditLog.id.asc())
        ).scalars().all()
    )
    return {"rows": [serializers.audit_row(a) for a in rows], "verified": audit.verify_chain(session, deal.id)}


@app.post("/api/extract/balance-sheet")
def extract_balance_sheet(body: BSExtractReq):
    result = schema_extractor.run(body.pdf_path, body.template)
    return result.model_dump()


# SPA mount LAST so it never shadows /api/*
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
