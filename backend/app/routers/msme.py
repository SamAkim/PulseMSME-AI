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
    ConsentFinancialSignals,
    ConsentStatus,
    CreateMsmeRequest,
    MsmeListItem,
    MsmeMaster,
    MsmeProfile,
    PublicSignals,
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


@router.post("", response_model=MsmeListItem, status_code=201)
def create_msme(body: CreateMsmeRequest) -> MsmeListItem:
    """Register a new MSME supplied by the credit officer via the UI form.

    A unique CUSTOM_XXX id is generated automatically. All three data objects
    (master profile, public signals, consent financial signals) are written to
    the live in-memory store so the normal assessment pipeline can run
    immediately without a server restart.
    """
    from datetime import date

    store = get_data_store()
    consent_store = get_consent_store()
    msme_id = store.next_custom_id()
    today = date.today().isoformat()

    master = MsmeMaster(
        msme_id=msme_id,
        business_name=body.business_name,
        sector=body.sector,
        city=body.city,
        state=body.state,
        business_age_years=body.business_age_years,
        legal_structure=body.legal_structure,
        udyam_registered=body.udyam_registered,
        employee_count=body.employee_count,
        credit_history_available=body.credit_history_available,
        primary_sales_channel=body.primary_sales_channel,
        archetype=body.archetype,
    )

    public = PublicSignals(
        msme_id=msme_id,
        google_rating=body.google_rating,
        google_review_count=body.google_review_count,
        positive_review_percentage=body.positive_review_percentage,
        review_sentiment_score=body.review_sentiment_score,
        social_media_followers=body.social_media_followers,
        social_engagement_rate=body.social_engagement_rate,
        website_present=body.website_present,
        website_quality_score=body.website_quality_score,
        website_domain_age_years=body.website_domain_age_years,
        business_listing_consistency=body.business_listing_consistency,
        digital_activity_score=body.digital_activity_score,
        public_data_last_updated=today,
    )

    consent = ConsentFinancialSignals(
        msme_id=msme_id,
        average_monthly_gst_turnover=body.average_monthly_gst_turnover,
        annual_gst_turnover=body.annual_gst_turnover,
        gst_turnover_growth_percentage=body.gst_turnover_growth_percentage,
        gst_filing_timeliness_percentage=body.gst_filing_timeliness_percentage,
        gst_sales_variance=body.gst_sales_variance,
        average_monthly_upi_inflow=body.average_monthly_upi_inflow,
        upi_transaction_count=body.upi_transaction_count,
        upi_inflow_growth_percentage=body.upi_inflow_growth_percentage,
        upi_refund_percentage=body.upi_refund_percentage,
        average_monthly_bank_credit=body.average_monthly_bank_credit,
        average_monthly_bank_debit=body.average_monthly_bank_debit,
        average_monthly_balance=body.average_monthly_balance,
        monthly_cash_surplus=body.monthly_cash_surplus,
        existing_monthly_loan_obligation=body.existing_monthly_loan_obligation,
        cheque_bounce_count=body.cheque_bounce_count,
        payment_failure_percentage=body.payment_failure_percentage,
        epfo_employee_count=body.epfo_employee_count,
        epfo_employee_growth_percentage=body.epfo_employee_growth_percentage,
        epfo_contribution_timeliness_percentage=body.epfo_contribution_timeliness_percentage,
        cash_flow_volatility=body.cash_flow_volatility,
        consent_status=ConsentStatus.NOT_REQUESTED,
        financial_data_last_updated=today,
    )

    store.add_msme(master, public, consent)
    return build_list_item(store, consent_store, msme_id)


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
