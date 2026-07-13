import type { ReactNode } from "react";
import type { RiskBand } from "../lib/types";
import { bandStyle } from "../lib/riskBand";

export function RiskBandBadge({ band, size = "md" }: { band: RiskBand; size?: "sm" | "md" }) {
  const style = bandStyle(band);
  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses}`}
      style={{ backgroundColor: style.bg, color: style.fg }}
    >
      {style.text}
    </span>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "brand" | "warning";
}) {
  const toneClasses: Record<string, string> = {
    neutral: "bg-[var(--color-surface-sunken)] text-[var(--color-ink-700)]",
    brand: "bg-[var(--color-brand-100)] text-[var(--color-brand-700)]",
    warning: "bg-[var(--color-band-average-bg)] text-[var(--color-band-average)]",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}
