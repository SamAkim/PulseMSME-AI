"""Deterministic rule-based template fallbacks — used whenever no LLM
provider is configured or every provider call fails. The app must remain
fully functional and coherent with zero API keys.
"""
from __future__ import annotations

from app.models.schemas import EnhancedScoreResult, MsmeMaster, PublicScoreResult


def health_summary_template(
    master: MsmeMaster,
    public_score: PublicScoreResult | None,
    enhanced_score: EnhancedScoreResult | None,
) -> str:
    parts = [f"{master.business_name} is a {master.business_age_years:.0f}-year-old {master.sector.lower()} business in {master.city}."]

    if enhanced_score is not None:
        parts.append(
            f"Based on consent-based financial data, it scores {enhanced_score.finalScore}/100 "
            f"({enhanced_score.riskBand.value} band) with {enhanced_score.confidenceScore}% confidence."
        )
        if enhanced_score.positiveFactors:
            parts.append("Key strengths: " + "; ".join(enhanced_score.positiveFactors[:2]) + ".")
        if enhanced_score.riskFactors and "No material risk" not in enhanced_score.riskFactors[0]:
            parts.append("Key risks: " + "; ".join(enhanced_score.riskFactors[:2]) + ".")
    elif public_score is not None:
        parts.append(
            f"Public signals alone indicate a preliminary score of {public_score.preliminaryScore}/100 "
            f"at {public_score.confidencePercentage}% confidence ({public_score.confidenceLabel}). "
            "Consent-based data has not yet been granted for a full assessment."
        )
    return " ".join(parts)


def recommendation_narrative_template(product: str, justification: str, risk_band_value: str) -> str:
    return (
        f"{product} is recommended given the {risk_band_value} risk classification. {justification} "
        "This recommendation is data-driven and indicative; it requires bank policy review before "
        "any offer is extended."
    )


def chat_fallback_template(question: str) -> str:
    return (
        "I can only answer using the data available for this MSME's assessment. "
        "Based on the current scoring output, I don't have a configured language model to "
        "generate a free-form answer to that question right now, but you can review the "
        "Enhanced Health Card and Recommendation screens for the underlying figures that "
        "would inform an answer to: \"" + question.strip() + "\""
    )
