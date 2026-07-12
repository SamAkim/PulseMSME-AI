"""Indicative loan eligibility — secondary feature, deterministic formula.

  turnover_limit  = annual_gst_turnover x 0.20
  cash_flow_limit = monthly_cash_surplus x 12
  base            = min(turnover_limit, cash_flow_limit)
  final           = base x band multiplier, clamped to [50,000, 50,00,000]
"""
from __future__ import annotations

from app.models.schemas import ConsentFinancialSignals, DISCLAIMER, LoanEligibility, RiskBand
from app.scoring.risk_bands import multiplier_for_band

MIN_AMOUNT = 50_000
MAX_AMOUNT = 50_00_000


def compute_loan_eligibility(consent: ConsentFinancialSignals, risk_band: RiskBand) -> LoanEligibility:
    turnover_limit = consent.annual_gst_turnover * 0.20
    cash_flow_limit = max(consent.monthly_cash_surplus, 0) * 12
    base = min(turnover_limit, cash_flow_limit)
    multiplier = multiplier_for_band(risk_band)
    raw_final = base * multiplier

    eligible = multiplier > 0 and raw_final >= MIN_AMOUNT
    final_amount = max(MIN_AMOUNT, min(MAX_AMOUNT, raw_final)) if eligible else 0.0

    tenure_map: dict[RiskBand, tuple[int, int]] = {
        RiskBand.HIGH_RISK: (0, 0),
        RiskBand.BAD: (6, 12),
        RiskBand.AVERAGE: (12, 24),
        RiskBand.GOOD: (12, 36),
        RiskBand.EXCELLENT: (12, 48),
    }

    explanation = (
        f"turnover_limit = annual_gst_turnover (Rs.{consent.annual_gst_turnover:,.0f}) x 0.20 = "
        f"Rs.{turnover_limit:,.0f}; cash_flow_limit = monthly_cash_surplus (Rs.{consent.monthly_cash_surplus:,.0f}) "
        f"x 12 = Rs.{cash_flow_limit:,.0f}; base = min(turnover_limit, cash_flow_limit) = Rs.{base:,.0f}; "
        f"final = base x {risk_band.value} multiplier ({multiplier:.2f}) = Rs.{raw_final:,.0f}, "
        f"clamped to [Rs.{MIN_AMOUNT:,.0f}, Rs.{MAX_AMOUNT:,.0f}]."
    )

    return LoanEligibility(
        eligible=eligible,
        indicativeAmount=round(final_amount, -3) if eligible else 0.0,
        turnoverLimit=round(turnover_limit, 2),
        cashFlowLimit=round(cash_flow_limit, 2),
        baseAmount=round(base, 2),
        bandMultiplier=multiplier,
        tenureRangeMonths=tenure_map[risk_band],
        formulaExplanation=explanation,
        disclaimer=DISCLAIMER,
    )
