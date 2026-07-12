"""Layer 2 — enhanced six-dimension score. Pure Python, no LLM.

Dimension weights (fixed by the build contract):
  Cash-flow stability 25 · Compliance & discipline 20 · Revenue & growth 20
  · Repayment capacity 20 · Operational stability 10 · Digital reputation 5
"""
from __future__ import annotations

from app.models.schemas import ConsentFinancialSignals, ConsentSource, MsmeMaster, PublicSignals
from app.scoring.models import EnhancedScoreDimensions, EnhancedScoreResult
from app.scoring.risk_bands import band_for_score


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _cash_flow_stability(c: ConsentFinancialSignals) -> float:
    surplus_ratio = _clamp01((c.monthly_cash_surplus / max(c.average_monthly_bank_credit, 1)) / 0.5)
    volatility_score = 1 - _clamp01(c.cash_flow_volatility / 60)
    bounce_score = 1 - _clamp01(c.cheque_bounce_count / 10)
    failure_score = 1 - _clamp01(c.payment_failure_percentage / 20)
    fraction = 0.35 * surplus_ratio + 0.30 * volatility_score + 0.20 * bounce_score + 0.15 * failure_score
    return 25 * _clamp01(fraction)


def _compliance(c: ConsentFinancialSignals, m: MsmeMaster, p: PublicSignals) -> float:
    gst_component = c.gst_filing_timeliness_percentage / 100
    epfo_component = c.epfo_contribution_timeliness_percentage / 100
    udyam_component = 1.0 if m.udyam_registered else 0.4
    listing_component = p.business_listing_consistency / 100
    fraction = 0.40 * gst_component + 0.30 * epfo_component + 0.15 * udyam_component + 0.15 * listing_component
    return 20 * _clamp01(fraction)


def _revenue_and_growth(c: ConsentFinancialSignals) -> float:
    turnover_level = _clamp01(c.annual_gst_turnover / 20_000_000)
    gst_growth = _clamp01((c.gst_turnover_growth_percentage + 20) / 60)
    upi_growth = _clamp01((c.upi_inflow_growth_percentage + 20) / 60)
    epfo_growth = _clamp01((c.epfo_employee_growth_percentage + 20) / 60)
    growth_composite = (gst_growth + upi_growth + epfo_growth) / 3
    fraction = 0.5 * turnover_level + 0.5 * growth_composite
    return 20 * _clamp01(fraction)


def _repayment_capacity(c: ConsentFinancialSignals) -> float:
    obligation_ratio = c.existing_monthly_loan_obligation / max(c.average_monthly_bank_credit, 1)
    obligation_score = 1 - _clamp01(obligation_ratio / 0.5)
    buffer_score = _clamp01(
        (c.monthly_cash_surplus / max(c.existing_monthly_loan_obligation, 1)) / 3
    ) if c.existing_monthly_loan_obligation > 0 else 1.0
    balance_score = _clamp01(c.average_monthly_balance / max(c.average_monthly_bank_credit * 0.5, 1))
    fraction = 0.4 * obligation_score + 0.35 * buffer_score + 0.25 * balance_score
    return 20 * _clamp01(fraction)


def _operational_stability(c: ConsentFinancialSignals, m: MsmeMaster) -> float:
    age_score = _clamp01(m.business_age_years / 10)
    employee_score = _clamp01(c.epfo_employee_count / 20)
    txn_score = _clamp01(c.upi_transaction_count / 1000)
    seasonal_score = 1 - _clamp01(c.gst_sales_variance / 60)
    fraction = 0.30 * age_score + 0.25 * employee_score + 0.20 * txn_score + 0.25 * seasonal_score
    return 10 * _clamp01(fraction)


def _digital_reputation(p: PublicSignals) -> float:
    rating_score = p.google_rating / 5
    sentiment_score = (p.review_sentiment_score + 1) / 2
    listing_score = p.business_listing_consistency / 100
    presence_score = 1.0 if p.website_present else 0.3
    fraction = 0.35 * rating_score + 0.25 * sentiment_score + 0.20 * listing_score + 0.20 * presence_score
    return 5 * _clamp01(fraction)


def confidence_for_sources(granted_sources: list[ConsentSource]) -> int:
    return min(100, round(50 + 12.5 * len(granted_sources)))


def compute_enhanced_score(
    master: MsmeMaster,
    public: PublicSignals,
    consent: ConsentFinancialSignals,
    granted_sources: list[ConsentSource],
    missing_data: list[str],
) -> EnhancedScoreResult:
    cash_flow = _cash_flow_stability(consent)
    compliance = _compliance(consent, master, public)
    revenue = _revenue_and_growth(consent)
    repayment = _repayment_capacity(consent)
    operational = _operational_stability(consent, master)
    digital = _digital_reputation(public)

    dimensions = EnhancedScoreDimensions(
        cashFlowStability=round(cash_flow, 1),
        compliance=round(compliance, 1),
        revenueAndGrowth=round(revenue, 1),
        repaymentCapacity=round(repayment, 1),
        operationalStability=round(operational, 1),
        digitalReputation=round(digital, 1),
    )
    final_score = int(round(cash_flow + compliance + revenue + repayment + operational + digital))
    final_score = max(0, min(100, final_score))
    risk_band = band_for_score(final_score)
    confidence = confidence_for_sources(granted_sources)

    positives: list[str] = []
    risks: list[str] = []

    if consent.gst_filing_timeliness_percentage >= 90:
        positives.append(f"GST filing timeliness is {consent.gst_filing_timeliness_percentage:.0f}%, which lifted the compliance score")
    if consent.cash_flow_volatility <= 20:
        positives.append(f"Low cash-flow volatility ({consent.cash_flow_volatility:.0f}%) indicates stable inflows")
    if consent.gst_turnover_growth_percentage >= 10:
        positives.append(f"GST turnover growing at {consent.gst_turnover_growth_percentage:.0f}% year-on-year")
    if consent.monthly_cash_surplus > consent.existing_monthly_loan_obligation * 2:
        positives.append("Healthy monthly cash surplus relative to existing obligations")
    if consent.epfo_contribution_timeliness_percentage >= 90:
        positives.append("Consistent EPFO contribution timeliness, indicating stable payroll discipline")

    if consent.cash_flow_volatility > 40:
        risks.append(f"Cash-flow volatility of {consent.cash_flow_volatility:.0f}% reduced cash-flow stability")
    if consent.cheque_bounce_count > 2:
        risks.append(f"{consent.cheque_bounce_count} cheque bounces recorded in the review period")
    if consent.payment_failure_percentage > 8:
        risks.append(f"Payment failure rate of {consent.payment_failure_percentage:.0f}% is elevated")
    if consent.gst_turnover_growth_percentage < 0:
        risks.append(f"GST turnover declining at {abs(consent.gst_turnover_growth_percentage):.0f}% year-on-year")
    if consent.gst_filing_timeliness_percentage < 70:
        risks.append(f"GST filing timeliness of {consent.gst_filing_timeliness_percentage:.0f}% is below acceptable range")
    if consent.existing_monthly_loan_obligation > consent.average_monthly_bank_credit * 0.4:
        risks.append("Existing loan obligations consume a large share of monthly inflow")
    if not risks:
        risks.append("No material risk signals detected in consent-based data")

    return EnhancedScoreResult(
        finalScore=final_score,
        riskBand=risk_band,
        confidenceScore=confidence,
        dimensions=dimensions,
        positiveFactors=positives,
        riskFactors=risks,
        missingData=missing_data,
    )
