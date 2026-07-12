"""Credit Recommendation Agent — Node 4.

Picks a product via rules, computes optional indicative eligibility via
the deterministic loan_eligibility module, recommends a next action,
lists missing documents/verifications, and states the rationale (LLM
narrative with a deterministic template fallback).
"""
from __future__ import annotations

from collections.abc import Callable

from app.agents._util import log_status
from app.data_store import DataStore
from app.llm.prompts import build_recommendation_narrative_prompt
from app.llm.provider import generate_text
from app.llm.templates import recommendation_narrative_template
from app.models.schemas import (
    DISCLAIMER,
    AssessmentState,
    ConsentSource,
    EnhancedScoreResult,
    MsmeMaster,
    ProductRecommendation,
    RiskBand,
)
from app.scoring.loan_eligibility import compute_loan_eligibility

SOURCE_DOCS = {
    ConsentSource.GST: "GST returns / GSTIN verification",
    ConsentSource.UPI: "UPI settlement statement",
    ConsentSource.AA_BANKING: "Bank statements via Account Aggregator",
    ConsentSource.EPFO: "EPFO establishment contribution history",
}


def _pick_product(master: MsmeMaster, es: EnhancedScoreResult, consent) -> tuple[str, str]:
    if es.riskBand == RiskBand.HIGH_RISK:
        return "Manual Underwriting Required", (
            "Risk indicators (falling turnover, compliance lapses, or payment failures) require "
            "full manual credit review before any product can be offered."
        )
    if consent.gst_sales_variance >= 50:
        return "Seasonal Working Capital Facility", (
            f"GST sales variance of {consent.gst_sales_variance:.0f}% indicates strong seasonal "
            "demand concentration, best served by a facility sized to peak-season working capital needs."
        )
    if consent.cash_flow_volatility >= 40 and es.riskBand in (RiskBand.BAD, RiskBand.AVERAGE):
        return "Merchant Cash-Flow Loan", (
            f"Cash-flow volatility of {consent.cash_flow_volatility:.0f}% suggests a revenue-linked "
            "repayment structure fits better than a fixed-instalment loan."
        )
    if not master.credit_history_available and es.riskBand in (RiskBand.GOOD, RiskBand.EXCELLENT):
        return "Working Capital Loan", (
            "No traditional credit history exists, but consent-based GST and UPI data shows strong, "
            "consistent inflows that support a standard working capital facility."
        )
    if consent.average_monthly_upi_inflow > consent.average_monthly_gst_turnover * 0.5 and es.riskBand in (
        RiskBand.GOOD, RiskBand.EXCELLENT,
    ):
        return "Invoice Financing", (
            "High-frequency digital receivables (UPI inflows) relative to GST turnover suggest "
            "invoice/receivables-based financing would suit this business's cash cycle."
        )
    if consent.epfo_employee_growth_percentage >= 15 and es.riskBand == RiskBand.EXCELLENT:
        return "Equipment Finance", (
            "Strong employee growth alongside an excellent risk band indicates capacity expansion — "
            "equipment finance supports that growth directly."
        )
    if es.riskBand == RiskBand.EXCELLENT:
        return "Small Business Term Loan", (
            "Consistently strong performance across all six dimensions supports a standard term loan."
        )
    if es.riskBand == RiskBand.BAD:
        return "Secured Credit Review", (
            "Below-average risk indicators suggest unsecured lending is premature; a secured "
            "facility with collateral review is the more prudent path."
        )
    return "Working Capital Loan", (
        f"{es.riskBand.value} overall risk classification supports a standard working capital facility."
    )


def build_recommendation_node(store: DataStore) -> Callable[[AssessmentState], dict]:
    async def recommendation_node(state: AssessmentState) -> dict:
        log = log_status(
            state.agentLog, "Credit Recommendation Agent", "running", "Selecting product and computing eligibility"
        )

        master = store.master.get(state.msmeId)
        consent = store.consent.get(state.msmeId)

        if master is None:
            log = log_status(log, "Credit Recommendation Agent", "error", "Missing MSME master record")
            return {"agentLog": log}

        missing_docs = [SOURCE_DOCS[s] for s in ConsentSource if s not in state.grantedSources]

        if state.enhancedScore is None or consent is None:
            recommendation = ProductRecommendation(
                product="Preliminary Review Only",
                justification="Consent-based financial data has not been granted yet.",
                riskConditions=["Full assessment requires GST, UPI, banking, and EPFO consent"],
                requiredManualChecks=["Obtain MSME consent for all data sources before proceeding"],
                nextBestAction="Request consent-based assessment to unlock a product recommendation",
                rationale="No enhanced score is available without consent-based data.",
                eligibility=None,
                missingDocuments=missing_docs,
                disclaimer=DISCLAIMER,
            )
            log = log_status(log, "Credit Recommendation Agent", "completed", "Preliminary review only — consent required")
            return {"recommendation": recommendation, "agentLog": log}

        es = state.enhancedScore
        product, justification = _pick_product(master, es, consent)
        eligibility = compute_loan_eligibility(consent, es.riskBand)

        risk_conditions: list[str] = []
        if es.riskBand in (RiskBand.HIGH_RISK, RiskBand.BAD):
            risk_conditions.append("Requires senior credit officer sign-off")
        if consent.cheque_bounce_count > 0:
            risk_conditions.append(f"{consent.cheque_bounce_count} cheque bounce(s) on record — review before disbursal")
        if consent.payment_failure_percentage > 5:
            risk_conditions.append("Elevated payment failure rate — verify with additional bank statements")
        if not risk_conditions:
            risk_conditions.append("No elevated risk conditions beyond standard policy checks")

        manual_checks = ["Bureau data pull", "KYC and AML verification", "Bank policy compliance check"]
        if es.riskBand in (RiskBand.HIGH_RISK, RiskBand.BAD):
            manual_checks.append("Field verification visit recommended")

        next_action = (
            "Proceed to indicative offer generation and bureau pull"
            if es.riskBand in (RiskBand.GOOD, RiskBand.EXCELLENT)
            else "Route to manual underwriting for further review"
            if es.riskBand == RiskBand.HIGH_RISK
            else "Request additional supporting documents before proceeding"
        )

        context = {
            "businessName": master.business_name, "product": product, "riskBand": es.riskBand.value,
            "finalScore": es.finalScore, "justification": justification,
            "indicativeAmount": eligibility.indicativeAmount if eligibility.eligible else 0,
        }
        system_prompt, user_prompt = build_recommendation_narrative_prompt(context)
        llm_text, used_llm = await generate_text(system_prompt, user_prompt)
        rationale = llm_text or recommendation_narrative_template(product, justification, es.riskBand.value)

        recommendation = ProductRecommendation(
            product=product,
            justification=justification,
            riskConditions=risk_conditions,
            requiredManualChecks=manual_checks,
            nextBestAction=next_action,
            rationale=rationale,
            eligibility=eligibility,
            missingDocuments=missing_docs,
            disclaimer=DISCLAIMER,
        )

        log = log_status(
            log, "Credit Recommendation Agent", "completed",
            f"Recommended {product}" + (" (LLM rationale)" if used_llm else " (template rationale)"),
        )
        return {"recommendation": recommendation, "agentLog": log}

    return recommendation_node
