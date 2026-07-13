"""Risk band boundaries — pure lookup, no LLM, no randomness."""
from app.scoring.models import RiskBand

# (lower_bound_inclusive, upper_bound_inclusive, band)
_BANDS: list[tuple[int, int, RiskBand]] = [
    (0, 29, RiskBand.HIGH_RISK),
    (30, 44, RiskBand.BAD),
    (45, 59, RiskBand.AVERAGE),
    (60, 79, RiskBand.GOOD),
    (80, 100, RiskBand.EXCELLENT),
]

BAND_MULTIPLIERS: dict[RiskBand, float] = {
    RiskBand.HIGH_RISK: 0.0,
    RiskBand.BAD: 0.25,
    RiskBand.AVERAGE: 0.50,
    RiskBand.GOOD: 0.80,
    RiskBand.EXCELLENT: 1.00,
}


def band_for_score(score: int) -> RiskBand:
    score = max(0, min(100, score))
    for lower, upper, band in _BANDS:
        if lower <= score <= upper:
            return band
    raise ValueError(f"score out of range: {score}")


def multiplier_for_band(band: RiskBand) -> float:
    return BAND_MULTIPLIERS[band]
