# PulseMSME AI

**A GenAI/Agentic-AI-driven MSME Financial Health Card for bank relationship managers and credit officers.**

> Indicative assessment for demonstration purposes. Final lending decisions require bank policy checks, bureau data, KYC, AML, and human credit review.

## The Problem

Banks evaluate MSME creditworthiness using traditional financial documents that New-to-Credit (NTC) and New-to-Bank (NTB) enterprises often lack. Alternate data exists — GST, UPI, Account Aggregator banking, EPFO, and public digital signals — but there is no unified assessment framework. This causes high rejection rates, missed viable borrowers, slow onboarding, and poor financial inclusion.

## The Solution

PulseMSME AI aggregates consent-based alternate data and public business signals, computes a multidimensional explainable health score in deterministic Python, and recommends a credit product. It integrates *conceptually* with ULI, OCEN, and Account Aggregator ecosystems via mock adapters behind production-ready interface boundaries (`backend/app/adapters/`).

## Key Features

- **Two-layer assessment** — a public, consent-free preliminary view, followed by a deeper consent-based enhanced assessment.
- **LangGraph agent pipeline** — four sequential agents (ingestion, scoring, risk & insight, recommendation) with live per-node status streamed over SSE.
- **Deterministic scoring engine** — all scores, risk bands, and eligibility figures are computed in pure Python. The LLM never touches arithmetic.
- **LLM explanation layer** — Gemini or Groq generate natural-language summaries and power a contextual chat assistant, with a fully deterministic rule-based fallback so the app works with zero API keys.
- **20 synthetic MSMEs**, including five hand-tuned demo archetypes, across 10 sectors and 20 Indian tier-2/tier-3 cities.
- **Indicative loan eligibility** — a transparent, explainable formula, always secondary to the product recommendation.
- **Printable report** for the credit file.

## The Two-Layer Journey

```
Select MSME → Analyse public signals → Preliminary assessment
→ Simulate MSME consent → Ingest consent-based data → Run LangGraph agent pipeline
→ Enhanced health card → Risks & strengths → Product recommendation
→ Credit officer chats with AI assistant → Printable report
```

**Layer 1 — Public Intelligence Assessment** (no consent): a preliminary score (0-100), risk classification, digital credibility summary, and a public-data confidence level capped at 70%. Always shown with: *"Public signals provide a preliminary view and should not be treated as direct evidence of repayment capacity."*

**Layer 2 — Consent-Based Financial Assessment** (after simulated consent): an enhanced score, a six-dimension health card, risk/strength analysis, a recommended credit product, and optional indicative loan eligibility.

## LangGraph Agent Workflow

Four nodes run sequentially as a `StateGraph` over a typed `AssessmentState` (see [`ARCHITECTURE.md`](ARCHITECTURE.md) for the diagram):

1. **Data Ingestion Agent** (`app/agents/ingestion.py`) — pulls public data and consent data for granted sources via the mock adapters, flags missing sources, computes data completeness.
2. **Financial Scoring Agent** (`app/agents/scoring_agent.py`) — calls the deterministic scoring engine. No LLM.
3. **Risk & Insight Agent** (`app/agents/risk_insight.py`) — derives strengths, risks, and anomalies via rules; asks the LLM only to phrase the natural-language health summary (with a deterministic template fallback).
4. **Credit Recommendation Agent** (`app/agents/recommendation.py`) — picks a product via rules, computes eligibility, and asks the LLM only to phrase the rationale narrative (with a fallback).

The pipeline is exposed both synchronously (`POST /api/msme/{id}/assess`) and as a live SSE stream (`GET /api/msme/{id}/assess/stream`) that the Agent Processing screen consumes to animate per-agent status in real time.

## Scoring Methodology

### Layer 1 — Public preliminary score (0-100)

Customer reputation 30% · Digital presence 25% · Business maturity 20% · Engagement & activity 15% · Listing consistency 10%. Confidence is capped at 70%: Limited data 25-40%, Moderate footprint 41-60%, Strong footprint 61-70%.

### Layer 2 — Enhanced score (0-100), six dimensions

| Dimension | Points | Key inputs |
|---|---|---|
| Cash-flow stability | 25 | Monthly surplus, inflow volatility, cheque bounces, payment failures |
| Compliance & discipline | 20 | GST/EPFO filing timeliness, Udyam registration, listing consistency |
| Revenue & growth | 20 | GST turnover level and growth, UPI growth, employee growth |
| Repayment capacity | 20 | Obligation-to-inflow ratio, surplus buffer, average balance |
| Operational stability | 10 | Business age, employee count, transaction volume, seasonal resilience |
| Digital reputation | 5 | Rating, sentiment, listing consistency, web/social presence |

**Risk bands:** 0-29 High Risk · 30-44 Bad · 45-59 Average · 60-79 Good · 80-100 Excellent.

### Loan eligibility (secondary figure)

```
turnover_limit  = annual_gst_turnover × 0.20
cash_flow_limit = monthly_cash_surplus × 12
base            = min(turnover_limit, cash_flow_limit)
final           = base × band_multiplier, clamped to [₹50,000, ₹50,00,000]
```

Band multipliers: High Risk 0 · Bad 0.25 · Average 0.50 · Good 0.80 · Excellent 1.00.

All scoring logic lives in `backend/app/scoring/` and is covered by `pytest` (dimension boundary tests, band boundaries, eligibility formula, and archetype-band expectations).

## Synthetic Data

`backend/scripts/generate_synthetic_data.py` generates 20 MSMEs with a **fixed random seed (42)** into `backend/data/*.json` (+ `.csv` copies for judges). The API loads only the committed JSON at startup and never writes files at runtime. All figures are entirely synthetic and are never to be presented as real business data.

Five archetypes are hand-tuned and clearly flagged in the UI:

1. **Credit Invisible** (Sri Lakshmi Textiles) — no traditional credit history, strong UPI/GST signals → Good/Excellent after consent.
2. **Cash-Flow Volatile** (Deccan Precision Engineering) — high growth, large variance → moderate (Average) risk.
3. **Digitally Weak** (Nagpur Grain & Provisions) — weak public footprint, strong GST/banking → low public score, good enhanced score. Proves the two-layer story.
4. **High Risk** (Rajkot Auto Spares & Repairs) — falling turnover, delayed GST, cheque bounces → High Risk band.
5. **Seasonal** (Madurai Silk & Sarees Emporium) — high seasonal variance, healthy annually → seasonal working capital recommendation.

## Architecture & Stack

- **Backend:** Python 3.11+, FastAPI, LangGraph + LangChain Core, pydantic-settings, pandas, sse-starlette, pytest, ruff.
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS v4, Recharts, React Router.
- **LLM:** `langchain-google-genai` (Gemini) and `langchain-groq` (Groq), with a deterministic rule-based fallback.
- **Deployment:** a single FastAPI process serves the built frontend as static files at `/`, with the API under `/api/*`.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full module map, state diagram, and mock adapter interfaces.

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m scripts.generate_synthetic_data            # regenerate data (already committed)
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the OpenAPI docs.

### Frontend

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173, proxies /api to localhost:8000
```

### Environment variables (`backend/.env`, copy from `.env.example`)

```env
GEMINI_API_KEY=
GROQ_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
GROQ_MODEL=llama-3.1-8b-instant
PREFERRED_LLM_PROVIDER=gemini
```

All blank by default — the app is fully functional with zero keys (health summaries, recommendation rationale, and chat all degrade to deterministic templates).

### Running tests

```bash
cd backend
pytest              # 50 tests: scoring, bands, eligibility, archetypes, API
ruff check app scripts tests
```

```bash
cd frontend
npm run build        # tsc -b && vite build
npm run lint          # oxlint
```

## Deployment

```bash
docker build -t pulsemsme-ai .
docker run -p 8000:8000 --env-file backend/.env pulsemsme-ai
```

The Dockerfile builds the frontend, then copies the static build into the backend image, which serves everything from one process. A `render.yaml` is included for one-click Render deployment.

## Demo Walkthrough

See [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) for a timed 3-minute walkthrough using the Credit-Invisible and Digitally-Weak archetypes.

## Limitations

- All data is synthetic and generated with a fixed seed — it is not real MSME data.
- GST/UPI/AA/EPFO/ULI/OCEN integrations are mocked behind production-ready interfaces; no real data provider is called.
- There is no database — synthetic data is loaded from committed JSON, and simulated consent is held in memory only (resets on restart).
- No authentication, real money movement, or real credit decisions are implemented.

## Production Roadmap

- Swap each mock adapter for a real GSTN/UPI-switch/Account-Aggregator/EPFO integration behind the same `Adapter` ABC.
- Add a persistence layer (assessment history, audit trail, consent ledger).
- Add bureau data and KYC/AML integration ahead of the recommendation step.
- Add authentication and role-based access for credit officers vs. relationship managers.
- Expand the scoring engine with sector-specific benchmarks and a model governance/monitoring layer.

## Responsible AI & Lending Disclaimer

The LLM is used exclusively for natural-language explanation — health summaries, risk narratives, recommendation rationale, and chat. It never computes scores, arithmetic, eligibility, or risk bands, and it never issues a final credit decision. Every indicative amount and recommendation carries this disclaimer:

> Indicative assessment for demonstration purposes. Final lending decisions require bank policy checks, bureau data, KYC, AML, and human credit review.

PulseMSME AI does not replace human credit officers — it is a decision-support tool for them.
