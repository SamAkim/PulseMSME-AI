from app.scoring.public_score import compute_public_score


def test_public_score_within_bounds(base_master, base_public):
    result = compute_public_score(base_master, base_public)
    assert 0 <= result.preliminaryScore <= 100
    assert 25 <= result.confidencePercentage <= 70


def test_confidence_never_exceeds_70(base_master, base_public):
    base_public.digital_activity_score = 100.0
    base_public.social_engagement_rate = 10.0
    base_public.website_quality_score = 100.0
    result = compute_public_score(base_master, base_public)
    assert result.confidencePercentage <= 70


def test_strong_signals_yield_higher_score_than_weak_signals(base_master, base_public):
    strong = compute_public_score(base_master, base_public)

    weak_public = base_public.model_copy(update={
        "google_rating": 2.0, "positive_review_percentage": 30.0, "review_sentiment_score": -0.5,
        "website_present": False, "website_quality_score": 0.0, "business_listing_consistency": 20.0,
        "digital_activity_score": 10.0, "social_media_followers": 50, "social_engagement_rate": 0.1,
        "google_review_count": 3,
    })
    weak = compute_public_score(base_master, weak_public)
    assert strong.preliminaryScore > weak.preliminaryScore


def test_no_website_triggers_warning(base_master, base_public):
    base_public.website_present = False
    result = compute_public_score(base_master, base_public)
    assert any("website" in w.lower() for w in result.warningIndicators)


def test_component_scores_present(base_master, base_public):
    result = compute_public_score(base_master, base_public)
    expected_keys = {
        "customerReputation", "digitalPresence", "businessMaturity",
        "engagementActivity", "listingConsistency",
    }
    assert expected_keys == set(result.componentScores.keys())
