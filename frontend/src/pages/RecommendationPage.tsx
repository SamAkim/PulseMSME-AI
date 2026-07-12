import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { AssessmentResponse } from "../lib/types";
import { formatInr } from "../lib/format";
import { Card, CardHeader } from "../components/Card";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";
import { SkeletonCard } from "../components/Skeleton";
import { ErrorState } from "../components/States";
import { JourneySteps } from "../components/JourneySteps";
import { useAssessmentStore } from "../lib/AssessmentContext";

export default function RecommendationPage() {
  const { id = "" } = useParams();
  const { get, set } = useAssessmentStore();
  const [data, setData] = useState<AssessmentResponse | null>(get(id) ?? null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(!data);
  const [showFormula, setShowFormula] = useState(false);

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
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load the recommendation"))
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
      </div>
    );
  }

  const rec = data.recommendation;

  if (!rec) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <ErrorState message="No recommendation available yet — grant consent and run the assessment first." />
      </div>
    );
  }

  const elig = rec.eligibility;

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
      <JourneySteps current="recommendation" />

      <div>
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">Credit Recommendation</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-500)]">Data-driven, indicative — not a final credit decision.</p>
      </div>

      <Card>
        <CardHeader title={rec.product} subtitle={rec.justification} />
        <p className="text-sm leading-relaxed text-[var(--color-ink-700)]">{rec.rationale}</p>
      </Card>

      {elig && (
        <Card>
          <CardHeader title="Indicative Loan Eligibility" subtitle="Secondary figure — always read alongside the recommendation above" />
          {elig.eligible ? (
            <>
              <p className="font-display text-3xl font-semibold text-[var(--color-ink-900)]">
                {formatInr(elig.indicativeAmount)}
              </p>
              <p className="mt-1 text-sm text-[var(--color-ink-500)]">
                Tenure {elig.tenureRangeMonths[0]}–{elig.tenureRangeMonths[1]} months
              </p>
            </>
          ) : (
            <p className="text-sm text-[var(--color-ink-700)]">Not eligible for an indicative amount under the current risk band.</p>
          )}
          <button
            type="button"
            onClick={() => setShowFormula((v) => !v)}
            className="mt-3 text-xs font-medium text-[var(--color-brand-700)] hover:underline"
          >
            {showFormula ? "Hide" : "How was this calculated?"}
          </button>
          {showFormula && (
            <p className="font-mono-data mt-2 rounded-lg bg-[var(--color-surface-sunken)] p-3 text-xs leading-relaxed text-[var(--color-ink-700)]">
              {elig.formulaExplanation}
            </p>
          )}
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader title="Risk Conditions" />
          <ul className="space-y-1.5 text-sm text-[var(--color-ink-700)]">
            {rec.riskConditions.map((r) => (
              <li key={r}>• {r}</li>
            ))}
          </ul>
        </Card>
        <Card>
          <CardHeader title="Required Manual Checks" />
          <ul className="space-y-1.5 text-sm text-[var(--color-ink-700)]">
            {rec.requiredManualChecks.map((c) => (
              <li key={c}>• {c}</li>
            ))}
          </ul>
        </Card>
      </div>

      {rec.missingDocuments.length > 0 && (
        <Card>
          <CardHeader title="Missing Documents / Verifications" />
          <div className="flex flex-wrap gap-2">
            {rec.missingDocuments.map((d) => (
              <Badge key={d} tone="warning">
                {d}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      <Card tone="dark">
        <p className="text-sm font-medium">Next Best Action</p>
        <p className="mt-1 text-sm text-white/80">{rec.nextBestAction}</p>
      </Card>

      <p className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-sunken)] px-4 py-3 text-xs leading-relaxed text-[var(--color-ink-500)]">
        {rec.disclaimer}
      </p>

      <div className="flex flex-wrap justify-end gap-3">
        <Link to={`/msme/${id}/chat`}>
          <Button variant="secondary">Ask AI Credit Assistant</Button>
        </Link>
        <Link to={`/msme/${id}/report`}>
          <Button>View Printable Report →</Button>
        </Link>
      </div>
    </div>
  );
}
