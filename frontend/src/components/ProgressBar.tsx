interface ProgressBarProps {
  value: number;
  max: number;
  color?: string;
  label?: string;
  showValue?: boolean;
}

export function ProgressBar({ value, max, color = "var(--color-brand-600)", label, showValue = true }: ProgressBarProps) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
  return (
    <div>
      {(label || showValue) && (
        <div className="mb-1 flex items-center justify-between text-sm">
          {label && <span className="text-[var(--color-ink-700)]">{label}</span>}
          {showValue && (
            <span className="font-mono-data text-[var(--color-ink-500)]">
              {value.toFixed(1)}/{max}
            </span>
          )}
        </div>
      )}
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-[var(--color-surface-sunken)]"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, backgroundColor: color, transition: "width 0.6s cubic-bezier(0.4,0,0.2,1)" }}
        />
      </div>
    </div>
  );
}
