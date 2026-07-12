"""In-memory data store. Loads the committed synthetic JSON files once at
process startup via pandas/Pydantic. The app never writes files at runtime.
"""
from __future__ import annotations

import json
from functools import lru_cache

from app.config import DATA_DIR
from app.models.schemas import ConsentFinancialSignals, MsmeMaster, PublicSignals

DEMO_ARCHETYPES = {
    "credit_invisible",
    "cash_flow_volatile",
    "digitally_weak",
    "high_risk",
    "seasonal",
}


class DataStore:
    def __init__(self) -> None:
        self.master: dict[str, MsmeMaster] = {}
        self.public: dict[str, PublicSignals] = {}
        self.consent: dict[str, ConsentFinancialSignals] = {}
        self._load()

    def _load(self) -> None:
        master_raw = json.loads((DATA_DIR / "msme_master.json").read_text(encoding="utf-8"))
        public_raw = json.loads((DATA_DIR / "public_signals.json").read_text(encoding="utf-8"))
        consent_raw = json.loads(
            (DATA_DIR / "consent_financial_signals.json").read_text(encoding="utf-8")
        )

        for row in master_raw:
            m = MsmeMaster.model_validate(row)
            self.master[m.msme_id] = m
        for row in public_raw:
            p = PublicSignals.model_validate(row)
            self.public[p.msme_id] = p
        for row in consent_raw:
            c = ConsentFinancialSignals.model_validate(row)
            self.consent[c.msme_id] = c

    def is_demo_archetype(self, msme_id: str) -> bool:
        m = self.master.get(msme_id)
        return bool(m) and m.archetype.value in DEMO_ARCHETYPES

    def all_ids(self) -> list[str]:
        return list(self.master.keys())


@lru_cache
def get_data_store() -> DataStore:
    return DataStore()
