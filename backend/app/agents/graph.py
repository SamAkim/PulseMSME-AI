"""LangGraph StateGraph wiring the four pipeline agents sequentially.

    ingestion -> scoring -> risk_insight -> recommendation

Exposes both a synchronous (non-streaming) run and an async generator that
streams per-node AgentStatus events for the SSE endpoint.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.adapters.aa_banking import MockAaBankingAdapter
from app.adapters.epfo import MockEpfoAdapter
from app.adapters.gst import MockGstAdapter
from app.adapters.upi import MockUpiAdapter
from app.agents.ingestion import build_ingestion_node
from app.agents.recommendation import build_recommendation_node
from app.agents.risk_insight import build_risk_insight_node
from app.agents.scoring_agent import build_scoring_node
from app.data_store import DataStore, get_data_store
from app.models.schemas import AgentStatus, AssessmentState, ConsentSource


def _build_compiled_graph(store: DataStore):
    gst_adapter = MockGstAdapter(store)
    upi_adapter = MockUpiAdapter(store)
    aa_adapter = MockAaBankingAdapter(store)
    epfo_adapter = MockEpfoAdapter(store)

    builder = StateGraph(AssessmentState)
    builder.add_node("ingestion", build_ingestion_node(store, gst_adapter, upi_adapter, aa_adapter, epfo_adapter))
    builder.add_node("scoring", build_scoring_node(store))
    builder.add_node("risk_insight", build_risk_insight_node(store))
    builder.add_node("recommendation", build_recommendation_node(store))

    builder.add_edge(START, "ingestion")
    builder.add_edge("ingestion", "scoring")
    builder.add_edge("scoring", "risk_insight")
    builder.add_edge("risk_insight", "recommendation")
    builder.add_edge("recommendation", END)

    return builder.compile()


@lru_cache
def get_pipeline_graph():
    return _build_compiled_graph(get_data_store())


def _initial_state(msme_id: str, granted_sources: list[ConsentSource]) -> AssessmentState:
    return AssessmentState(msmeId=msme_id, grantedSources=granted_sources)


async def run_pipeline(msme_id: str, granted_sources: list[ConsentSource]) -> AssessmentState:
    graph = get_pipeline_graph()
    result = await graph.ainvoke(_initial_state(msme_id, granted_sources))
    return AssessmentState.model_validate(result)


async def stream_pipeline(
    msme_id: str, granted_sources: list[ConsentSource]
) -> AsyncGenerator[tuple[str, AgentStatus | AssessmentState], None]:
    """Yields ("status", AgentStatus) for each agent-log entry as it appears,
    then a final ("result", AssessmentState) once the graph completes."""
    graph = get_pipeline_graph()
    initial = _initial_state(msme_id, granted_sources)
    prev_log_len = 0
    final_state = initial

    async for snapshot in graph.astream(initial, stream_mode="values"):
        state = AssessmentState.model_validate(snapshot)
        for entry in state.agentLog[prev_log_len:]:
            yield ("status", entry)
        prev_log_len = len(state.agentLog)
        final_state = state

    yield ("result", final_state)
