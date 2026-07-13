import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { CreateMsmeRequest, Archetype } from "../lib/types";

// ─── tiny helpers ────────────────────────────────────────────────────────────

function Label({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) {
  return (
    <label htmlFor={htmlFor} className="block text-xs font-semibold uppercase tracking-wide text-[var(--color-ink-500)] mb-1">
      {children}
    </label>
  );
}

function Input({
  id,
  type = "text",
  value,
  onChange,
  placeholder,
  min,
  max,
  step,
  required,
}: {
  id: string;
  type?: string;
  value: string | number;
  onChange: (v: string) => void;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  required?: boolean;
}) {
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      min={min}
      max={max}
      step={step}
      required={required}
      className="w-full rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-500)]"
    />
  );
}

function Select({
  id,
  value,
  onChange,
  options,
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <select
      id={id}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-500)]"
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

function CheckRow({
  id,
  label,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label htmlFor={id} className="flex items-center gap-2 cursor-pointer select-none text-sm text-[var(--color-ink-700)]">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-[var(--color-border)] accent-[var(--color-brand-500)]"
      />
      {label}
    </label>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="col-span-2 text-sm font-semibold text-[var(--color-brand-600)] border-b border-[var(--color-border)] pb-1 mt-4 mb-2">
      {children}
    </h3>
  );
}

function FieldGroup({ label, id, children }: { label: string; id: string; children: React.ReactNode }) {
  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      {children}
    </div>
  );
}

// ─── default form state ───────────────────────────────────────────────────────

const DEFAULT: CreateMsmeRequest = {
  // Step 1
  business_name: "",
  sector: "",
  city: "",
  state: "",
  business_age_years: 1,
  legal_structure: "Sole Proprietorship",
  udyam_registered: false,
  employee_count: 1,
  credit_history_available: false,
  primary_sales_channel: "In-store",
  archetype: "standard",
  // Step 2 — Public Signals
  google_rating: 3.5,
  google_review_count: 0,
  positive_review_percentage: 70,
  review_sentiment_score: 0,
  social_media_followers: 0,
  social_engagement_rate: 0,
  website_present: false,
  website_quality_score: 0,
  website_domain_age_years: 0,
  business_listing_consistency: 50,
  digital_activity_score: 30,
  // Step 2 — Financial Signals
  average_monthly_gst_turnover: 0,
  annual_gst_turnover: 0,
  gst_turnover_growth_percentage: 0,
  gst_filing_timeliness_percentage: 80,
  gst_sales_variance: 20,
  average_monthly_upi_inflow: 0,
  upi_transaction_count: 0,
  upi_inflow_growth_percentage: 0,
  upi_refund_percentage: 0,
  average_monthly_bank_credit: 0,
  average_monthly_bank_debit: 0,
  average_monthly_balance: 0,
  monthly_cash_surplus: 0,
  existing_monthly_loan_obligation: 0,
  cheque_bounce_count: 0,
  payment_failure_percentage: 0,
  epfo_employee_count: 0,
  epfo_employee_growth_percentage: 0,
  epfo_contribution_timeliness_percentage: 80,
  cash_flow_volatility: 20,
};

const SECTORS = [
  "Textile Retail", "Small Manufacturing", "Food & Beverage", "Agri-Processing",
  "Electronics Retail", "Grocery & Provisions", "Healthcare Services",
  "Auto Services", "Handicrafts", "Construction Materials", "Education Services",
  "IT Services", "Logistics & Transport", "Hospitality", "Other",
];

const LEGAL_STRUCTURES = [
  "Sole Proprietorship", "Partnership", "Private Limited", "LLP",
  "Public Limited", "Trust", "Society", "Other",
];

const SALES_CHANNELS = [
  "In-store", "Online + In-store", "B2B Direct", "Online Only",
  "Wholesale", "Marketplace", "Other",
];

const ARCHETYPES: { value: Archetype; label: string }[] = [
  { value: "standard", label: "Standard" },
  { value: "credit_invisible", label: "Credit Invisible" },
  { value: "cash_flow_volatile", label: "Cash-Flow Volatile" },
  { value: "digitally_weak", label: "Digitally Weak" },
  { value: "high_risk", label: "High Risk" },
  { value: "seasonal", label: "Seasonal" },
];

// ─── Step indicators ──────────────────────────────────────────────────────────

function StepIndicator({ current }: { current: 1 | 2 }) {
  const steps = [
    { n: 1, label: "Business Profile" },
    { n: 2, label: "Financial Signals" },
  ];
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((s, idx) => (
        <div key={s.n} className="flex items-center">
          <div className="flex flex-col items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                current === s.n
                  ? "bg-[var(--color-brand-500)] text-white"
                  : s.n < current
                  ? "bg-[var(--color-brand-200)] text-[var(--color-brand-700)]"
                  : "bg-[var(--color-ink-100)] text-[var(--color-ink-400)]"
              }`}
            >
              {s.n < current ? "✓" : s.n}
            </div>
            <span
              className={`mt-1 text-xs font-medium ${
                current === s.n ? "text-[var(--color-brand-600)]" : "text-[var(--color-ink-400)]"
              }`}
            >
              {s.label}
            </span>
          </div>
          {idx < steps.length - 1 && (
            <div
              className={`h-0.5 w-24 mx-2 mb-4 transition-colors ${
                s.n < current ? "bg-[var(--color-brand-400)]" : "bg-[var(--color-ink-200)]"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function AddMsmePage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2>(1);
  const [form, setForm] = useState<CreateMsmeRequest>(DEFAULT);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generic setters
  const setStr = (key: keyof CreateMsmeRequest) => (v: string) =>
    setForm((f) => ({ ...f, [key]: v }));
  const setNum = (key: keyof CreateMsmeRequest) => (v: string) =>
    setForm((f) => ({ ...f, [key]: v === "" ? 0 : parseFloat(v) }));
  const setInt = (key: keyof CreateMsmeRequest) => (v: string) =>
    setForm((f) => ({ ...f, [key]: v === "" ? 0 : parseInt(v, 10) }));
  const setBool = (key: keyof CreateMsmeRequest) => (v: boolean) =>
    setForm((f) => ({ ...f, [key]: v }));

  const handleStep1Next = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.business_name.trim() || !form.sector || !form.city.trim() || !form.state.trim()) {
      setError("Please fill in all required fields.");
      return;
    }
    setError(null);
    setStep(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const created = await api.createMsme(form);
      navigate(`/msme/${created.msmeId}/public`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create MSME. Please try again.");
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">
          Register New MSME
        </h1>
        <p className="mt-1 text-sm text-[var(--color-ink-500)]">
          Fill in the business profile and financial signals to add a new MSME for assessment.
        </p>
      </div>

      <StepIndicator current={step} />

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* ── STEP 1: Business Profile ── */}
      {step === 1 && (
        <form onSubmit={handleStep1Next}>
          <div className="rounded-xl border border-[var(--color-border)] bg-white p-6 shadow-sm">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <SectionHeading>Business Identity</SectionHeading>

              <FieldGroup label="Business Name *" id="business_name">
                <Input id="business_name" value={form.business_name} onChange={setStr("business_name")} placeholder="e.g. Krishna Hardware Store" required />
              </FieldGroup>

              <FieldGroup label="Sector *" id="sector">
                <Select id="sector" value={form.sector} onChange={setStr("sector")} options={[{ value: "", label: "Select sector…" }, ...SECTORS.map((s) => ({ value: s, label: s }))]} />
              </FieldGroup>

              <FieldGroup label="City *" id="city">
                <Input id="city" value={form.city} onChange={setStr("city")} placeholder="e.g. Nagpur" required />
              </FieldGroup>

              <FieldGroup label="State *" id="state">
                <Input id="state" value={form.state} onChange={setStr("state")} placeholder="e.g. Maharashtra" required />
              </FieldGroup>

              <SectionHeading>Business Details</SectionHeading>

              <FieldGroup label="Business Age (years)" id="business_age_years">
                <Input id="business_age_years" type="number" value={form.business_age_years} onChange={setNum("business_age_years")} min={0} step={0.5} />
              </FieldGroup>

              <FieldGroup label="Legal Structure" id="legal_structure">
                <Select id="legal_structure" value={form.legal_structure} onChange={setStr("legal_structure")} options={LEGAL_STRUCTURES.map((s) => ({ value: s, label: s }))} />
              </FieldGroup>

              <FieldGroup label="Employee Count" id="employee_count">
                <Input id="employee_count" type="number" value={form.employee_count} onChange={setInt("employee_count")} min={0} />
              </FieldGroup>

              <FieldGroup label="Primary Sales Channel" id="primary_sales_channel">
                <Select id="primary_sales_channel" value={form.primary_sales_channel} onChange={setStr("primary_sales_channel")} options={SALES_CHANNELS.map((s) => ({ value: s, label: s }))} />
              </FieldGroup>

              <FieldGroup label="Archetype" id="archetype">
                <Select id="archetype" value={form.archetype} onChange={(v) => setForm((f) => ({ ...f, archetype: v as Archetype }))} options={ARCHETYPES} />
              </FieldGroup>

              <div className="sm:col-span-2 flex flex-wrap gap-6 mt-2">
                <CheckRow id="udyam_registered" label="Udyam Registered" checked={form.udyam_registered} onChange={setBool("udyam_registered")} />
                <CheckRow id="credit_history_available" label="Credit History Available" checked={form.credit_history_available} onChange={setBool("credit_history_available")} />
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate("/msme")}
              className="rounded-lg border border-[var(--color-border)] px-5 py-2 text-sm font-medium text-[var(--color-ink-600)] hover:bg-[var(--color-ink-50)] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-[var(--color-brand-500)] px-6 py-2 text-sm font-semibold text-white hover:bg-[var(--color-brand-600)] transition-colors"
            >
              Next: Financial Signals →
            </button>
          </div>
        </form>
      )}

      {/* ── STEP 2: Financial Signals ── */}
      {step === 2 && (
        <form onSubmit={handleSubmit}>
          <div className="rounded-xl border border-[var(--color-border)] bg-white p-6 shadow-sm space-y-2">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

              {/* Public Signals */}
              <SectionHeading>🌐 Public Signals (Digital Presence)</SectionHeading>

              <FieldGroup label="Google Rating (0–5)" id="google_rating">
                <Input id="google_rating" type="number" value={form.google_rating} onChange={setNum("google_rating")} min={0} max={5} step={0.1} />
              </FieldGroup>

              <FieldGroup label="Google Review Count" id="google_review_count">
                <Input id="google_review_count" type="number" value={form.google_review_count} onChange={setInt("google_review_count")} min={0} />
              </FieldGroup>

              <FieldGroup label="Positive Review % (0–100)" id="positive_review_percentage">
                <Input id="positive_review_percentage" type="number" value={form.positive_review_percentage} onChange={setNum("positive_review_percentage")} min={0} max={100} />
              </FieldGroup>

              <FieldGroup label="Review Sentiment Score (-1 to 1)" id="review_sentiment_score">
                <Input id="review_sentiment_score" type="number" value={form.review_sentiment_score} onChange={setNum("review_sentiment_score")} min={-1} max={1} step={0.01} />
              </FieldGroup>

              <FieldGroup label="Social Media Followers" id="social_media_followers">
                <Input id="social_media_followers" type="number" value={form.social_media_followers} onChange={setInt("social_media_followers")} min={0} />
              </FieldGroup>

              <FieldGroup label="Social Engagement Rate (%)" id="social_engagement_rate">
                <Input id="social_engagement_rate" type="number" value={form.social_engagement_rate} onChange={setNum("social_engagement_rate")} min={0} step={0.1} />
              </FieldGroup>

              <FieldGroup label="Business Listing Consistency (%)" id="business_listing_consistency">
                <Input id="business_listing_consistency" type="number" value={form.business_listing_consistency} onChange={setNum("business_listing_consistency")} min={0} max={100} />
              </FieldGroup>

              <FieldGroup label="Digital Activity Score (0–100)" id="digital_activity_score">
                <Input id="digital_activity_score" type="number" value={form.digital_activity_score} onChange={setNum("digital_activity_score")} min={0} max={100} />
              </FieldGroup>

              <FieldGroup label="Website Quality Score (0–100)" id="website_quality_score">
                <Input id="website_quality_score" type="number" value={form.website_quality_score} onChange={setNum("website_quality_score")} min={0} max={100} />
              </FieldGroup>

              <FieldGroup label="Website Domain Age (years)" id="website_domain_age_years">
                <Input id="website_domain_age_years" type="number" value={form.website_domain_age_years} onChange={setNum("website_domain_age_years")} min={0} step={0.5} />
              </FieldGroup>

              <div className="sm:col-span-2 mt-1">
                <CheckRow id="website_present" label="Website Present" checked={form.website_present} onChange={setBool("website_present")} />
              </div>

              {/* GST Signals */}
              <SectionHeading>📋 GST Signals</SectionHeading>

              <FieldGroup label="Avg Monthly GST Turnover (₹)" id="average_monthly_gst_turnover">
                <Input id="average_monthly_gst_turnover" type="number" value={form.average_monthly_gst_turnover} onChange={setNum("average_monthly_gst_turnover")} min={0} />
              </FieldGroup>

              <FieldGroup label="Annual GST Turnover (₹)" id="annual_gst_turnover">
                <Input id="annual_gst_turnover" type="number" value={form.annual_gst_turnover} onChange={setNum("annual_gst_turnover")} min={0} />
              </FieldGroup>

              <FieldGroup label="GST Turnover Growth (%)" id="gst_turnover_growth_percentage">
                <Input id="gst_turnover_growth_percentage" type="number" value={form.gst_turnover_growth_percentage} onChange={setNum("gst_turnover_growth_percentage")} step={0.1} />
              </FieldGroup>

              <FieldGroup label="GST Filing Timeliness (%)" id="gst_filing_timeliness_percentage">
                <Input id="gst_filing_timeliness_percentage" type="number" value={form.gst_filing_timeliness_percentage} onChange={setNum("gst_filing_timeliness_percentage")} min={0} max={100} />
              </FieldGroup>

              <FieldGroup label="GST Sales Variance (%)" id="gst_sales_variance">
                <Input id="gst_sales_variance" type="number" value={form.gst_sales_variance} onChange={setNum("gst_sales_variance")} min={0} />
              </FieldGroup>

              {/* UPI Signals */}
              <SectionHeading>📱 UPI Signals</SectionHeading>

              <FieldGroup label="Avg Monthly UPI Inflow (₹)" id="average_monthly_upi_inflow">
                <Input id="average_monthly_upi_inflow" type="number" value={form.average_monthly_upi_inflow} onChange={setNum("average_monthly_upi_inflow")} min={0} />
              </FieldGroup>

              <FieldGroup label="UPI Transaction Count (monthly)" id="upi_transaction_count">
                <Input id="upi_transaction_count" type="number" value={form.upi_transaction_count} onChange={setInt("upi_transaction_count")} min={0} />
              </FieldGroup>

              <FieldGroup label="UPI Inflow Growth (%)" id="upi_inflow_growth_percentage">
                <Input id="upi_inflow_growth_percentage" type="number" value={form.upi_inflow_growth_percentage} onChange={setNum("upi_inflow_growth_percentage")} step={0.1} />
              </FieldGroup>

              <FieldGroup label="UPI Refund Rate (%)" id="upi_refund_percentage">
                <Input id="upi_refund_percentage" type="number" value={form.upi_refund_percentage} onChange={setNum("upi_refund_percentage")} min={0} max={100} />
              </FieldGroup>

              {/* Banking Signals */}
              <SectionHeading>🏦 Account Aggregator / Banking</SectionHeading>

              <FieldGroup label="Avg Monthly Bank Credit (₹)" id="average_monthly_bank_credit">
                <Input id="average_monthly_bank_credit" type="number" value={form.average_monthly_bank_credit} onChange={setNum("average_monthly_bank_credit")} min={0} />
              </FieldGroup>

              <FieldGroup label="Avg Monthly Bank Debit (₹)" id="average_monthly_bank_debit">
                <Input id="average_monthly_bank_debit" type="number" value={form.average_monthly_bank_debit} onChange={setNum("average_monthly_bank_debit")} min={0} />
              </FieldGroup>

              <FieldGroup label="Avg Monthly Balance (₹)" id="average_monthly_balance">
                <Input id="average_monthly_balance" type="number" value={form.average_monthly_balance} onChange={setNum("average_monthly_balance")} min={0} />
              </FieldGroup>

              <FieldGroup label="Monthly Cash Surplus (₹)" id="monthly_cash_surplus">
                <Input id="monthly_cash_surplus" type="number" value={form.monthly_cash_surplus} onChange={setNum("monthly_cash_surplus")} />
              </FieldGroup>

              <FieldGroup label="Existing Monthly Loan Obligation (₹)" id="existing_monthly_loan_obligation">
                <Input id="existing_monthly_loan_obligation" type="number" value={form.existing_monthly_loan_obligation} onChange={setNum("existing_monthly_loan_obligation")} min={0} />
              </FieldGroup>

              <FieldGroup label="Cheque Bounce Count (past 12 months)" id="cheque_bounce_count">
                <Input id="cheque_bounce_count" type="number" value={form.cheque_bounce_count} onChange={setInt("cheque_bounce_count")} min={0} />
              </FieldGroup>

              <FieldGroup label="Payment Failure Rate (%)" id="payment_failure_percentage">
                <Input id="payment_failure_percentage" type="number" value={form.payment_failure_percentage} onChange={setNum("payment_failure_percentage")} min={0} max={100} />
              </FieldGroup>

              <FieldGroup label="Cash Flow Volatility (%)" id="cash_flow_volatility">
                <Input id="cash_flow_volatility" type="number" value={form.cash_flow_volatility} onChange={setNum("cash_flow_volatility")} min={0} />
              </FieldGroup>

              {/* EPFO Signals */}
              <SectionHeading>👷 EPFO Signals</SectionHeading>

              <FieldGroup label="EPFO Employee Count" id="epfo_employee_count">
                <Input id="epfo_employee_count" type="number" value={form.epfo_employee_count} onChange={setInt("epfo_employee_count")} min={0} />
              </FieldGroup>

              <FieldGroup label="EPFO Employee Growth (%)" id="epfo_employee_growth_percentage">
                <Input id="epfo_employee_growth_percentage" type="number" value={form.epfo_employee_growth_percentage} onChange={setNum("epfo_employee_growth_percentage")} step={0.1} />
              </FieldGroup>

              <FieldGroup label="EPFO Contribution Timeliness (%)" id="epfo_contribution_timeliness_percentage">
                <Input id="epfo_contribution_timeliness_percentage" type="number" value={form.epfo_contribution_timeliness_percentage} onChange={setNum("epfo_contribution_timeliness_percentage")} min={0} max={100} />
              </FieldGroup>

            </div>
          </div>

          <div className="mt-6 flex justify-between gap-3">
            <button
              type="button"
              onClick={() => { setStep(1); setError(null); }}
              className="rounded-lg border border-[var(--color-border)] px-5 py-2 text-sm font-medium text-[var(--color-ink-600)] hover:bg-[var(--color-ink-50)] transition-colors"
            >
              ← Back
            </button>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => navigate("/msme")}
                className="rounded-lg border border-[var(--color-border)] px-5 py-2 text-sm font-medium text-[var(--color-ink-600)] hover:bg-[var(--color-ink-50)] transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="rounded-lg bg-[var(--color-brand-500)] px-6 py-2 text-sm font-semibold text-white hover:bg-[var(--color-brand-600)] disabled:opacity-60 transition-colors"
              >
                {submitting ? "Registering…" : "Register MSME ✓"}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
