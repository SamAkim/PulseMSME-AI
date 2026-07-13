import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { MsmeListItem } from "../lib/types";
import { DEMO_ARCHETYPE_LABELS } from "../lib/types";
import { Card } from "../components/Card";
import { Badge, RiskBandBadge } from "../components/Badge";
import { Skeleton } from "../components/Skeleton";
import { ErrorState, EmptyState } from "../components/States";

export default function MsmeSelectionPage() {
  const [items, setItems] = useState<MsmeListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [sector, setSector] = useState("");
  const [city, setCity] = useState("");

  const load = () => {
    setError(null);
    api
      .listMsmes()
      .then(setItems)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load MSMEs"));
  };

  useEffect(load, []);

  const sectors = useMemo(() => Array.from(new Set((items ?? []).map((i) => i.sector))).sort(), [items]);
  const cities = useMemo(() => Array.from(new Set((items ?? []).map((i) => i.city))).sort(), [items]);

  const filtered = (items ?? []).filter((i) => {
    if (search && !i.businessName.toLowerCase().includes(search.toLowerCase())) return false;
    if (sector && i.sector !== sector) return false;
    if (city && i.city !== city) return false;
    return true;
  });

  const navigate = useNavigate();

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">Select an MSME</h1>
          <p className="mt-1 text-sm text-[var(--color-ink-500)]">
            Choose a business to begin its financial health assessment. Demo archetypes are badged for quick access.
          </p>
        </div>
        <button
          id="add-msme-btn"
          onClick={() => navigate("/msme/add")}
          className="shrink-0 flex items-center gap-2 rounded-lg bg-[var(--color-brand-500)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--color-brand-600)] transition-colors shadow-sm"
        >
          <span className="text-base leading-none">+</span> Add New MSME
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by business name…"
          className="min-w-56 flex-1 rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-500)]"
        />
        <select
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          className="rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-500)]"
        >
          <option value="">All sectors</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-500)]"
        >
          <option value="">All cities</option>
          {cities.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {error && <ErrorState message={error} onRetry={load} />}

      {!error && items === null && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      )}

      {items !== null && filtered.length === 0 && (
        <EmptyState title="No MSMEs match your filters" description="Try clearing the search or filters." />
      )}

      {filtered.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((item) => (
            <Link key={item.msmeId} to={`/msme/${item.msmeId}/public`}>
              <Card className="h-full transition-shadow hover:shadow-md">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-semibold text-[var(--color-ink-900)]">{item.businessName}</p>
                  {item.isDemoArchetype && <Badge tone="brand">{DEMO_ARCHETYPE_LABELS[item.archetype]}</Badge>}
                </div>
                <p className="mt-1 text-xs text-[var(--color-ink-500)]">
                  {item.sector} · {item.city}, {item.state}
                </p>
                <div className="mt-3 flex items-center gap-2">
                  {item.lastRiskBand ? (
                    <>
                      <span className="font-mono-data text-sm text-[var(--color-ink-700)]">{item.lastFinalScore}</span>
                      <RiskBandBadge band={item.lastRiskBand} size="sm" />
                    </>
                  ) : (
                    <span className="text-xs text-[var(--color-ink-300)]">Not yet assessed this session</span>
                  )}
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
