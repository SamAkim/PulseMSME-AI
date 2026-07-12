const STEPS = [
  { key: "public", label: "Public Assessment" },
  { key: "consent", label: "Consent" },
  { key: "processing", label: "Agent Processing" },
  { key: "health-card", label: "Health Card" },
  { key: "recommendation", label: "Recommendation" },
];

export function JourneySteps({ current }: { current: string }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current);
  return (
    <ol className="no-print flex flex-wrap items-center gap-x-1 gap-y-2 text-xs">
      {STEPS.map((step, i) => {
        const state = i < currentIndex ? "done" : i === currentIndex ? "current" : "upcoming";
        return (
          <li key={step.key} className="flex items-center gap-1">
            <span
              className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-semibold ${
                state === "done"
                  ? "bg-[var(--color-brand-600)] text-white"
                  : state === "current"
                    ? "bg-[var(--color-ink-900)] text-white"
                    : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-500)]"
              }`}
            >
              {i + 1}
            </span>
            <span className={state === "upcoming" ? "text-[var(--color-ink-300)]" : "text-[var(--color-ink-700)]"}>
              {step.label}
            </span>
            {i < STEPS.length - 1 && <span className="mx-1.5 h-px w-4 bg-[var(--color-border)]" />}
          </li>
        );
      })}
    </ol>
  );
}
