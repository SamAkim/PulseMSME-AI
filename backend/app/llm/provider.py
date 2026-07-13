"""LLM provider chain: preferred provider -> the other configured provider ->
deterministic rule-based template. The app must work with zero API keys.

The LLM is used ONLY for natural-language phrasing (health summaries, risk
narratives, recommendation rationale, chat). It never computes scores,
eligibility, risk bands, or arithmetic — see app/scoring for that.
"""
from __future__ import annotations

import asyncio
import logging

from app.config import Settings, get_settings

logger = logging.getLogger("pulsemsme.llm")


class LlmUnavailable(Exception):
    """Raised internally when a provider can't be used; caller degrades to template."""


async def _call_gemini(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    if not settings.gemini_api_key:
        raise LlmUnavailable("no gemini key")
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise LlmUnavailable(str(exc)) from exc

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.2,
    )
    result = await llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    return str(result.content).strip()


async def _call_groq(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    if not settings.groq_api_key:
        raise LlmUnavailable("no groq key")
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_groq import ChatGroq
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise LlmUnavailable(str(exc)) from exc

    llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)
    result = await llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    return str(result.content).strip()


_PROVIDERS = {"gemini": _call_gemini, "groq": _call_groq}


async def generate_text(system_prompt: str, user_prompt: str) -> tuple[str | None, bool]:
    """Try the preferred provider, then the other, then give up.

    Returns (text, used_llm). When text is None the caller must apply its
    own deterministic template fallback.
    """
    settings = get_settings()
    order = [settings.preferred_llm_provider]
    order += [p for p in _PROVIDERS if p != settings.preferred_llm_provider]

    for provider_name in order:
        call = _PROVIDERS.get(provider_name)
        if call is None:
            continue
        try:
            text = await asyncio.wait_for(
                call(settings, system_prompt, user_prompt), timeout=settings.llm_timeout_seconds
            )
            if text:
                return text, True
        except LlmUnavailable:
            continue
        except (TimeoutError, asyncio.TimeoutError):
            logger.warning("LLM provider %s timed out", provider_name)
            continue
        except Exception as exc:  # noqa: BLE001 - any provider failure silently degrades
            logger.warning("LLM provider %s failed: %s", provider_name, exc)
            continue

    return None, False
