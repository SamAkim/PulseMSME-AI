export type Archetype =
  | "credit_invisible"
  | "cash_flow_volatile"
  | "digitally_weak"
  | "high_risk"
  | "seasonal"
  | "standard";

export type RiskBand = "High Risk" | "Bad" | "Average" | "Good" | "Excellent";

export type ConsentSource = "gst" | "upi" | "aa_banking" | "epfo";

export type ConsentStatus = "not_requested" | "granted" | "partial";

export interface AppConfig {
  appName: string;
  appTagline: string;
}

export interface MsmeListItem {
  msmeId: string;
  businessName: string;
  sector: string;
  city: string;
  state: string;
  archetype: Archetype;
  isDemoArchetype: boolean;
  lastRiskBand: RiskBand | null;
  lastFinalScore: number | null;
}

export interface MsmeMaster {
  msme_id: string;
  business_name: string;
  sector: string;
  city: string;
  state: string;
  business_age_years: number;
  legal_structure: string;
  udyam_registered: boolean;
  employee_count: number;
  credit_history_available: boolean;
  primary_sales_channel: string;
  archetype: Archetype;
}

export interface MsmeProfile {
  master: MsmeMaster;
  isDemoArchetype: boolean;
  consentStatus: ConsentStatus;
  grantedSources: ConsentSource[];
}

export interface PublicSignals {
  msme_id: string;
  google_rating: number;
  google_review_count: number;
  positive_review_percentage: number;
  review_sentiment_score: number;
  social_media_followers: number;
  social_engagement_rate: number;
  website_present: boolean;
  website_quality_score: number;
  website_domain_age_years: number;
  business_listing_consistency: number;
  digital_activity_score: number;
  public_data_last_updated: string;
}

export interface ConsentFinancialSignals {
  msme_id: string;
  average_monthly_gst_turnover: number;
  annual_gst_turnover: number;
  gst_turnover_growth_percentage: number;
  gst_filing_timeliness_percentage: number;
  gst_sales_variance: number;
  average_monthly_upi_inflow: number;
  upi_transaction_count: number;
  upi_inflow_growth_percentage: number;
  upi_refund_percentage: number;
  average_monthly_bank_credit: number;
  average_monthly_bank_debit: number;
  average_monthly_balance: number;
  monthly_cash_surplus: number;
  existing_monthly_loan_obligation: number;
  cheque_bounce_count: number;
  payment_failure_percentage: number;
  epfo_employee_count: number;
  epfo_employee_growth_percentage: number;
  epfo_contribution_timeliness_percentage: number;
  cash_flow_volatility: number;
  consent_status: string;
  financial_data_last_updated: string;
}

export interface PublicScoreResult {
  preliminaryScore: number;
  confidenceLabel: "Limited data" | "Moderate footprint" | "Strong footprint";
  confidencePercentage: number;
  componentScores: Record<string, number>;
  positiveIndicators: string[];
  warningIndicators: string[];
  caution: string;
}

export interface EnhancedScoreDimensions {
  cashFlowStability: number;
  compliance: number;
  revenueAndGrowth: number;
  repaymentCapacity: number;
  operationalStability: number;
  digitalReputation: number;
}

export interface EnhancedScoreResult {
  finalScore: number;
  riskBand: RiskBand;
  confidenceScore: number;
  dimensions: EnhancedScoreDimensions;
  positiveFactors: string[];
  riskFactors: string[];
  missingData: string[];
}

export interface LoanEligibility {
  eligible: boolean;
  indicativeAmount: number;
  turnoverLimit: number;
  cashFlowLimit: number;
  baseAmount: number;
  bandMultiplier: number;
  tenureRangeMonths: [number, number];
  formulaExplanation: string;
  disclaimer: string;
}

export interface ProductRecommendation {
  product: string;
  justification: string;
  riskConditions: string[];
  requiredManualChecks: string[];
  nextBestAction: string;
  rationale: string;
  eligibility: LoanEligibility | null;
  missingDocuments: string[];
  disclaimer: string;
}

export interface AgentStatus {
  agent: string;
  status: "pending" | "running" | "completed" | "error";
  message: string;
  timestampMs: number;
}

export interface AssessmentResponse {
  msmeId: string;
  availableSources: string[];
  missingSources: string[];
  dataCompleteness: number;
  ingestionWarnings: string[];
  publicScore: PublicScoreResult | null;
  enhancedScore: EnhancedScoreResult | null;
  positiveIndicators: string[];
  riskIndicators: string[];
  anomalies: string[];
  healthSummary: string;
  recommendation: ProductRecommendation | null;
  agentLog: AgentStatus[];
  errors: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  reply: string;
  usedLlm: boolean;
}

export interface DashboardMetrics {
  totalMsmes: number;
  averageScore: number;
  excellentCount: number;
  goodCount: number;
  requiringReviewCount: number;
  publicOnlyCount: number;
  consentEnhancedCount: number;
  sectorDistribution: Record<string, number>;
  riskDistribution: Record<string, number>;
  recentAssessments: MsmeListItem[];
}

export interface ReportPayload {
  profile: MsmeProfile;
  publicSignals: PublicSignals;
  consentSignals: ConsentFinancialSignals | null;
  publicScore: PublicScoreResult | null;
  enhancedScore: EnhancedScoreResult | null;
  positiveIndicators: string[];
  riskIndicators: string[];
  healthSummary: string;
  recommendation: ProductRecommendation | null;
  generatedAt: string;
  disclaimer: string;
}

export const DEMO_ARCHETYPE_LABELS: Record<Archetype, string> = {
  credit_invisible: "Credit Invisible",
  cash_flow_volatile: "Cash-Flow Volatile",
  digitally_weak: "Digitally Weak",
  high_risk: "High Risk",
  seasonal: "Seasonal",
  standard: "Standard",
};

export const CONSENT_SOURCE_LABELS: Record<ConsentSource, string> = {
  gst: "GST",
  upi: "UPI",
  aa_banking: "Account Aggregator Banking",
  epfo: "EPFO",
};
