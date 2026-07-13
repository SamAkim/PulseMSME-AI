"""Financial Scoring Agent — Node 2.

Calls the deterministic scoring engine only. No LLM. Computes the Layer 1
public score always, and the Layer 2 enhanced score once at least one
consent source has been granted and its data ingested.
"""
from __future__ import annotations

from collections.abc import Callable

from app.agents._util import log_status
from app.data_store import DataStore
from app.models.schemas import AssessmentState
from app.scoring.enhanced_score import compute_enhanced_score
from app.scoring.public_score import compute_public_score


def build_scoring_node(store: DataStore) -> Callable[[AssessmentState], dict]:
    def scoring_node(state: AssessmentState) -> dict:
        log = log_status(state.agentLog, "Financial Scoring Agent", "running", "Computing deterministic scores")

        master = store.master.get(state.msmeId)
        public = store.public.get(state.msmeId)
        consent = store.consent.get(state.msmeId)

        if master is None or public is None:
            log = log_status(log, "Financial Scoring Agent", "error", "Missing base MSME data")
            return {"agentLog": log}

        public_score = compute_public_score(master, public)

        enhanced_score = None
        if state.grantedSources and consent is not None:
            enhanced_score = compute_enhanced_score(
                master, public, consent, state.grantedSources, state.missingSources
            )

        message = f"Public score {public_score.preliminaryScore}/100"
        if enhanced_score is not None:
            message += f"; enhanced score {enhanced_score.finalScore}/100 ({enhanced_score.riskBand.value})"

        log = log_status(log, "Financial Scoring Agent", "completed", message)

        return {"publicScore": public_score, "enhancedScore": enhanced_score, "agentLog": log}

    return scoring_node
