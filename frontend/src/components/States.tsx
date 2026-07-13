import type { ReactNode } from "react";
import { Button } from "./Button";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-[var(--color-band-highrisk)]/20 bg-[var(--color-band-highrisk-bg)] p-8 text-center">
      <p className="text-sm font-medium text-[var(--color-band-highrisk)]">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-[var(--color-border)] bg-[var(--color-surface)] p-10 text-center">
      <p className="text-sm font-semibold text-[var(--color-ink-900)]">{title}</p>
      {description && <p className="max-w-sm text-sm text-[var(--color-ink-500)]">{description}</p>}
      {action}
    </div>
  );
}

export function DisclaimerBanner() {
  return (
    <p className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-sunken)] px-4 py-3 text-xs leading-relaxed text-[var(--color-ink-500)]">
      Indicative assessment for demonstration purposes. Final lending decisions require bank policy
      checks, bureau data, KYC, AML, and human credit review.
    </p>
  );
}
