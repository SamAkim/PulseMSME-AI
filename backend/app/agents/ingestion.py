"""Data Ingestion Agent — Node 1.

Pulls the MSME's public data (always available) and consent data for
granted sources via the mock adapters, validates required fields, flags
missing fields, and normalizes completeness. No LLM, no scoring.
"""
from __future__ import annotations

from collections.abc import Callable

from app.adapters.aa_banking import AaBankingAdapter
from app.adapters.epfo import EpfoAdapter
from app.adapters.gst import GstAdapter
from app.adapters.upi import UpiAdapter
from app.agents._util import log_status
from app.data_store import DataStore
from app.models.schemas import AssessmentState, ConsentSource

SOURCE_LABELS = {
    ConsentSource.GST: "GST",
    ConsentSource.UPI: "UPI",
    ConsentSource.AA_BANKING: "Account Aggregator Banking",
    ConsentSource.EPFO: "EPFO",
}

TOTAL_CATEGORIES = 1 + len(ConsentSource)  # public + 4 consent sources


def build_ingestion_node(
    store: DataStore,
    gst_adapter: GstAdapter,
    upi_adapter: UpiAdapter,
    aa_adapter: AaBankingAdapter,
    epfo_adapter: EpfoAdapter,
) -> Callable[[AssessmentState], dict]:
    def ingestion_node(state: AssessmentState) -> dict:
        log = log_status(state.agentLog, "Data Ingestion Agent", "running", "Reading public and consent data sources")

        master = store.master.get(state.msmeId)
        public = store.public.get(state.msmeId)
        errors = list(state.errors)
        if master is None or public is None:
            errors.append(f"MSME {state.msmeId} not found in data store")
            log = log_status(log, "Data Ingestion Agent", "error", f"MSME {state.msmeId} not found")
            return {"errors": errors, "agentLog": log}

        available_sources = ["public"]
        missing_sources: list[str] = []
        warnings: list[str] = []

        adapter_map = {
            ConsentSource.GST: gst_adapter,
            ConsentSource.UPI: upi_adapter,
            ConsentSource.AA_BANKING: aa_adapter,
            ConsentSource.EPFO: epfo_adapter,
        }

        for source in ConsentSource:
            label = SOURCE_LABELS[source]
            if source not in state.grantedSources:
                missing_sources.append(label)
                continue
            data = adapter_map[source].fetch(state.msmeId)
            if data is None:
                missing_sources.append(label)
                warnings.append(f"{label} consent was granted but no data could be retrieved")
            else:
                available_sources.append(source.value)

        if public.google_review_count < 10:
            warnings.append("Public review sample size is small — treat public signals with caution")
        if not warnings:
            warnings.append("No data quality issues detected")

        data_completeness = round(len(available_sources) / TOTAL_CATEGORIES, 2)

        log = log_status(
            log, "Data Ingestion Agent", "completed",
            f"{len(available_sources)}/{TOTAL_CATEGORIES} data categories available "
            f"({data_completeness * 100:.0f}% completeness)",
        )

        return {
            "availableSources": available_sources,
            "missingSources": missing_sources,
            "dataCompleteness": data_completeness,
            "ingestionWarnings": warnings,
            "agentLog": log,
            "errors": errors,
        }

    return ingestion_node
