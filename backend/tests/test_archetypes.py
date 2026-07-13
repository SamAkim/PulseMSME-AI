"""Each mandatory demo archetype must land in its expected risk band under
the deterministic scoring engine — this is the gate for Phase 2."""
import pytest

from app.data_store import get_data_store
from app.models.schemas import ConsentSource, RiskBand
from app.scoring.enhanced_score import compute_enhanced_score
from app.scoring.public_score import compute_public_score

ALL_SOURCES = list(ConsentSource)

EXPECTED_BANDS = {
    "MSME001": {RiskBand.GOOD, RiskBand.EXCELLENT},  # credit_invisible
    "MSME002": {RiskBand.BAD, RiskBand.AVERAGE},  # cash_flow_volatile
    "MSME003": {RiskBand.GOOD, RiskBand.EXCELLENT},  # digitally_weak (enhanced)
    "MSME004": {RiskBand.HIGH_RISK},  # high_risk
    "MSME005": {RiskBand.AVERAGE, RiskBand.GOOD},  # seasonal
}


@pytest.mark.parametrize("msme_id,expected_bands", EXPECTED_BANDS.items())
def test_archetype_lands_in_expected_band(msme_id, expected_bands):
    store = get_data_store()
    master = store.master[msme_id]
    public = store.public[msme_id]
    consent = store.consent[msme_id]

    result = compute_enhanced_score(master, public, consent, ALL_SOURCES, [])
    assert result.riskBand in expected_bands, (
        f"{msme_id} ({master.archetype.value}) scored {result.finalScore} "
        f"-> {result.riskBand}, expected one of {expected_bands}"
    )


def test_digitally_weak_public_score_is_low_but_enhanced_is_good():
    store = get_data_store()
    msme_id = "MSME003"
    master = store.master[msme_id]
    public = store.public[msme_id]
    consent = store.consent[msme_id]

    public_result = compute_public_score(master, public)
    enhanced_result = compute_enhanced_score(master, public, consent, ALL_SOURCES, [])

    assert public_result.preliminaryScore < 45
    assert enhanced_result.finalScore >= 60
    assert enhanced_result.finalScore - public_result.preliminaryScore >= 20


def test_credit_invisible_has_no_traditional_credit_history():
    store = get_data_store()
    master = store.master["MSME001"]
    assert master.credit_history_available is False


def test_seasonal_has_high_sales_variance():
    store = get_data_store()
    consent = store.consent["MSME005"]
    assert consent.gst_sales_variance >= 50


def test_high_risk_has_falling_turnover_and_bounces():
    store = get_data_store()
    consent = store.consent["MSME004"]
    assert consent.gst_turnover_growth_percentage < 0
    assert consent.cheque_bounce_count >= 3
    assert consent.gst_filing_timeliness_percentage < 70
