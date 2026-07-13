import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RTooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { api, ApiError } from "../lib/api";
import type { DashboardMetrics } from "../lib/types";
import { Card, CardHeader } from "../components/Card";
import { RiskBandBadge } from "../components/Badge";
import { SkeletonCard } from "../components/Skeleton";
import { ErrorState } from "../components/States";
import { bandColorHex } from "../lib/riskBand";
import type { RiskBand } from "../lib/types";

const RISK_ORDER: RiskBand[] = ["High Risk", "Bad", "Average", "Good", "Excellent"];
const SECTOR_COLORS = ["#146356", "#1f9683", "#5b6472", "#9a7b0a", "#b5641f", "#a4342a", "#2b7a5b", "#9aa4b2", "#0c352f", "#c2703d"];

export default function DashboardPage() {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    setError(null);
    api
      .getDashboard()
      .then(setData)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load the dashboard"))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <ErrorState message={error ?? "Something went wrong"} onRetry={load} />
      </div>
    );
  }

  const riskData = RISK_ORDER.map((band) => ({ band, count: data.riskDistribution[band] ?? 0 }));
  const sectorData = Object.entries(data.sectorDistribution).map(([sector, count]) => ({ name: sector, value: count }));

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">Portfolio Dashboard</h1>
          <p className="mt-1 text-sm text-[var(--color-ink-500)]">
            Assessed MSME portfolio overview, synthetic demo data.
          </p>
        </div>
        <Link
          to="/msme"
          className="rounded-lg bg-[var(--color-brand-700)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--color-brand-900)]"
        >
          Browse MSMEs
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total MSMEs" value={data.totalMsmes.toString()} />
        <StatCard label="Average Score" value={data.averageScore.toFixed(1)} />
        <StatCard label="Excellent + Good" value={(data.excellentCount + data.goodCount).toString()} />
        <StatCard label="Requiring Review" value={data.requiringReviewCount.toString()} tone="warning" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Risk Band Distribution" subtitle="Across the full assessed portfolio" />
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskData} margin={{ left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="band" tick={{ fontSize: 11 }} stroke="var(--color-ink-500)" />
                <YAxis tick={{ fontSize: 11 }} stroke="var(--color-ink-500)" allowDecimals={false} />
                <RTooltip cursor={{ fill: "var(--color-surface-sunken)" }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {riskData.map((entry) => (
                    <Cell key={entry.band} fill={bandColorHex(entry.band)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Sector Distribution" subtitle="Number of MSMEs per sector" />
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sectorData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} paddingAngle={1}>
                  {sectorData.map((entry, i) => (
                    <Cell key={entry.name} fill={SECTOR_COLORS[i % SECTOR_COLORS.length]} />
                  ))}
                </Pie>
                <RTooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Recently Assessed"
          subtitle={
            data.publicOnlyCount + data.consentEnhancedCount > 0
              ? `${data.consentEnhancedCount} consent-enhanced · ${data.publicOnlyCount} public-only`
              : undefined
          }
        />
        {data.recentAssessments.length === 0 ? (
          <p className="text-sm text-[var(--color-ink-500)]">
            No consent has been granted yet this session. Visit an MSME and grant consent to see it here.
          </p>
        ) : (
          <div className="divide-y divide-[var(--color-border)]">
            {data.recentAssessments.map((item) => (
              <Link
                key={item.msmeId}
                to={`/msme/${item.msmeId}/public`}
                className="flex items-center justify-between gap-4 py-3 hover:bg-[var(--color-surface-sunken)]/50"
              >
                <div>
                  <p className="text-sm font-medium text-[var(--color-ink-900)]">{item.businessName}</p>
                  <p className="text-xs text-[var(--color-ink-500)]">
                    {item.sector} · {item.city}
                  </p>
                </div>
                {item.lastRiskBand && (
                  <div className="flex items-center gap-2">
                    <span className="font-mono-data text-sm text-[var(--color-ink-700)]">{item.lastFinalScore}</span>
                    <RiskBandBadge band={item.lastRiskBand} size="sm" />
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function StatCard({ label, value, tone }: { label: string; value: string; tone?: "warning" }) {
  return (
    <Card padded={false} className="p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--color-ink-500)]">{label}</p>
      <p
        className={`font-display mt-1 text-2xl font-semibold ${
          tone === "warning" ? "text-[var(--color-band-bad)]" : "text-[var(--color-ink-900)]"
        }`}
      >
        {value}
      </p>
    </Card>
  );
}
