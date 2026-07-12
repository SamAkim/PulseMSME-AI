import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { api, ApiError } from "../lib/api";
import type { AssessmentResponse, EnhancedScoreDimensions } from "../lib/types";
import { Card, CardHeader } from "../components/Card";
import { Button } from "../components/Button";
import { RiskBandBadge } from "../components/Badge";
import { ScoreRing } from "../components/ScoreRing";
import { ProgressBar } from "../components/ProgressBar";
import { SkeletonCard } from "../components/Skeleton";
import { ErrorState } from "../components/States";
import { JourneySteps } from "../components/JourneySteps";
import { InfoDot } from "../components/Tooltip";
import { useAssessmentStore } from "../lib/AssessmentContext";
import { bandColorHex } from "../lib/riskBand";

const DIMENSION_META: { key: keyof EnhancedScoreDimensions; label: string; max: number; tooltip: string }[] = [
  { key: "cashFlowStability", label: "Cash-Flow Stability", max: 25, tooltip: "Monthly surplus, inflow stability, volatility, bounces, and payment failures." },
  { key: "compliance", label: "Compliance & Discipline", max: 20, tooltip: "GST filing timeliness, EPFO contribution timeliness, Udyam registration, listing consistency." },
  { key: "revenueAndGrowth", label: "Revenue & Growth", max: 20, tooltip: "GST turnover, revenue growth, UPI growth, employee growth, trend direction." },
  { key: "repaymentCapacity", label: "Repayment Capacity", max: 20, tooltip: "Monthly surplus, existing obligations, obligation-to-inflow ratio, average balance." },
  { key: "operationalStability", label: "Operational Stability", max: 10, tooltip: "Business age, employee stability, transaction volume, seasonal resilience." },
  { key: "digitalReputation", label: "Digital Reputation", max: 5, tooltip: "Rating, sentiment, listing consistency, web/social presence." },
];

export default function HealthCardPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const { get, set } = useAssessmentStore();
  const [data, setData] = useState<AssessmentResponse | null>(get(id) ?? null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(!data);

  useEffect(() => {
    const cached = get(id);
    if (cached) {
      setData(cached);
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .assess(id)
      .then((r) => {
        set(id, r);
        setData(r);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not run the assessment"))
      .finally(() => setLoading(false));
  }, [id, get, set]);

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
        <ErrorState message={error} />
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8 sm:px-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (!data.enhancedScore) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <ErrorState
          message="No consent-based data is available yet for this MSME. Grant consent first to see the enhanced health card."
        />
        <div className="mt-4 text-center">
          <Link to={`/msme/${id}/consent`} className="text-sm font-medium text-[var(--color-brand-700)] hover:underline">
            Go to Consent Simulation
          </Link>
        </div>
      </div>
    );
  }

  const es = data.enhancedScore;
  const radarData = DIMENSION_META.map((d) => ({
    dimension: d.label.split(" ")[0],
    value: es.dimensions[d.key],
    fullMark: d.max,
  }));

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
      <JourneySteps current="health-card" />

      <div>
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">Enhanced Financial Health Card</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-500)]">
          Consent-based assessment combining public signals with GST, UPI, banking, and EPFO data.
        </p>
      </div>

      <Card>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          <ScoreRing score={es.finalScore} band={es.riskBand} label="Enhanced" />
          <div className="flex-1 space-y-3 text-center sm:text-left">
            <div className="flex flex-wrap items-center justify-center gap-2 sm:justify-start">
              <RiskBandBadge band={es.riskBand} />
              <span className="text-sm text-[var(--color-ink-500)]">Confidence {es.confidenceScore}%</span>
            </div>
            <p className="text-sm leading-relaxed text-[var(--color-ink-700)]">{data.healthSummary}</p>
            <div className="flex flex-wrap justify-center gap-4 text-xs text-[var(--color-ink-500)] sm:justify-start">
              <span>Data completeness: {(data.dataCompleteness * 100).toFixed(0)}%</span>
              <span>Sources: {data.availableSources.join(", ")}</span>
            </div>
          </div>
        </div>
      </Card>

      {data.publicScore && (
        <Card>
          <CardHeader title="Public vs. Enhanced Assessment" subtitle="Why consent-based data matters" />
          <div className="flex items-center gap-6">
            <div className="flex-1">
              <p className="text-xs text-[var(--color-ink-500)]">Public (Layer 1)</p>
              <p className="font-mono-data text-2xl font-semibold text-[var(--color-ink-700)]">
                {data.publicScore.preliminaryScore}
              </p>
              <ProgressBar value={data.publicScore.preliminaryScore} max={100} color="var(--color-ink-300)" showValue={false} />
            </div>
            <div className="flex-1">
              <p className="text-xs text-[var(--color-ink-500)]">Enhanced (Layer 2)</p>
              <p className="font-mono-data text-2xl font-semibold text-[var(--color-ink-900)]">{es.finalScore}</p>
              <ProgressBar value={es.finalScore} max={100} color={bandColorHex(es.riskBand)} showValue={false} />
            </div>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Six-Dimension Breakdown" />
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="75%">
                <PolarGrid stroke="var(--color-border)" />
                <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 10, fill: "var(--color-ink-500)" }} />
                <PolarRadiusAxis tick={false} axisLine={false} />
                <Radar dataKey="value" stroke="var(--color-brand-600)" fill="var(--color-brand-500)" fillOpacity={0.35} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 space-y-3">
            {DIMENSION_META.map((d) => (
              <div key={d.label}>
                <div className="mb-1 flex items-center gap-1 text-sm text-[var(--color-ink-700)]">
                  {d.label}
                  <InfoDot text={d.tooltip} />
                </div>
                <ProgressBar value={es.dimensions[d.key]} max={d.max} />
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader title="Top Strengths" />
            {data.positiveIndicators.length === 0 ? (
              <p className="text-sm text-[var(--color-ink-500)]">No standout strengths identified.</p>
            ) : (
              <ul className="space-y-2 text-sm text-[var(--color-ink-700)]">
                {data.positiveIndicators.map((p) => (
                  <li key={p} className="flex gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-band-good)]" />
                    {p}
                  </li>
                ))}
              </ul>
            )}
          </Card>
          <Card>
            <CardHeader title="Top Risks" />
            <ul className="space-y-2 text-sm text-[var(--color-ink-700)]">
              {data.riskIndicators.map((r) => (
                <li key={r} className="flex gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-band-highrisk)]" />
                  {r}
                </li>
              ))}
            </ul>
          </Card>
          {data.anomalies.length > 0 && (
            <Card>
              <CardHeader title="Notable Anomalies" />
              <ul className="space-y-2 text-sm text-[var(--color-ink-700)]">
                {data.anomalies.map((a) => (
                  <li key={a} className="flex gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-band-average)]" />
                    {a}
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={() => navigate(`/msme/${id}/recommendation`)}>View Recommendation →</Button>
      </div>
    </div>
  );
}
