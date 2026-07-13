import pytest

from app.models.schemas import (
    Archetype,
    ConsentFinancialSignals,
    ConsentStatus,
    MsmeMaster,
    PublicSignals,
)


@pytest.fixture
def base_master() -> MsmeMaster:
    return MsmeMaster(
        msme_id="TEST001",
        business_name="Test Traders",
        sector="Grocery",
        city="Pune",
        state="Maharashtra",
        business_age_years=5.0,
        legal_structure="Partnership",
        udyam_registered=True,
        employee_count=8,
        credit_history_available=True,
        primary_sales_channel="Offline Retail",
        archetype=Archetype.STANDARD,
    )


@pytest.fixture
def base_public() -> PublicSignals:
    return PublicSignals(
        msme_id="TEST001",
        google_rating=4.0,
        google_review_count=100,
        positive_review_percentage=80.0,
        review_sentiment_score=0.4,
        social_media_followers=2000,
        social_engagement_rate=2.5,
        website_present=True,
        website_quality_score=60.0,
        website_domain_age_years=3.0,
        business_listing_consistency=75.0,
        digital_activity_score=55.0,
        public_data_last_updated="2026-06-30",
    )


@pytest.fixture
def base_consent() -> ConsentFinancialSignals:
    return ConsentFinancialSignals(
        msme_id="TEST001",
        average_monthly_gst_turnover=500000.0,
        annual_gst_turnover=6000000.0,
        gst_turnover_growth_percentage=10.0,
        gst_filing_timeliness_percentage=85.0,
        gst_sales_variance=25.0,
        average_monthly_upi_inflow=250000.0,
        upi_transaction_count=800,
        upi_inflow_growth_percentage=8.0,
        upi_refund_percentage=2.0,
        average_monthly_bank_credit=550000.0,
        average_monthly_bank_debit=450000.0,
        average_monthly_balance=150000.0,
        monthly_cash_surplus=100000.0,
        existing_monthly_loan_obligation=40000.0,
        cheque_bounce_count=0,
        payment_failure_percentage=2.0,
        epfo_employee_count=7,
        epfo_employee_growth_percentage=5.0,
        epfo_contribution_timeliness_percentage=88.0,
        cash_flow_volatility=20.0,
        consent_status=ConsentStatus.GRANTED,
        financial_data_last_updated="2026-06-30",
    )
