"""In-memory consent grant tracker for the POC consent-simulation flow.

Not persisted — a process restart resets all simulated consent, which is
expected behaviour for a demo (no database, per the build contract).
"""
from __future__ import annotations

from functools import lru_cache

from app.models.schemas import ConsentSource, ConsentStatus


class ConsentStore:
    def __init__(self) -> None:
        self._granted: dict[str, set[ConsentSource]] = {}
        self._grant_order: list[str] = []

    def grant(self, msme_id: str, sources: list[ConsentSource]) -> set[ConsentSource]:
        current = self._granted.setdefault(msme_id, set())
        current.update(sources)
        if msme_id in self._grant_order:
            self._grant_order.remove(msme_id)
        self._grant_order.append(msme_id)
        return current

    def granted_sources(self, msme_id: str) -> list[ConsentSource]:
        return sorted(self._granted.get(msme_id, set()), key=lambda s: s.value)

    def status(self, msme_id: str) -> ConsentStatus:
        granted = self._granted.get(msme_id, set())
        if not granted:
            return ConsentStatus.NOT_REQUESTED
        if len(granted) == len(ConsentSource):
            return ConsentStatus.GRANTED
        return ConsentStatus.PARTIAL

    def recently_granted_msme_ids(self, limit: int = 5) -> list[str]:
        return list(reversed(self._grant_order))[:limit]


@lru_cache
def get_consent_store() -> ConsentStore:
    return ConsentStore()
