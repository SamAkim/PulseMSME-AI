"""GST (Goods and Services Tax) data adapter.

Real-integration swap: replace MockGstAdapter with an implementation that
calls the GSTN / GSP (GST Suvidha Provider) API using the MSME's GSTIN and
a consent artefact obtained via the Account Aggregator or ULI/OCEN consent
flow. The ABC boundary means the rest of the pipeline (ingestion agent,
scoring engine) never changes — only this class's internals do.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from app.data_store import DataStore


class GstData(TypedDict):
    average_monthly_gst_turnover: float
    annual_gst_turnover: float
    gst_turnover_growth_percentage: float
    gst_filing_timeliness_percentage: float
    gst_sales_variance: float


class GstAdapter(ABC):
    @abstractmethod
    def fetch(self, msme_id: str) -> GstData | None:
        """Return GST-derived signals for an MSME, or None if unavailable."""


class MockGstAdapter(GstAdapter):
    def __init__(self, store: DataStore) -> None:
        self._store = store

    def fetch(self, msme_id: str) -> GstData | None:
        record = self._store.consent.get(msme_id)
        if record is None:
            return None
        return GstData(
            average_monthly_gst_turnover=record.average_monthly_gst_turnover,
            annual_gst_turnover=record.annual_gst_turnover,
            gst_turnover_growth_percentage=record.gst_turnover_growth_percentage,
            gst_filing_timeliness_percentage=record.gst_filing_timeliness_percentage,
            gst_sales_variance=record.gst_sales_variance,
        )
