from app.models.schemas import RiskBand
from app.scoring.loan_eligibility import MAX_AMOUNT, MIN_AMOUNT, compute_loan_eligibility


def test_high_risk_band_is_ineligible(base_consent):
    result = compute_loan_eligibility(base_consent, RiskBand.HIGH_RISK)
    assert result.eligible is False
    assert result.indicativeAmount == 0.0
    assert result.bandMultiplier == 0.0


def test_excellent_band_uses_full_multiplier(base_consent):
    result = compute_loan_eligibility(base_consent, RiskBand.EXCELLENT)
    assert result.bandMultiplier == 1.0
    expected_base = min(
        base_consent.annual_gst_turnover * 0.20, base_consent.monthly_cash_surplus * 12
    )
    assert abs(result.baseAmount - expected_base) < 1.0


def test_amount_clamped_to_bounds(base_consent):
    huge = base_consent.model_copy(update={
        "annual_gst_turnover": 500_000_000.0, "monthly_cash_surplus": 5_000_000.0,
    })
    result = compute_loan_eligibility(huge, RiskBand.EXCELLENT)
    assert result.indicativeAmount <= MAX_AMOUNT

    tiny = base_consent.model_copy(update={
        "annual_gst_turnover": 100_000.0, "monthly_cash_surplus": 1000.0,
    })
    tiny_result = compute_loan_eligibility(tiny, RiskBand.AVERAGE)
    assert tiny_result.indicativeAmount == 0.0 or tiny_result.indicativeAmount >= MIN_AMOUNT


def test_formula_uses_min_of_two_limits(base_consent):
    result = compute_loan_eligibility(base_consent, RiskBand.GOOD)
    turnover_limit = base_consent.annual_gst_turnover * 0.20
    cash_flow_limit = base_consent.monthly_cash_surplus * 12
    assert result.baseAmount == round(min(turnover_limit, cash_flow_limit), 2)


def test_disclaimer_always_attached(base_consent):
    for band in RiskBand:
        result = compute_loan_eligibility(base_consent, band)
        assert "Indicative assessment" in result.disclaimer
