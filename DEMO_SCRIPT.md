# Demo Script (3 minutes)

Uses the **Credit Invisible** and **Digitally Weak** archetypes — together they best prove the two-layer story: alternate data can both *reveal* hidden creditworthiness and *correct for* an unrepresentative digital footprint.

## 0:00 – 0:20 — The Problem (Dashboard)

Open on the **Portfolio Dashboard**.

> "Banks have 20 MSMEs here, spanning textile retail to logistics, across tier-2 and tier-3 cities. Traditional credit history alone would reject or misjudge several of them. PulseMSME AI aggregates GST, UPI, banking, and EPFO data — with public signals as a fast first pass — into one explainable health card."

Point at the risk-band and sector distribution charts.

## 0:20 – 1:00 — Layer 1: Public Intelligence (Credit Invisible)

Navigate to **MSMEs → Sri Lakshmi Textiles** (badged "Credit Invisible").

> "Sri Lakshmi Textiles has no traditional credit history — a classic New-to-Credit business. But look at its public score: 75, driven by a 4.6 Google rating, consistent listings, and an active social presence."

Point out the confidence cap (≤70%) and the caution banner.

> "This is deliberately capped — public signals alone are never sufficient for a lending decision."

## 1:00 – 1:40 — Consent + Live Agent Pipeline

Click **Request Consent-Based Assessment → Simulate MSME Consent**. Check all four sources, click **Grant Consent and Continue**.

> "In production this consent flow routes through an Account Aggregator or ULI consent artefact. Here it's simulated for the demo — no real data leaves the bank's boundary."

Watch the **Agent Processing** screen live-update via Server-Sent Events as the four LangGraph agents run.

> "Four agents run in sequence: ingest the consent data, score it deterministically, derive risk/strength insights, and recommend a product — all streamed live, all under five seconds without an LLM call."

## 1:40 – 2:15 — Layer 2: Enhanced Health Card

Land on the **Enhanced Financial Health Card**.

> "The enhanced score jumps to 77 — Good band, 100% confidence. Strong UPI inflows, 97% GST filing timeliness, and low cash-flow volatility. This business was invisible to a bureau, but not to its own transaction data."

Point at the public-vs-enhanced comparison and the six-dimension radar chart.

## 2:15 – 2:40 — The Flip Side: Digitally Weak

Switch to **MSMEs → Nagpur Grain & Provisions** (badged "Digitally Weak"). Show its **Public Assessment**: score ~35, no website, sparse reviews.

> "This business would look weak on any public-signal-only model. But it has no website by choice, not by distress."

Jump straight to its (pre-computed) **Enhanced Health Card**: score 70, Good band.

> "Strong GST turnover, timely filings, healthy banking relationship. The two-layer model corrects for a misleading digital footprint — exactly the inclusion gap this product is built to close."

## 2:40 – 3:00 — Recommendation + Close

Navigate to **Recommendation**: show the product, the indicative eligibility amount with its expandable formula, and the disclaimer.

> "Every number here is deterministic and explainable — the LLM only writes the narrative around it, never the arithmetic. And it stays fully functional with zero API keys, falling back to rule-based templates. This is PulseMSME AI — indicative, explainable, and always a decision-support tool, never a replacement for the credit officer."

---

## Pitch-Deck Bullets

- **Problem:** MSMEs without traditional credit history are under-served; alternate data exists but isn't unified.
- **Solution:** A two-layer, explainable financial health card — public signals first, consent-based data second.
- **Differentiator:** Deterministic, auditable scoring; the LLM explains, it never decides.
- **Agentic architecture:** LangGraph pipeline with four sequential agents and live progress streaming.
- **Inclusion story:** Corrects for both credit invisibility and unrepresentative digital footprints.
- **Production-ready seams:** Mock adapters behind ABCs, ready to swap for real GST/UPI/AA/EPFO/ULI/OCEN integrations.
- **Responsible AI:** Every recommendation carries the same disclaimer — indicative only, human review required.
