"""EPFO (Employees' Provident Fund Organisation) data adapter.

Real-integration swap: replace MockEpfoAdapter with a client for the
EPFO employer establishment API (via DigiLocker/UMANG or a licensed data
aggregator), consumed only after the business consents to sharing its
establishment ID. This class is the only place that would need to change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from app.data_store import DataStore


class EpfoData(TypedDict):
    epfo_employee_count: int
    epfo_employee_growth_percentage: float
    epfo_contribution_timeliness_percentage: float


class EpfoAdapter(ABC):
    @abstractmethod
    def fetch(self, msme_id: str) -> EpfoData | None:
        """Return EPFO-derived signals for an MSME, or None if unavailable."""


class MockEpfoAdapter(EpfoAdapter):
    def __init__(self, store: DataStore) -> None:
        self._store = store

    def fetch(self, msme_id: str) -> EpfoData | None:
        record = self._store.consent.get(msme_id)
        if record is None:
            return None
        return EpfoData(
            epfo_employee_count=record.epfo_employee_count,
            epfo_employee_growth_percentage=record.epfo_employee_growth_percentage,
            epfo_contribution_timeliness_percentage=record.epfo_contribution_timeliness_percentage,
        )
