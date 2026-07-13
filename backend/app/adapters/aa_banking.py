"""Account Aggregator (AA) banking data adapter.

Real-integration swap: replace MockAaBankingAdapter with a client that
consumes the Sahamati/RBI Account Aggregator "FIP" data flow — bank
statements delivered as signed, encrypted FI Data Ranges after the
customer approves a consent artefact via an AA app. This class is the
only place that would need to change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from app.data_store import DataStore


class AaBankingData(TypedDict):
    average_monthly_bank_credit: float
    average_monthly_bank_debit: float
    average_monthly_balance: float
    monthly_cash_surplus: float
    existing_monthly_loan_obligation: float
    cheque_bounce_count: int
    payment_failure_percentage: float
    cash_flow_volatility: float


class AaBankingAdapter(ABC):
    @abstractmethod
    def fetch(self, msme_id: str) -> AaBankingData | None:
        """Return AA banking signals for an MSME, or None if unavailable."""


class MockAaBankingAdapter(AaBankingAdapter):
    def __init__(self, store: DataStore) -> None:
        self._store = store

    def fetch(self, msme_id: str) -> AaBankingData | None:
        record = self._store.consent.get(msme_id)
        if record is None:
            return None
        return AaBankingData(
            average_monthly_bank_credit=record.average_monthly_bank_credit,
            average_monthly_bank_debit=record.average_monthly_bank_debit,
            average_monthly_balance=record.average_monthly_balance,
            monthly_cash_surplus=record.monthly_cash_surplus,
            existing_monthly_loan_obligation=record.existing_monthly_loan_obligation,
            cheque_bounce_count=record.cheque_bounce_count,
            payment_failure_percentage=record.payment_failure_percentage,
            cash_flow_volatility=record.cash_flow_volatility,
        )
