"""Pydantic v2 models — the single source of truth for API contracts and
the LangGraph pipeline state. Every request/response body in the app is
one of these models.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DISCLAIMER = (
    "Indicative assessment for demonstration purposes. Final lending decisions "
    "require bank policy checks, bureau data, KYC, AML, and human credit review."
)


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------

class Archetype(str, Enum):
    CREDIT_INVISIBLE = "credit_invisible"
    CASH_FLOW_VOLATILE = "cash_flow_volatile"
    DIGITALLY_WEAK = "digitally_weak"
    HIGH_RISK = "high_risk"
    SEASONAL = "seasonal"
    STANDARD = "standard"


class RiskBand(str, Enum):
    HIGH_RISK = "High Risk"
    BAD = "Bad"
    AVERAGE = "Average"
    GOOD = "Good"
    EXCELLENT = "Excellent"


class ConsentSource(str, Enum):
    GST = "gst"
    UPI = "upi"
    AA_BANKING = "aa_banking"
    EPFO = "epfo"


class ConsentStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    GRANTED = "granted"
    PARTIAL = "partial"


# --------------------------------------------------------------------------
# Master / raw data models (mirror synthetic data columns)
# --------------------------------------------------------------------------

class MsmeMaster(BaseModel):
    msme_id: str
    business_name: str
    sector: str
    city: str
    state: str
    business_age_years: float
    legal_structure: str
    udyam_registered: bool
    employee_count: int
    credit_history_available: bool
    primary_sales_channel: str
    archetype: Archetype


class PublicSignals(BaseModel):
    msme_id: str
    google_rating: float
    google_review_count: int
    positive_review_percentage: float
    review_sentiment_score: float
    social_media_followers: int
    social_engagement_rate: float
    website_present: bool
    website_quality_score: float
    website_domain_age_years: float
    business_listing_consistency: float
    digital_activity_score: float
    public_data_last_updated: date


class ConsentFinancialSignals(BaseModel):
    msme_id: str
    average_monthly_gst_turnover: float
    annual_gst_turnover: float
    gst_turnover_growth_percentage: float
    gst_filing_timeliness_percentage: float
    gst_sales_variance: float
    average_monthly_upi_inflow: float
    upi_transaction_count: int
    upi_inflow_growth_percentage: float
    upi_refund_percentage: float
    average_monthly_bank_credit: float
    average_monthly_bank_debit: float
    average_monthly_balance: float
    monthly_cash_surplus: float
    existing_monthly_loan_obligation: float
    cheque_bounce_count: int
    payment_failure_percentage: float
    epfo_employee_count: int
    epfo_employee_growth_percentage: float
    epfo_contribution_timeliness_percentage: float
    cash_flow_volatility: float
    consent_status: ConsentStatus
    financial_data_last_updated: date


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

class AppConfig(BaseModel):
    appName: str
    appTagline: str


# --------------------------------------------------------------------------
# Scoring models
# --------------------------------------------------------------------------

class PublicScoreResult(BaseModel):
    preliminaryScore: int
    confidenceLabel: Literal["Limited data", "Moderate footprint", "Strong footprint"]
    confidencePercentage: int
    componentScores: dict[str, float]
    positiveIndicators: list[str]
    warningIndicators: list[str]
    caution: str = (
        "Public signals provide a preliminary view and should not be treated as "
        "direct evidence of repayment capacity."
    )


class EnhancedScoreDimensions(BaseModel):
    cashFlowStability: float
    compliance: float
    revenueAndGrowth: float
    repaymentCapacity: float
    operationalStability: float
    digitalReputation: float


class EnhancedScoreResult(BaseModel):
    finalScore: int
    riskBand: RiskBand
    confidenceScore: int
    dimensions: EnhancedScoreDimensions
    positiveFactors: list[str]
    riskFactors: list[str]
    missingData: list[str]


class LoanEligibility(BaseModel):
    eligible: bool
    indicativeAmount: float
    turnoverLimit: float
    cashFlowLimit: float
    baseAmount: float
    bandMultiplier: float
    tenureRangeMonths: tuple[int, int]
    formulaExplanation: str
    disclaimer: str = DISCLAIMER


class ProductRecommendation(BaseModel):
    product: str
    justification: str
    riskConditions: list[str]
    requiredManualChecks: list[str]
    nextBestAction: str
    rationale: str
    eligibility: LoanEligibility | None
    missingDocuments: list[str]
    disclaimer: str = DISCLAIMER


# --------------------------------------------------------------------------
# Agent pipeline state / status
# --------------------------------------------------------------------------

class AgentStatus(BaseModel):
    agent: str
    status: Literal["pending", "running", "completed", "error"]
    message: str
    timestampMs: int


class AssessmentState(BaseModel):
    """Typed state object threaded through the LangGraph pipeline."""

    msmeId: str
    grantedSources: list[ConsentSource] = Field(default_factory=list)

    availableSources: list[str] = Field(default_factory=list)
    missingSources: list[str] = Field(default_factory=list)
    dataCompleteness: float = 0.0
    ingestionWarnings: list[str] = Field(default_factory=list)

    publicScore: PublicScoreResult | None = None
    enhancedScore: EnhancedScoreResult | None = None

    positiveIndicators: list[str] = Field(default_factory=list)
    riskIndicators: list[str] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)
    healthSummary: str = ""

    recommendation: ProductRecommendation | None = None

    agentLog: list[AgentStatus] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)


# --------------------------------------------------------------------------
# API request/response models
# --------------------------------------------------------------------------

class MsmeListItem(BaseModel):
    msmeId: str
    businessName: str
    sector: str
    city: str
    state: str
    archetype: Archetype
    isDemoArchetype: bool
    lastRiskBand: RiskBand | None = None
    lastFinalScore: int | None = None


class MsmeProfile(BaseModel):
    master: MsmeMaster
    isDemoArchetype: bool
    consentStatus: ConsentStatus
    grantedSources: list[ConsentSource]


class ConsentRequest(BaseModel):
    sources: list[ConsentSource]


class ConsentResponse(BaseModel):
    msmeId: str
    consentStatus: ConsentStatus
    grantedSources: list[ConsentSource]


class AssessmentResponse(BaseModel):
    msmeId: str
    availableSources: list[str]
    missingSources: list[str]
    dataCompleteness: float
    ingestionWarnings: list[str]
    publicScore: PublicScoreResult | None
    enhancedScore: EnhancedScoreResult | None
    positiveIndicators: list[str]
    riskIndicators: list[str]
    anomalies: list[str]
    healthSummary: str
    recommendation: ProductRecommendation | None
    agentLog: list[AgentStatus]
    errors: list[str]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    usedLlm: bool


class DashboardMetrics(BaseModel):
    totalMsmes: int
    averageScore: float
    excellentCount: int
    goodCount: int
    requiringReviewCount: int
    publicOnlyCount: int
    consentEnhancedCount: int
    sectorDistribution: dict[str, int]
    riskDistribution: dict[str, int]
    recentAssessments: list[MsmeListItem]


class ReportPayload(BaseModel):
    profile: MsmeProfile
    publicSignals: PublicSignals
    consentSignals: ConsentFinancialSignals | None
    publicScore: PublicScoreResult | None
    enhancedScore: EnhancedScoreResult | None
    positiveIndicators: list[str]
    riskIndicators: list[str]
    healthSummary: str
    recommendation: ProductRecommendation | None
    generatedAt: str
    disclaimer: str = DISCLAIMER
