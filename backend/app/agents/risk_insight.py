"""Risk & Insight Agent — Node 3.

Derives top positive indicators, top risks, and anomalies/conflicting
signals via rules. Invokes the LLM only to phrase the natural-language
health summary, with a deterministic template fallback.
"""
from __future__ import annotations

from collections.abc import Callable

from app.agents._util import log_status
from app.data_store import DataStore
from app.llm.prompts import build_health_summary_prompt
from app.llm.provider import generate_text
from app.llm.templates import health_summary_template
from app.models.schemas import AssessmentState

MAX_INDICATORS = 5


def _detect_anomalies(state: AssessmentState, consent_available: bool) -> list[str]:
    anomalies: list[str] = []
    ps, es = state.publicScore, state.enhancedScore

    if ps is not None and es is not None:
        gap = es.finalScore - ps.preliminaryScore
        if gap >= 25:
            anomalies.append(
                "Public digital signals understated this business — consent-based data revealed "
                "materially stronger financial health than public presence suggested."
            )
        elif gap <= -20:
            anomalies.append(
                "Consent-based financial data is weaker than the public digital presence suggested — "
                "review for possible reputation/financial-health mismatch."
            )

    if es is not None:
        if es.dimensions.revenueAndGrowth >= 14 and es.dimensions.cashFlowStability <= 8:
            anomalies.append("Strong revenue growth is not translating into stable cash flow — worth probing.")
        if es.dimensions.compliance >= 16 and es.dimensions.repaymentCapacity <= 6:
            anomalies.append("High compliance discipline but low repayment buffer — obligations may be tight.")

    if not consent_available:
        anomalies.append("Assessment is based on public signals only — no consent-based data available yet.")

    return anomalies


def build_risk_insight_node(store: DataStore) -> Callable[[AssessmentState], dict]:
    async def risk_insight_node(state: AssessmentState) -> dict:
        log = log_status(state.agentLog, "Risk & Insight Agent", "running", "Deriving risk and strength signals")

        master = store.master.get(state.msmeId)
        positives: list[str] = []
        risks: list[str] = []

        if state.publicScore is not None:
            positives.extend(state.publicScore.positiveIndicators)
            risks.extend(state.publicScore.warningIndicators)
        if state.enhancedScore is not None:
            positives.extend(state.enhancedScore.positiveFactors)
            risks.extend(state.enhancedScore.riskFactors)

        # De-duplicate while preserving order, cap to top N for UI focus.
        positives = list(dict.fromkeys(positives))[:MAX_INDICATORS]
        risks = list(dict.fromkeys(risks))[:MAX_INDICATORS]

        anomalies = _detect_anomalies(state, consent_available=state.enhancedScore is not None)

        summary = ""
        used_llm = False
        if master is not None:
            context = {
                "businessName": master.business_name,
                "sector": master.sector,
                "city": master.city,
                "businessAgeYears": master.business_age_years,
                "publicScore": state.publicScore.model_dump() if state.publicScore else None,
                "enhancedScore": state.enhancedScore.model_dump() if state.enhancedScore else None,
                "positiveIndicators": positives,
                "riskIndicators": risks,
            }
            system_prompt, user_prompt = build_health_summary_prompt(context)
            llm_text, used_llm = await generate_text(system_prompt, user_prompt)
            summary = llm_text or health_summary_template(master, state.publicScore, state.enhancedScore)

        log = log_status(
            log, "Risk & Insight Agent", "completed",
            f"Identified {len(positives)} strengths, {len(risks)} risks"
            + (" (LLM summary)" if used_llm else " (template summary)"),
        )

        return {
            "positiveIndicators": positives,
            "riskIndicators": risks,
            "anomalies": anomalies,
            "healthSummary": summary,
            "agentLog": log,
        }

    return risk_insight_node
