"""Layer 1 — public preliminary score. Pure Python, no LLM.

Weights (fixed by the build contract):
  Customer reputation 30% · Digital presence 25% · Business maturity 20%
  · Engagement & activity 15% · Listing consistency 10%
"""
from __future__ import annotations

from app.models.schemas import MsmeMaster, PublicSignals
from app.scoring.models import PublicScoreResult


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _reputation_subscore(p: PublicSignals) -> float:
    rating_component = (p.google_rating / 5.0) * 100
    sentiment_component = _clamp((p.review_sentiment_score + 1) / 2 * 100)
    return _clamp(0.4 * rating_component + 0.3 * p.positive_review_percentage + 0.3 * sentiment_component)


def _digital_presence_subscore(p: PublicSignals) -> float:
    website_component = p.website_quality_score if p.website_present else 0.0
    domain_age_component = _clamp(p.website_domain_age_years / 10 * 100)
    followers_component = _clamp(p.social_media_followers / 10000 * 100)
    engagement_component = _clamp(p.social_engagement_rate / 5 * 100)
    return _clamp(
        0.4 * website_component
        + 0.2 * domain_age_component
        + 0.2 * followers_component
        + 0.2 * engagement_component
    )


def _business_maturity_subscore(m: MsmeMaster) -> float:
    age_component = _clamp(m.business_age_years / 10 * 100)
    udyam_component = 100.0 if m.udyam_registered else 40.0
    employee_component = _clamp(m.employee_count / 20 * 100)
    return _clamp(0.5 * age_component + 0.3 * udyam_component + 0.2 * employee_component)


def _engagement_activity_subscore(p: PublicSignals) -> float:
    activity_component = p.digital_activity_score
    engagement_component = _clamp(p.social_engagement_rate / 5 * 100)
    review_volume_component = _clamp(p.google_review_count / 200 * 100)
    return _clamp(0.5 * activity_component + 0.25 * engagement_component + 0.25 * review_volume_component)


def _confidence(digital_subscore: float, engagement_subscore: float) -> tuple[int, str]:
    footprint_strength = (digital_subscore * 0.5 + engagement_subscore * 0.5) / 100
    percentage = round(25 + footprint_strength * 45)
    percentage = int(_clamp(percentage, 25, 70))
    if percentage <= 40:
        label = "Limited data"
    elif percentage <= 60:
        label = "Moderate footprint"
    else:
        label = "Strong footprint"
    return percentage, label


def compute_public_score(master: MsmeMaster, public: PublicSignals) -> PublicScoreResult:
    reputation = _reputation_subscore(public)
    digital = _digital_presence_subscore(public)
    maturity = _business_maturity_subscore(master)
    engagement = _engagement_activity_subscore(public)
    listing = _clamp(public.business_listing_consistency)

    weighted_total = (
        0.30 * reputation + 0.25 * digital + 0.20 * maturity + 0.15 * engagement + 0.10 * listing
    )
    preliminary_score = int(round(_clamp(weighted_total)))
    confidence_pct, confidence_label = _confidence(digital, engagement)

    positives: list[str] = []
    warnings: list[str] = []

    if public.google_rating >= 4.2 and public.positive_review_percentage >= 80:
        positives.append(
            f"Google rating of {public.google_rating:.1f} with {public.positive_review_percentage:.0f}% positive reviews"
        )
    if public.website_present and public.website_quality_score >= 65:
        positives.append(f"Well-maintained website (quality score {public.website_quality_score:.0f}/100)")
    if public.business_listing_consistency >= 80:
        positives.append("Business listings are highly consistent across public directories")
    if master.udyam_registered:
        positives.append("Udyam registered, indicating formal MSME recognition")
    if public.social_media_followers >= 5000:
        positives.append(f"Established social media presence ({public.social_media_followers:,} followers)")

    if not public.website_present:
        warnings.append("No website detected — limited digital footprint")
    elif public.website_quality_score < 40:
        warnings.append(f"Website quality is low ({public.website_quality_score:.0f}/100)")
    if public.google_review_count < 15:
        warnings.append(f"Very few public reviews ({public.google_review_count}) — low sample confidence")
    if public.positive_review_percentage < 60:
        warnings.append(f"Only {public.positive_review_percentage:.0f}% of reviews are positive")
    if public.business_listing_consistency < 50:
        warnings.append("Inconsistent business listings across public directories")
    if not warnings:
        warnings.append("No significant public-data warning signals detected")

    return PublicScoreResult(
        preliminaryScore=preliminary_score,
        confidenceLabel=confidence_label,  # type: ignore[arg-type]
        confidencePercentage=confidence_pct,
        componentScores={
            "customerReputation": round(reputation, 1),
            "digitalPresence": round(digital, 1),
            "businessMaturity": round(maturity, 1),
            "engagementActivity": round(engagement, 1),
            "listingConsistency": round(listing, 1),
        },
        positiveIndicators=positives,
        warningIndicators=warnings,
    )
