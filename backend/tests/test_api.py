from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_config_endpoint():
    r = client.get("/api/config")
    assert r.status_code == 200
    body = r.json()
    assert body["appName"] == "PulseMSME AI"


def test_list_msmes_returns_twenty():
    r = client.get("/api/msme")
    assert r.status_code == 200
    assert len(r.json()) == 20


def test_msme_not_found_returns_404():
    r = client.get("/api/msme/NOPE999")
    assert r.status_code == 404


def test_public_assessment_capped_confidence():
    r = client.get("/api/msme/MSME001/public-assessment")
    assert r.status_code == 200
    body = r.json()
    assert body["confidencePercentage"] <= 70


def test_consent_then_assess_flow():
    consent_resp = client.post("/api/msme/MSME001/consent", json={"sources": ["gst", "upi", "aa_banking", "epfo"]})
    assert consent_resp.status_code == 200
    assert consent_resp.json()["consentStatus"] == "granted"

    assess_resp = client.post("/api/msme/MSME001/assess")
    assert assess_resp.status_code == 200
    body = assess_resp.json()
    assert body["enhancedScore"]["finalScore"] == 77
    assert body["enhancedScore"]["riskBand"] == "Good"
    assert body["recommendation"]["product"] is not None
    assert len(body["agentLog"]) == 8


def test_assess_without_consent_has_no_enhanced_score():
    r = client.post("/api/msme/MSME999_UNUSED/assess")
    assert r.status_code == 404


def test_chat_returns_reply_without_llm_keys():
    r = client.post("/api/msme/MSME001/chat", json={"message": "Why is this MSME classified as good?"})
    assert r.status_code == 200
    body = r.json()
    assert body["usedLlm"] is False
    assert len(body["reply"]) > 0


def test_dashboard_metrics_shape():
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    body = r.json()
    assert body["totalMsmes"] == 20
    assert set(body["riskDistribution"].keys()) <= {"High Risk", "Bad", "Average", "Good", "Excellent"}


def test_report_endpoint():
    r = client.get("/api/msme/MSME005/report")
    assert r.status_code == 200
    body = r.json()
    assert "Indicative assessment" in body["disclaimer"]
