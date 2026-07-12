import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { MsmeProfile, PublicScoreResult } from "../lib/types";
import { DEMO_ARCHETYPE_LABELS } from "../lib/types";
import { Card, CardHeader } from "../components/Card";
import { Badge } from "../components/Badge";
import { Button } from "../components/Button";
import { ScoreRing } from "../components/ScoreRing";
import { SkeletonCard } from "../components/Skeleton";
import { ErrorState } from "../components/States";
import { JourneySteps } from "../components/JourneySteps";
import { InfoDot } from "../components/Tooltip";

export default function PublicAssessmentPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<MsmeProfile | null>(null);
  const [score, setScore] = useState<PublicScoreResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    setProfile(null);
    setScore(null);
    Promise.all([api.getProfile(id), api.getPublicAssessment(id)])
      .then(([p, s]) => {
        setProfile(p);
        setScore(s);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load the public assessment"));
  };

  useEffect(load, [id]);

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
        <ErrorState message={error} onRetry={load} />
      </div>
    );
  }

  if (!profile || !score) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 px-4 py-8 sm:px-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  const { master } = profile;

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
      <JourneySteps current="public" />

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">{master.business_name}</h1>
            {profile.isDemoArchetype && <Badge tone="brand">{DEMO_ARCHETYPE_LABELS[master.archetype]}</Badge>}
          </div>
          <p className="mt-1 text-sm text-[var(--color-ink-500)]">
            {master.sector} · {master.city}, {master.state} · {master.business_age_years.toFixed(0)} years in operation
          </p>
        </div>
        <Link to="/msme" className="text-sm font-medium text-[var(--color-brand-700)] hover:underline">
          ← Back to selection
        </Link>
      </div>

      <Card>
        <p className="mb-4 rounded-lg border border-[var(--color-band-average)]/25 bg-[var(--color-band-average-bg)] px-4 py-3 text-sm text-[var(--color-band-average)]">
          Public signals provide a preliminary view and should not be treated as direct evidence of repayment
          capacity.
        </p>
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          <ScoreRing score={score.preliminaryScore} label="Preliminary" />
          <div className="flex-1 space-y-3">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-[var(--color-ink-500)]">
                Public Data Confidence
              </p>
              <p className="font-display text-xl font-semibold text-[var(--color-ink-900)]">
                {score.confidencePercentage}% — {score.confidenceLabel}
              </p>
              <p className="text-xs text-[var(--color-ink-500)]">Capped at 70% for public-only signals</p>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
              {Object.entries(score.componentScores).map(([key, value]) => (
                <div key={key}>
                  <p className="text-xs text-[var(--color-ink-500)]">{formatComponentLabel(key)}</p>
                  <p className="font-mono-data text-sm font-medium text-[var(--color-ink-900)]">{value.toFixed(0)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader title="Positive Indicators" />
          {score.positiveIndicators.length === 0 ? (
            <p className="text-sm text-[var(--color-ink-500)]">No strong public positive signals detected.</p>
          ) : (
            <ul className="space-y-2 text-sm text-[var(--color-ink-700)]">
              {score.positiveIndicators.map((p) => (
                <li key={p} className="flex gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-band-good)]" />
                  {p}
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <CardHeader title="Warning Indicators" />
          <ul className="space-y-2 text-sm text-[var(--color-ink-700)]">
            {score.warningIndicators.map((w) => (
              <li key={w} className="flex gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--color-band-average)]" />
                {w}
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card>
        <div className="flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-between sm:text-left">
          <div className="flex items-center gap-1.5">
            <p className="text-sm text-[var(--color-ink-700)]">
              For a full risk assessment, request consent to the MSME's GST, UPI, banking, and EPFO data.
            </p>
            <InfoDot text="This simulates the MSME granting consent via an Account Aggregator-style flow. No real data is shared." />
          </div>
          <Button onClick={() => navigate(`/msme/${id}/consent`)}>Request Consent-Based Assessment</Button>
        </div>
      </Card>
    </div>
  );
}

function formatComponentLabel(key: string): string {
  const labels: Record<string, string> = {
    customerReputation: "Customer Reputation",
    digitalPresence: "Digital Presence",
    businessMaturity: "Business Maturity",
    engagementActivity: "Engagement & Activity",
    listingConsistency: "Listing Consistency",
  };
  return labels[key] ?? key;
}
