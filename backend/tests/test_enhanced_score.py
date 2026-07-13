from app.models.schemas import ConsentSource
from app.scoring.enhanced_score import compute_enhanced_score, confidence_for_sources

ALL_SOURCES = list(ConsentSource)


def test_enhanced_score_within_bounds(base_master, base_public, base_consent):
    result = compute_enhanced_score(base_master, base_public, base_consent, ALL_SOURCES, [])
    assert 0 <= result.finalScore <= 100


def test_dimension_points_respect_weight_ceilings(base_master, base_public, base_consent):
    result = compute_enhanced_score(base_master, base_public, base_consent, ALL_SOURCES, [])
    d = result.dimensions
    assert 0 <= d.cashFlowStability <= 25
    assert 0 <= d.compliance <= 20
    assert 0 <= d.revenueAndGrowth <= 20
    assert 0 <= d.repaymentCapacity <= 20
    assert 0 <= d.operationalStability <= 10
    assert 0 <= d.digitalReputation <= 5


def test_final_score_equals_sum_of_dimensions(base_master, base_public, base_consent):
    result = compute_enhanced_score(base_master, base_public, base_consent, ALL_SOURCES, [])
    d = result.dimensions
    total = (
        d.cashFlowStability + d.compliance + d.revenueAndGrowth
        + d.repaymentCapacity + d.operationalStability + d.digitalReputation
    )
    assert abs(result.finalScore - total) < 1.0


def test_deteriorating_signals_lower_the_score(base_master, base_public, base_consent):
    healthy = compute_enhanced_score(base_master, base_public, base_consent, ALL_SOURCES, [])

    stressed = base_consent.model_copy(update={
        "cash_flow_volatility": 60.0, "cheque_bounce_count": 8, "payment_failure_percentage": 20.0,
        "gst_filing_timeliness_percentage": 30.0, "gst_turnover_growth_percentage": -15.0,
        "monthly_cash_surplus": -5000.0, "existing_monthly_loan_obligation": 200000.0,
    })
    distressed = compute_enhanced_score(base_master, base_public, stressed, ALL_SOURCES, [])
    assert distressed.finalScore < healthy.finalScore


def test_confidence_for_sources_scales_with_grant_count():
    assert confidence_for_sources([]) == 50
    assert confidence_for_sources(ALL_SOURCES) == 100
    assert confidence_for_sources(ALL_SOURCES[:1]) < confidence_for_sources(ALL_SOURCES[:2])


def test_missing_data_passthrough(base_master, base_public, base_consent):
    result = compute_enhanced_score(
        base_master, base_public, base_consent, ALL_SOURCES[:1], ["epfo", "aa_banking"]
    )
    assert result.missingData == ["epfo", "aa_banking"]
