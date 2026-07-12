import type { RiskBand } from "../lib/types";
import { bandColorHex } from "../lib/riskBand";

interface ScoreRingProps {
  score: number;
  band?: RiskBand;
  size?: number;
  label?: string;
}

export function ScoreRing({ score, band, size = 160, label }: ScoreRingProps) {
  const strokeWidth = size * 0.09;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference * (1 - clamped / 100);
  const color = band ? bandColorHex(band) : "var(--color-brand-600)";

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90" role="img" aria-label={`Score ${score} out of 100`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-surface-sunken)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1)" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl font-semibold text-[var(--color-ink-900)]">{Math.round(score)}</span>
        <span className="text-xs text-[var(--color-ink-500)]">/ 100</span>
        {label && <span className="mt-1 text-xs font-medium text-[var(--color-ink-500)]">{label}</span>}
      </div>
    </div>
  );
}
