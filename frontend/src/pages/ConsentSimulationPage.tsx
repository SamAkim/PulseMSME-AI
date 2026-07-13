import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { ConsentSource, MsmeProfile } from "../lib/types";
import { CONSENT_SOURCE_LABELS } from "../lib/types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/States";
import { JourneySteps } from "../components/JourneySteps";

const ALL_SOURCES: ConsentSource[] = ["gst", "upi", "aa_banking", "epfo"];

const SOURCE_DESCRIPTIONS: Record<ConsentSource, string> = {
  gst: "GST return filings, turnover, and filing timeliness",
  upi: "UPI transaction inflows and settlement history",
  aa_banking: "Bank statements via Account Aggregator consent",
  epfo: "EPFO employee contribution and payroll history",
};

export default function ConsentSimulationPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<MsmeProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<ConsentSource>>(new Set(ALL_SOURCES));
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .getProfile(id)
      .then(setProfile)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load MSME profile"));
  }, [id]);

  const toggle = (source: ConsentSource) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(source)) next.delete(source);
      else next.add(source);
      return next;
    });
  };

  const handleGrant = async () => {
    setSubmitting(true);
    try {
      await api.grantConsent(id, Array.from(selected));
      navigate(`/msme/${id}/processing`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not record consent");
      setSubmitting(false);
    }
  };

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <ErrorState message={error} />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <Skeleton className="h-64" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 px-4 py-8 sm:px-6">
      <JourneySteps current="consent" />

      <div>
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">Simulate MSME Consent</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-500)]">
          For {profile.master.business_name}. In production this would route through an Account Aggregator /
          ULI consent flow; here it is a simulated toggle for demo purposes.
        </p>
      </div>

      <Card>
        <div className="space-y-3">
          {ALL_SOURCES.map((source) => (
            <label
              key={source}
              className="flex cursor-pointer items-start gap-3 rounded-lg border border-[var(--color-border)] p-3 hover:bg-[var(--color-surface-sunken)]/50"
            >
              <input
                type="checkbox"
                checked={selected.has(source)}
                onChange={() => toggle(source)}
                className="mt-0.5 h-4 w-4 rounded border-[var(--color-border)] text-[var(--color-brand-700)] focus:ring-[var(--color-brand-500)]"
              />
              <div>
                <p className="text-sm font-medium text-[var(--color-ink-900)]">{CONSENT_SOURCE_LABELS[source]}</p>
                <p className="text-xs text-[var(--color-ink-500)]">{SOURCE_DESCRIPTIONS[source]}</p>
              </div>
            </label>
          ))}
        </div>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-xs text-[var(--color-ink-500)]">
          {selected.size} of {ALL_SOURCES.length} data sources selected
        </p>
        <Button onClick={handleGrant} disabled={selected.size === 0 || submitting}>
          {submitting ? "Granting…" : "Grant Consent and Continue"}
        </Button>
      </div>
    </div>
  );
}
