"""UPI (Unified Payments Interface) transaction data adapter.

Real-integration swap: replace MockUpiAdapter with a client for a UPI
switch / PSP settlement-data API (or an Account Aggregator "UPI history"
FI type), gated by explicit customer consent. Downstream code only depends
on the UpiAdapter ABC, so no other module needs to change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from app.data_store import DataStore


class UpiData(TypedDict):
    average_monthly_upi_inflow: float
    upi_transaction_count: int
    upi_inflow_growth_percentage: float
    upi_refund_percentage: float


class UpiAdapter(ABC):
    @abstractmethod
    def fetch(self, msme_id: str) -> UpiData | None:
        """Return UPI-derived signals for an MSME, or None if unavailable."""


class MockUpiAdapter(UpiAdapter):
    def __init__(self, store: DataStore) -> None:
        self._store = store

    def fetch(self, msme_id: str) -> UpiData | None:
        record = self._store.consent.get(msme_id)
        if record is None:
            return None
        return UpiData(
            average_monthly_upi_inflow=record.average_monthly_upi_inflow,
            upi_transaction_count=record.upi_transaction_count,
            upi_inflow_growth_percentage=record.upi_inflow_growth_percentage,
            upi_refund_percentage=record.upi_refund_percentage,
        )
