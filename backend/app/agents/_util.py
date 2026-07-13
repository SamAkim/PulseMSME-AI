"""Shared helpers for agent node functions."""
from __future__ import annotations

import time

from app.models.schemas import AgentStatus


def now_ms() -> int:
    return int(time.time() * 1000)


def log_status(current_log: list[AgentStatus], agent: str, status: str, message: str) -> list[AgentStatus]:
    entry = AgentStatus(agent=agent, status=status, message=message, timestampMs=now_ms())
    return [*current_log, entry]
