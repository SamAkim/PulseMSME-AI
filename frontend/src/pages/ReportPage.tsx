import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { ReportPayload } from "../lib/types";
import { DEMO_ARCHETYPE_LABELS } from "../lib/types";
import { formatInr, formatDateTime } from "../lib/format";
import { Card, CardHeader } from "../components/Card";
import { Button } from "../components/Button";
import { RiskBandBadge, Badge } from "../components/Badge";
import { PulseMark } from "../components/PulseMark";
import { SkeletonCard } from "../components/Skeleton";
import { ErrorState } from "../components/States";
import { useAppConfig } from "../lib/AppConfigContext";

export default function ReportPage() {
  const { id = "" } = useParams();
  const config = useAppConfig();
  const [data, setData] = useState<ReportPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    api
      .getReport(id)
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load the report"));
  };

  useEffect(load, [id]);

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
        <ErrorState message={error} onRetry={load} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8 sm:px-6">
        <SkeletonCard />
      </div>
    );
  }

  const { profile, publicScore, enhancedScore, recommendation } = data;
  const master = profile.master;

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6 print:px-0 print:py-4">
      <div className="no-print flex justify-end">
        <Button onClick={() => window.print()}>Print / Save as PDF</Button>
      </div>

      <div className="flex items-center justify-between border-b border-[var(--color-border)] pb-4">
        <div className="flex items-center gap-2.5">
          <PulseMark size={28} />
          <div>
            <p className="font-display text-sm font-semibold text-[var(--color-ink-900)]">{config.appName}</p>
            <p className="text-xs text-[var(--color-ink-500)]">MSME Financial Health Report</p>
          </div>
        </div>
        <p className="text-xs text-[var(--color-ink-500)]">Generated {formatDateTime(data.generatedAt)}</p>
      </div>

      <div className="flex items-center gap-2">
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">{master.business_name}</h1>
        {profile.isDemoArchetype && <Badge tone="brand">{DEMO_ARCHETYPE_LABELS[master.archetype]}</Badge>}
      </div>
      <p className="-mt-4 text-sm text-[var(--color-ink-500)]">
        {master.sector} · {master.city}, {master.state} · {master.business_age_years.toFixed(0)} years ·{" "}
        {master.legal_structure}
      </p>

      <Card>
        <CardHeader title="Data Sources" />
        <p className="text-sm text-[var(--color-ink-700)]">
          Consent status: <strong>{profile.consentStatus.replace("_", " ")}</strong>
          {profile.grantedSources.length > 0 && ` — ${profile.grantedSources.join(", ").toUpperCase()}`}
        </p>
      </Card>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader title="Public Score (Layer 1)" />
          {publicScore ? (
            <>
              <p className="font-display text-3xl font-semibold text-[var(--color-ink-900)]">
                {publicScore.preliminaryScore}/100
              </p>
              <p className="text-xs text-[var(--color-ink-500)]">
                {publicScore.confidencePercentage}% confidence — {publicScore.confidenceLabel}
              </p>
            </>
          ) : (
            <p className="text-sm text-[var(--color-ink-500)]">Not available</p>
          )}
        </Card>
        <Card>
          <CardHeader title="Enhanced Score (Layer 2)" />
          {enhancedScore ? (
            <>
              <div className="flex items-center gap-2">
                <p className="font-display text-3xl font-semibold text-[var(--color-ink-900)]">
                  {enhancedScore.finalScore}/100
                </p>
                <RiskBandBadge band={enhancedScore.riskBand} size="sm" />
              </div>
              <p className="text-xs text-[var(--color-ink-500)]">{enhancedScore.confidenceScore}% confidence</p>
            </>
          ) : (
            <p className="text-sm text-[var(--color-ink-500)]">Consent-based data not granted</p>
          )}
        </Card>
      </div>

      {enhancedScore && (
        <Card>
          <CardHeader title="Six-Dimension Breakdown" />
          <table className="w-full text-sm">
            <tbody>
              {[
                ["Cash-Flow Stability", enhancedScore.dimensions.cashFlowStability, 25],
                ["Compliance & Discipline", enhancedScore.dimensions.compliance, 20],
                ["Revenue & Growth", enhancedScore.dimensions.revenueAndGrowth, 20],
                ["Repayment Capacity", enhancedScore.dimensions.repaymentCapacity, 20],
                ["Operational Stability", enhancedScore.dimensions.operationalStability, 10],
                ["Digital Reputation", enhancedScore.dimensions.digitalReputation, 5],
              ].map(([label, value, max]) => (
                <tr key={label as string} className="border-b border-[var(--color-border)] last:border-0">
                  <td className="py-1.5 text-[var(--color-ink-700)]">{label}</td>
                  <td className="font-mono-data py-1.5 text-right text-[var(--color-ink-900)]">
                    {(value as number).toFixed(1)} / {max}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader title="Strengths" />
          <ul className="space-y-1 text-sm text-[var(--color-ink-700)]">
            {data.positiveIndicators.map((p) => (
              <li key={p}>• {p}</li>
            ))}
          </ul>
        </Card>
        <Card>
          <CardHeader title="Risks" />
          <ul className="space-y-1 text-sm text-[var(--color-ink-700)]">
            {data.riskIndicators.map((r) => (
              <li key={r}>• {r}</li>
            ))}
          </ul>
        </Card>
      </div>

      <Card>
        <CardHeader title="AI Health Summary" />
        <p className="text-sm leading-relaxed text-[var(--color-ink-700)]">{data.healthSummary}</p>
      </Card>

      {recommendation && (
        <Card>
          <CardHeader title={`Recommendation: ${recommendation.product}`} />
          <p className="text-sm leading-relaxed text-[var(--color-ink-700)]">{recommendation.rationale}</p>
          {recommendation.eligibility?.eligible && (
            <p className="font-display mt-2 text-xl font-semibold text-[var(--color-ink-900)]">
              Indicative amount: {formatInr(recommendation.eligibility.indicativeAmount)}
            </p>
          )}
        </Card>
      )}

      <p className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-sunken)] px-4 py-3 text-xs leading-relaxed text-[var(--color-ink-500)] print:bg-transparent">
        {data.disclaimer}
      </p>
    </div>
  );
}
