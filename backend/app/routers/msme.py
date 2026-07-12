from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from app.agents.graph import run_pipeline, stream_pipeline
from app.consent_store import ConsentStore, get_consent_store
from app.data_store import DataStore, get_data_store
from app.llm.prompts import build_chat_prompt
from app.llm.provider import generate_text
from app.llm.templates import chat_fallback_template
from app.models.schemas import (
    AssessmentResponse,
    ChatRequest,
    ChatResponse,
    ConsentRequest,
    ConsentResponse,
    MsmeListItem,
    MsmeProfile,
    ReportPayload,
)
from app.scoring.enhanced_score import compute_enhanced_score
from app.scoring.public_score import compute_public_score

router = APIRouter(prefix="/api/msme", tags=["msme"])


def _get_msme_or_404(store: DataStore, msme_id: str):
    master = store.master.get(msme_id)
    if master is None:
        raise HTTPException(status_code=404, detail=f"MSME {msme_id} not found")
    return master


def build_list_item(store: DataStore, consent_store: ConsentStore, msme_id: str) -> MsmeListItem:
    master = store.master[msme_id]
    public = store.public[msme_id]
    consent = store.consent[msme_id]
    granted = consent_store.granted_sources(msme_id)

    last_band = None
    last_score = None
    if granted:
        enhanced = compute_enhanced_score(master, public, consent, granted, [])
        last_band = enhanced.riskBand
        last_score = enhanced.finalScore

    return MsmeListItem(
        msmeId=msme_id,
        businessName=master.business_name,
        sector=master.sector,
        city=master.city,
        state=master.state,
        archetype=master.archetype,
        isDemoArchetype=store.is_demo_archetype(msme_id),
        lastRiskBand=last_band,
        lastFinalScore=last_score,
    )


@router.get("", response_model=list[MsmeListItem])
def list_msmes(
    search: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    city: str | None = Query(default=None),
    riskBand: str | None = Query(default=None),
) -> list[MsmeListItem]:
    store = get_data_store()
    consent_store = get_consent_store()
    items = [build_list_item(store, consent_store, msme_id) for msme_id in store.all_ids()]

    if search:
        needle = search.lower()
        items = [i for i in items if needle in i.businessName.lower()]
    if sector:
        items = [i for i in items if i.sector == sector]
    if city:
        items = [i for i in items if i.city == city]
    if riskBand:
        items = [i for i in items if i.lastRiskBand is not None and i.lastRiskBand.value == riskBand]

    return items


@router.get("/{msme_id}", response_model=MsmeProfile)
def get_msme_profile(msme_id: str) -> MsmeProfile:
    store = get_data_store()
    consent_store = get_consent_store()
    master = _get_msme_or_404(store, msme_id)

    return MsmeProfile(
        master=master,
        isDemoArchetype=store.is_demo_archetype(msme_id),
        consentStatus=consent_store.status(msme_id),
        grantedSources=consent_store.granted_sources(msme_id),
    )


@router.get("/{msme_id}/public-assessment")
def get_public_assessment(msme_id: str):
    store = get_data_store()
    master = _get_msme_or_404(store, msme_id)
    public = store.public[msme_id]
    return compute_public_score(master, public)


@router.post("/{msme_id}/consent", response_model=ConsentResponse)
def grant_consent(msme_id: str, body: ConsentRequest) -> ConsentResponse:
    store = get_data_store()
    _get_msme_or_404(store, msme_id)
    consent_store = get_consent_store()
    consent_store.grant(msme_id, body.sources)

    return ConsentResponse(
        msmeId=msme_id,
        consentStatus=consent_store.status(msme_id),
        grantedSources=consent_store.granted_sources(msme_id),
    )


@router.post("/{msme_id}/assess", response_model=AssessmentResponse)
async def assess_msme(msme_id: str) -> AssessmentResponse:
    store = get_data_store()
    _get_msme_or_404(store, msme_id)
    consent_store = get_consent_store()
    granted = consent_store.granted_sources(msme_id)

    state = await run_pipeline(msme_id, granted)
    return AssessmentResponse(**state.model_dump())


@router.get("/{msme_id}/assess/stream")
async def assess_msme_stream(msme_id: str):
    store = get_data_store()
    _get_msme_or_404(store, msme_id)
    consent_store = get_consent_store()
    granted = consent_store.granted_sources(msme_id)

    async def event_generator():
        async for kind, payload in stream_pipeline(msme_id, granted):
            if kind == "status":
                yield {"event": "agent_status", "data": payload.model_dump_json()}
            else:
                response = AssessmentResponse(**payload.model_dump())
                yield {"event": "final_result", "data": response.model_dump_json()}

    return EventSourceResponse(event_generator())


@router.post("/{msme_id}/chat", response_model=ChatResponse)
async def chat_with_assistant(msme_id: str, body: ChatRequest) -> ChatResponse:
    store = get_data_store()
    master = _get_msme_or_404(store, msme_id)
    public = store.public[msme_id]
    consent = store.consent[msme_id]
    consent_store = get_consent_store()
    granted = consent_store.granted_sources(msme_id)

    public_score = compute_public_score(master, public)
    enhanced_score = compute_enhanced_score(master, public, consent, granted, []) if granted else None

    context = {
        "businessName": master.business_name,
        "sector": master.sector,
        "city": master.city,
        "archetype": master.archetype.value,
        "consentGranted": [s.value for s in granted],
        "publicScore": public_score.model_dump(),
        "enhancedScore": enhanced_score.model_dump() if enhanced_score else None,
    }
    history = [m.model_dump() for m in body.history[-10:]]

    system_prompt, user_prompt = build_chat_prompt(context, history, body.message)
    llm_text, used_llm = await generate_text(system_prompt, user_prompt)
    reply = llm_text or chat_fallback_template(body.message)

    return ChatResponse(reply=reply, usedLlm=used_llm)


@router.get("/{msme_id}/report", response_model=ReportPayload)
async def get_report(msme_id: str) -> ReportPayload:
    store = get_data_store()
    master = _get_msme_or_404(store, msme_id)
    public = store.public[msme_id]
    consent = store.consent[msme_id]
    consent_store = get_consent_store()
    granted = consent_store.granted_sources(msme_id)

    state = await run_pipeline(msme_id, granted)

    return ReportPayload(
        profile=MsmeProfile(
            master=master,
            isDemoArchetype=store.is_demo_archetype(msme_id),
            consentStatus=consent_store.status(msme_id),
            grantedSources=granted,
        ),
        publicSignals=public,
        consentSignals=consent if granted else None,
        publicScore=state.publicScore,
        enhancedScore=state.enhancedScore,
        positiveIndicators=state.positiveIndicators,
        riskIndicators=state.riskIndicators,
        healthSummary=state.healthSummary,
        recommendation=state.recommendation,
        generatedAt=datetime.now(timezone.utc).isoformat(),
    )
