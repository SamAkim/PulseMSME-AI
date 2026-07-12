# Team Plan

Four-member allocation for the hackathon build.

## Roles

**M1 — Lead / Integration / LangGraph / LLM / Deploy**
Owns the LangGraph pipeline (`backend/app/agents/`), the LLM provider chain and prompts (`backend/app/llm/`), the FastAPI app wiring (`backend/app/main.py`, `backend/app/routers/`), the Dockerfile, and `render.yaml`. Owns final merges to `main` and the deploy checklist.

**M2 — React Frontend / Charts / Consent Flow / SSE Panel**
Owns `frontend/src/pages/` and `frontend/src/components/`, the Recharts visualizations (dashboard bar/pie, health card radar), the Consent Simulation screen, and the Agent Processing screen's SSE-driven live activity panel.

**M3 — Data / Scoring / Eligibility / pytest**
Owns `backend/scripts/generate_synthetic_data.py`, `backend/app/scoring/`, and `backend/tests/`. Responsible for the five demo archetypes landing in their expected risk bands, and for all pytest coverage (dimension scorers, band boundaries, eligibility formula, archetype expectations).

**M4 — Assistant Prompts / Report / Docs / Pitch / Demo Script**
Owns the AI Credit Assistant prompt design (`backend/app/llm/prompts.py`), the Printable Report screen, `README.md`, `ARCHITECTURE.md`, and `DEMO_SCRIPT.md`, plus the pitch-deck bullet content.

## Git Workflow

- `main` — always deployable. No unfinished work pushed directly.
- `feature/ui-dashboard` — M2's frontend work.
- `feature/data-scoring` — M3's data generator and scoring engine.
- `feature/ai-assistant` — M1/M4's LLM provider, prompts, and chat.
- `feature/docs-demo` — M4's documentation and demo script.

**Contract discipline:** the Pydantic models in `backend/app/models/schemas.py` are the single source of truth for every API request/response and the LangGraph state. Any contract change is proposed as a PR comment before implementation, since both frontend and backend depend on it directly.

**Checkpoints:** integrate against `main` at the end of each phase in §12 of the build spec (skeleton → data+scoring → smallest e2e slice → full journey → LLM layer → ship), not just at the end. Small, frequent commits over large batched ones.

**Before merging to `main`:** `ruff check` and `pytest` must pass on the backend; `npm run build` and `npm run lint` must pass on the frontend. M1 owns the final merge and pre-deploy checklist.

## Phase Checkpoints (mirrors §12 of the build spec)

| Phase | Gate | Primary owner |
|---|---|---|
| 1. Skeleton | Backend starts, frontend builds | M1 |
| 2. Data + Scoring | `pytest` passes, archetypes land in expected bands | M3 |
| 3. Smallest e2e slice | Manual click-through: list → public → consent → enhanced card | M1 + M2 |
| 4. Full journey | Dashboard, SSE panel, recommendation, report, all polish states | M2 |
| 5. LLM layer | Chat + summaries work with keys, app fully functional with zero keys | M1 + M4 |
| 6. Ship | README/ARCHITECTURE/TEAM_PLAN/DEMO_SCRIPT, lint+tests+build, Docker | M4 + M1 |
