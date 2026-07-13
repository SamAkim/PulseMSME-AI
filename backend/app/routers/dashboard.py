"""Portfolio dashboard metrics.

Headline portfolio figures (average score, band counts, sector/risk
distribution) are computed as if every MSME's committed synthetic
consent data were available — this is static demo data representing
the bank's assessed portfolio. publicOnlyCount/consentEnhancedCount and
recentAssessments reflect the *live* in-memory consent state for this
session, so the two-layer demo flow is visible as the user grants consent.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.consent_store import get_consent_store
from app.data_store import get_data_store
from app.models.schemas import ConsentSource, DashboardMetrics, RiskBand
from app.routers.msme import build_list_item
from app.scoring.enhanced_score import compute_enhanced_score

router = APIRouter(prefix="/api", tags=["dashboard"])

ALL_SOURCES = list(ConsentSource)


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard() -> DashboardMetrics:
    store = get_data_store()
    consent_store = get_consent_store()

    sector_distribution: dict[str, int] = {}
    risk_distribution: dict[str, int] = {}
    scores: list[int] = []
    excellent = good = requiring_review = 0

    for msme_id, master in store.master.items():
        public = store.public[msme_id]
        consent = store.consent[msme_id]
        enhanced = compute_enhanced_score(master, public, consent, ALL_SOURCES, [])

        sector_distribution[master.sector] = sector_distribution.get(master.sector, 0) + 1
        risk_distribution[enhanced.riskBand.value] = risk_distribution.get(enhanced.riskBand.value, 0) + 1
        scores.append(enhanced.finalScore)

        if enhanced.riskBand == RiskBand.EXCELLENT:
            excellent += 1
        elif enhanced.riskBand == RiskBand.GOOD:
            good += 1
        if enhanced.riskBand in (RiskBand.HIGH_RISK, RiskBand.BAD):
            requiring_review += 1

    public_only_count = sum(1 for mid in store.all_ids() if not consent_store.granted_sources(mid))
    consent_enhanced_count = len(store.all_ids()) - public_only_count

    recent_ids = consent_store.recently_granted_msme_ids(limit=5)
    recent_assessments = [build_list_item(store, consent_store, mid) for mid in recent_ids]

    return DashboardMetrics(
        totalMsmes=len(store.all_ids()),
        averageScore=round(sum(scores) / len(scores), 1) if scores else 0.0,
        excellentCount=excellent,
        goodCount=good,
        requiringReviewCount=requiring_review,
        publicOnlyCount=public_only_count,
        consentEnhancedCount=consent_enhanced_count,
        sectorDistribution=sector_distribution,
        riskDistribution=risk_distribution,
        recentAssessments=recent_assessments,
    )
