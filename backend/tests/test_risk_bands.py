import pytest

from app.scoring.risk_bands import band_for_score, multiplier_for_band
from app.scoring.models import RiskBand


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, RiskBand.HIGH_RISK),
        (29, RiskBand.HIGH_RISK),
        (30, RiskBand.BAD),
        (44, RiskBand.BAD),
        (45, RiskBand.AVERAGE),
        (59, RiskBand.AVERAGE),
        (60, RiskBand.GOOD),
        (79, RiskBand.GOOD),
        (80, RiskBand.EXCELLENT),
        (100, RiskBand.EXCELLENT),
    ],
)
def test_band_boundaries(score, expected):
    assert band_for_score(score) == expected


def test_band_clamps_out_of_range_scores():
    assert band_for_score(-5) == RiskBand.HIGH_RISK
    assert band_for_score(150) == RiskBand.EXCELLENT


def test_multipliers_are_monotonic_and_bounded():
    ordered = [
        RiskBand.HIGH_RISK, RiskBand.BAD, RiskBand.AVERAGE, RiskBand.GOOD, RiskBand.EXCELLENT,
    ]
    multipliers = [multiplier_for_band(b) for b in ordered]
    assert multipliers == sorted(multipliers)
    assert multipliers[0] == 0.0
    assert multipliers[-1] == 1.0
