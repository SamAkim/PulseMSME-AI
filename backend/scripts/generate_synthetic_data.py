"""Generate synthetic MSME data with a fixed random seed.

Run with:  python -m scripts.generate_synthetic_data   (from backend/)

Writes msme_master, public_signals, and consent_financial_signals as both
JSON and CSV into backend/data/. This is the ONLY place synthetic data is
produced — the API loads the committed JSON at startup and never writes
files at runtime.

All figures are entirely synthetic (fixed seed = 42) and are never to be
presented as real business data.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pandas as pd

SEED = 42
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SECTORS = [
    "Textile Retail", "Small Manufacturing", "Pharmacy", "Grocery", "Restaurant",
    "E-commerce Seller", "Logistics", "Repair Services", "Food Processing",
    "Local Professional Services",
]
LEGAL_STRUCTURES = ["Sole Proprietorship", "Partnership", "Private Limited", "LLP"]
SALES_CHANNELS = [
    "Offline Retail", "Online + In-store", "B2B Direct", "Marketplace + Retail", "Wholesale + Retail",
]
STATE_BY_CITY = {
    "Coimbatore": "Tamil Nadu", "Surat": "Gujarat", "Indore": "Madhya Pradesh",
    "Nagpur": "Maharashtra", "Madurai": "Tamil Nadu", "Rajkot": "Gujarat",
    "Vijayawada": "Andhra Pradesh", "Jaipur": "Rajasthan", "Lucknow": "Uttar Pradesh",
    "Bhopal": "Madhya Pradesh", "Nashik": "Maharashtra", "Kochi": "Kerala",
    "Guwahati": "Assam", "Patna": "Bihar", "Ludhiana": "Punjab",
    "Vadodara": "Gujarat", "Amritsar": "Punjab", "Mysore": "Karnataka",
    "Chandigarh": "Chandigarh", "Visakhapatnam": "Andhra Pradesh",
}
CITIES = list(STATE_BY_CITY.keys())

LAST_UPDATED = "2026-06-30"


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def jitter(rng: random.Random, value: float, pct: float = 0.05) -> float:
    return value * (1 + rng.uniform(-pct, pct))


# --------------------------------------------------------------------------
# Five mandatory demo archetypes — hand-tuned so the deterministic scoring
# engine (app/scoring) lands each one in its intended risk band. See the
# design notes in project memory / PR description for the worked arithmetic.
# --------------------------------------------------------------------------

ARCHETYPE_RECORDS = [
    {
        "msme_id": "MSME001",
        "business_name": "Sri Lakshmi Textiles",
        "sector": "Textile Retail",
        "city": "Coimbatore",
        "archetype": "credit_invisible",
        "master": dict(
            business_age_years=3.0, legal_structure="Sole Proprietorship", udyam_registered=True,
            employee_count=6, credit_history_available=False, primary_sales_channel="Online + In-store",
        ),
        "public": dict(
            google_rating=4.6, google_review_count=180, positive_review_percentage=91.0,
            review_sentiment_score=0.75, social_media_followers=8000, social_engagement_rate=4.2,
            website_present=True, website_quality_score=70.0, website_domain_age_years=2.5,
            business_listing_consistency=88.0, digital_activity_score=75.0,
        ),
        "consent": dict(
            average_monthly_gst_turnover=800000.0, annual_gst_turnover=9600000.0,
            gst_turnover_growth_percentage=18.0, gst_filing_timeliness_percentage=97.0,
            gst_sales_variance=15.0, average_monthly_upi_inflow=650000.0, upi_transaction_count=2200,
            upi_inflow_growth_percentage=22.0, upi_refund_percentage=1.5,
            average_monthly_bank_credit=900000.0, average_monthly_bank_debit=700000.0,
            average_monthly_balance=250000.0, monthly_cash_surplus=200000.0,
            existing_monthly_loan_obligation=0.0, cheque_bounce_count=0, payment_failure_percentage=1.0,
            epfo_employee_count=5, epfo_employee_growth_percentage=20.0,
            epfo_contribution_timeliness_percentage=95.0, cash_flow_volatility=14.0,
        ),
    },
    {
        "msme_id": "MSME002",
        "business_name": "Deccan Precision Engineering",
        "sector": "Small Manufacturing",
        "city": "Vijayawada",
        "archetype": "cash_flow_volatile",
        "master": dict(
            business_age_years=6.0, legal_structure="Private Limited", udyam_registered=True,
            employee_count=12, credit_history_available=True, primary_sales_channel="B2B Direct",
        ),
        "public": dict(
            google_rating=4.0, google_review_count=60, positive_review_percentage=75.0,
            review_sentiment_score=0.35, social_media_followers=1500, social_engagement_rate=2.0,
            website_present=True, website_quality_score=55.0, website_domain_age_years=4.0,
            business_listing_consistency=70.0, digital_activity_score=55.0,
        ),
        "consent": dict(
            average_monthly_gst_turnover=1200000.0, annual_gst_turnover=14400000.0,
            gst_turnover_growth_percentage=28.0, gst_filing_timeliness_percentage=82.0,
            gst_sales_variance=48.0, average_monthly_upi_inflow=300000.0, upi_transaction_count=900,
            upi_inflow_growth_percentage=25.0, upi_refund_percentage=3.0,
            average_monthly_bank_credit=1400000.0, average_monthly_bank_debit=1250000.0,
            average_monthly_balance=180000.0, monthly_cash_surplus=150000.0,
            existing_monthly_loan_obligation=180000.0, cheque_bounce_count=2, payment_failure_percentage=6.0,
            epfo_employee_count=11, epfo_employee_growth_percentage=15.0,
            epfo_contribution_timeliness_percentage=80.0, cash_flow_volatility=55.0,
        ),
    },
    {
        "msme_id": "MSME003",
        "business_name": "Nagpur Grain & Provisions",
        "sector": "Grocery",
        "city": "Nagpur",
        "archetype": "digitally_weak",
        "master": dict(
            business_age_years=7.0, legal_structure="Partnership", udyam_registered=True,
            employee_count=5, credit_history_available=True, primary_sales_channel="Offline Retail",
        ),
        "public": dict(
            google_rating=3.0, google_review_count=5, positive_review_percentage=50.0,
            review_sentiment_score=-0.1, social_media_followers=80, social_engagement_rate=0.3,
            website_present=False, website_quality_score=0.0, website_domain_age_years=0.0,
            business_listing_consistency=30.0, digital_activity_score=20.0,
        ),
        "consent": dict(
            average_monthly_gst_turnover=1100000.0, annual_gst_turnover=13200000.0,
            gst_turnover_growth_percentage=12.0, gst_filing_timeliness_percentage=96.0,
            gst_sales_variance=18.0, average_monthly_upi_inflow=200000.0, upi_transaction_count=700,
            upi_inflow_growth_percentage=10.0, upi_refund_percentage=1.0,
            average_monthly_bank_credit=1300000.0, average_monthly_bank_debit=1100000.0,
            average_monthly_balance=320000.0, monthly_cash_surplus=200000.0,
            existing_monthly_loan_obligation=50000.0, cheque_bounce_count=0, payment_failure_percentage=1.5,
            epfo_employee_count=5, epfo_employee_growth_percentage=8.0,
            epfo_contribution_timeliness_percentage=93.0, cash_flow_volatility=16.0,
        ),
    },
    {
        "msme_id": "MSME004",
        "business_name": "Rajkot Auto Spares & Repairs",
        "sector": "Repair Services",
        "city": "Rajkot",
        "archetype": "high_risk",
        "master": dict(
            business_age_years=4.0, legal_structure="Sole Proprietorship", udyam_registered=False,
            employee_count=3, credit_history_available=False, primary_sales_channel="Offline Retail",
        ),
        "public": dict(
            google_rating=2.8, google_review_count=20, positive_review_percentage=40.0,
            review_sentiment_score=-0.3, social_media_followers=300, social_engagement_rate=0.8,
            website_present=False, website_quality_score=0.0, website_domain_age_years=0.0,
            business_listing_consistency=35.0, digital_activity_score=25.0,
        ),
        "consent": dict(
            average_monthly_gst_turnover=250000.0, annual_gst_turnover=3000000.0,
            gst_turnover_growth_percentage=-18.0, gst_filing_timeliness_percentage=45.0,
            gst_sales_variance=35.0, average_monthly_upi_inflow=90000.0, upi_transaction_count=300,
            upi_inflow_growth_percentage=-12.0, upi_refund_percentage=8.0,
            average_monthly_bank_credit=280000.0, average_monthly_bank_debit=290000.0,
            average_monthly_balance=25000.0, monthly_cash_surplus=-10000.0,
            existing_monthly_loan_obligation=60000.0, cheque_bounce_count=6, payment_failure_percentage=18.0,
            epfo_employee_count=2, epfo_employee_growth_percentage=-10.0,
            epfo_contribution_timeliness_percentage=50.0, cash_flow_volatility=58.0,
        ),
    },
    {
        "msme_id": "MSME005",
        "business_name": "Madurai Silk & Sarees Emporium",
        "sector": "Textile Retail",
        "city": "Madurai",
        "archetype": "seasonal",
        "master": dict(
            business_age_years=8.0, legal_structure="Partnership", udyam_registered=True,
            employee_count=10, credit_history_available=True, primary_sales_channel="Online + In-store",
        ),
        "public": dict(
            google_rating=4.3, google_review_count=95, positive_review_percentage=85.0,
            review_sentiment_score=0.5, social_media_followers=3000, social_engagement_rate=2.8,
            website_present=True, website_quality_score=60.0, website_domain_age_years=5.0,
            business_listing_consistency=75.0, digital_activity_score=55.0,
        ),
        "consent": dict(
            average_monthly_gst_turnover=900000.0, annual_gst_turnover=10800000.0,
            gst_turnover_growth_percentage=14.0, gst_filing_timeliness_percentage=90.0,
            gst_sales_variance=65.0, average_monthly_upi_inflow=400000.0, upi_transaction_count=1400,
            upi_inflow_growth_percentage=16.0, upi_refund_percentage=2.0,
            average_monthly_bank_credit=950000.0, average_monthly_bank_debit=800000.0,
            average_monthly_balance=220000.0, monthly_cash_surplus=150000.0,
            existing_monthly_loan_obligation=70000.0, cheque_bounce_count=1, payment_failure_percentage=3.0,
            epfo_employee_count=9, epfo_employee_growth_percentage=10.0,
            epfo_contribution_timeliness_percentage=88.0, cash_flow_volatility=42.0,
        ),
    },
]

STANDARD_NAMES = [
    ("Surat Diamond Trading Co.", "E-commerce Seller", "Surat"),
    ("Indore Spice & Provisions", "Grocery", "Indore"),
    ("Bhopal City Pharmacy", "Pharmacy", "Bhopal"),
    ("Nashik Vineyard Foods Processing", "Food Processing", "Nashik"),
    ("Kochi Backwater Logistics", "Logistics", "Kochi"),
    ("Guwahati Tea Traders", "E-commerce Seller", "Guwahati"),
    ("Patna Sadar Electronics Repairs", "Repair Services", "Patna"),
    ("Ludhiana Hosiery Manufacturing", "Small Manufacturing", "Ludhiana"),
    ("Vadodara Green Grocers", "Grocery", "Vadodara"),
    ("Amritsar Dhaba & Catering", "Restaurant", "Amritsar"),
    ("Mysore Sandal Handicrafts", "Local Professional Services", "Mysore"),
    ("Chandigarh Legal & Tax Associates", "Local Professional Services", "Chandigarh"),
    ("Visakhapatnam Seafood Exports", "Food Processing", "Visakhapatnam"),
    ("Jaipur Blue Pottery Retail", "Textile Retail", "Jaipur"),
    ("Lucknow Chikankari Boutique", "Textile Retail", "Lucknow"),
]

# Quality dial spread from struggling to excellent, deterministic per MSME.
Q_VALUES = [0.08, 0.16, 0.24, 0.31, 0.38, 0.45, 0.52, 0.58, 0.64, 0.70, 0.76, 0.82, 0.87, 0.91, 0.96]


def build_standard_record(index: int, name: str, sector: str, city: str, q: float, rng: random.Random) -> dict:
    msme_id = f"MSME{index:03d}"

    business_age_years = round(clamp(jitter(rng, 2 + 10 * q), 0.5, 25), 1)
    employee_count = max(1, round(jitter(rng, 2 + 18 * q)))
    credit_history_available = q > 0.35
    udyam_registered = q > 0.30

    google_rating = round(clamp(jitter(rng, 3.0 + 1.8 * q), 1.0, 5.0), 1)
    google_review_count = max(1, round(jitter(rng, 10 + 300 * q)))
    positive_review_percentage = round(clamp(jitter(rng, 50 + 45 * q), 0, 100), 1)
    review_sentiment_score = round(clamp(jitter(rng, -0.2 + 1.0 * q, 0.1), -1.0, 1.0), 2)
    social_media_followers = max(0, round(jitter(rng, 200 + 9000 * q)))
    social_engagement_rate = round(clamp(jitter(rng, 0.5 + 4.0 * q), 0, 10), 2)
    website_present = q > 0.25
    website_quality_score = round(clamp(jitter(rng, 20 + 70 * q), 0, 100), 1) if website_present else 0.0
    website_domain_age_years = round(clamp(jitter(rng, 1 + 9 * q), 0, 20), 1) if website_present else 0.0
    business_listing_consistency = round(clamp(jitter(rng, 40 + 55 * q), 0, 100), 1)
    digital_activity_score = round(clamp(jitter(rng, 25 + 65 * q), 0, 100), 1)

    avg_monthly_gst_turnover = round(clamp(jitter(rng, 200000 + 1800000 * q), 50000, 5000000), -2)
    annual_gst_turnover = round(avg_monthly_gst_turnover * 12 * clamp(jitter(rng, 0.98, 0.02), 0.9, 1.1), -2)
    gst_turnover_growth_percentage = round(clamp(jitter(rng, -10 + 30 * q, 0.15), -30, 40), 1)
    gst_filing_timeliness_percentage = round(clamp(jitter(rng, 50 + 48 * q), 0, 100), 1)
    gst_sales_variance = round(clamp(jitter(rng, 50 - 35 * q), 5, 70), 1)

    avg_monthly_upi_inflow = round(clamp(jitter(rng, 100000 + 700000 * q), 20000, 2000000), -2)
    upi_transaction_count = max(10, round(jitter(rng, 200 + 1800 * q)))
    upi_inflow_growth_percentage = round(clamp(jitter(rng, -8 + 28 * q, 0.15), -25, 35), 1)
    upi_refund_percentage = round(clamp(jitter(rng, 6 - 5 * q), 0, 15), 1)

    avg_monthly_bank_credit = round(clamp(jitter(rng, avg_monthly_gst_turnover * 1.05), 50000, 6000000), -2)
    debit_ratio = clamp(jitter(rng, 0.95 - 0.20 * q), 0.55, 1.05)
    avg_monthly_bank_debit = round(avg_monthly_bank_credit * debit_ratio, -2)
    avg_monthly_balance = round(avg_monthly_bank_credit * clamp(jitter(rng, 0.1 + 0.35 * q), 0.03, 0.6), -2)
    monthly_cash_surplus = round(avg_monthly_bank_credit - avg_monthly_bank_debit, -2)
    existing_monthly_loan_obligation = round(
        max(0.0, avg_monthly_bank_credit * clamp(jitter(rng, 0.25 - 0.15 * q), 0, 0.4)), -2
    )
    cheque_bounce_count = max(0, round(jitter(rng, 6 - 6 * q)))
    payment_failure_percentage = round(clamp(jitter(rng, 15 - 13 * q), 0, 25), 1)

    epfo_employee_count = max(0, round(employee_count * 0.8))
    epfo_employee_growth_percentage = round(clamp(jitter(rng, -5 + 20 * q, 0.15), -20, 30), 1)
    epfo_contribution_timeliness_percentage = round(clamp(jitter(rng, 50 + 45 * q), 0, 100), 1)
    cash_flow_volatility = round(clamp(jitter(rng, 55 - 40 * q), 5, 65), 1)

    return {
        "msme_id": msme_id,
        "business_name": name,
        "sector": sector,
        "city": city,
        "archetype": "standard",
        "master": dict(
            business_age_years=business_age_years,
            legal_structure=LEGAL_STRUCTURES[index % len(LEGAL_STRUCTURES)],
            udyam_registered=udyam_registered,
            employee_count=employee_count,
            credit_history_available=credit_history_available,
            primary_sales_channel=SALES_CHANNELS[index % len(SALES_CHANNELS)],
        ),
        "public": dict(
            google_rating=google_rating, google_review_count=google_review_count,
            positive_review_percentage=positive_review_percentage,
            review_sentiment_score=review_sentiment_score, social_media_followers=social_media_followers,
            social_engagement_rate=social_engagement_rate, website_present=website_present,
            website_quality_score=website_quality_score, website_domain_age_years=website_domain_age_years,
            business_listing_consistency=business_listing_consistency,
            digital_activity_score=digital_activity_score,
        ),
        "consent": dict(
            average_monthly_gst_turnover=avg_monthly_gst_turnover, annual_gst_turnover=annual_gst_turnover,
            gst_turnover_growth_percentage=gst_turnover_growth_percentage,
            gst_filing_timeliness_percentage=gst_filing_timeliness_percentage,
            gst_sales_variance=gst_sales_variance, average_monthly_upi_inflow=avg_monthly_upi_inflow,
            upi_transaction_count=upi_transaction_count,
            upi_inflow_growth_percentage=upi_inflow_growth_percentage,
            upi_refund_percentage=upi_refund_percentage, average_monthly_bank_credit=avg_monthly_bank_credit,
            average_monthly_bank_debit=avg_monthly_bank_debit, average_monthly_balance=avg_monthly_balance,
            monthly_cash_surplus=monthly_cash_surplus,
            existing_monthly_loan_obligation=existing_monthly_loan_obligation,
            cheque_bounce_count=cheque_bounce_count, payment_failure_percentage=payment_failure_percentage,
            epfo_employee_count=epfo_employee_count,
            epfo_employee_growth_percentage=epfo_employee_growth_percentage,
            epfo_contribution_timeliness_percentage=epfo_contribution_timeliness_percentage,
            cash_flow_volatility=cash_flow_volatility,
        ),
    }


def build_all_records() -> list[dict]:
    records = list(ARCHETYPE_RECORDS)
    rng = random.Random(SEED)
    for i, (name, sector, city) in enumerate(STANDARD_NAMES):
        q = Q_VALUES[i]
        records.append(build_standard_record(6 + i, name, sector, city, q, rng))
    return records


def to_rows(records: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    master_rows, public_rows, consent_rows = [], [], []
    for r in records:
        msme_id = r["msme_id"]
        city = r["city"]
        master_rows.append({
            "msme_id": msme_id, "business_name": r["business_name"], "sector": r["sector"],
            "city": city, "state": STATE_BY_CITY[city], "archetype": r["archetype"],
            **r["master"],
        })
        public_rows.append({
            "msme_id": msme_id, **r["public"], "public_data_last_updated": LAST_UPDATED,
        })
        consent_rows.append({
            "msme_id": msme_id, **r["consent"], "consent_status": "granted",
            "financial_data_last_updated": LAST_UPDATED,
        })
    return master_rows, public_rows, consent_rows


def write_json_and_csv(rows: list[dict], stem: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DATA_DIR / f"{stem}.json"
    csv_path = DATA_DIR / f"{stem}.csv"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"wrote {json_path} and {csv_path} ({len(rows)} rows)")


def main() -> None:
    records = build_all_records()
    assert len(records) == 20, f"expected 20 MSMEs, got {len(records)}"
    master_rows, public_rows, consent_rows = to_rows(records)
    write_json_and_csv(master_rows, "msme_master")
    write_json_and_csv(public_rows, "public_signals")
    write_json_and_csv(consent_rows, "consent_financial_signals")


if __name__ == "__main__":
    main()
