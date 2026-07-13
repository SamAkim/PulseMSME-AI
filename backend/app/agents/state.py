"""LangGraph pipeline state.

The canonical AssessmentState definition lives in app.models.schemas (the
single source of truth shared with API contracts, per the build contract).
Re-exported here so agent code reads naturally.
"""
from app.models.schemas import AgentStatus, AssessmentState  # noqa: F401

ALL_AGENT_NAMES = [
    "Data Ingestion Agent",
    "Financial Scoring Agent",
    "Risk & Insight Agent",
    "Credit Recommendation Agent",
]
