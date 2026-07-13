import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  padded?: boolean;
  tone?: "default" | "dark";
}

const TONE_CLASSES: Record<string, string> = {
  default: "bg-[var(--color-surface-raised)] text-inherit",
  dark: "bg-[var(--color-ink-900)] text-white",
};

export function Card({ children, className = "", padded = true, tone = "default" }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-[var(--color-border)] shadow-sm cred-card-hover ${TONE_CLASSES[tone]} ${
        padded ? "p-5 sm:p-6" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action }: { title: ReactNode; subtitle?: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4">
      <div>
        <h2 className="text-base font-semibold text-[var(--color-ink-900)]">{title}</h2>
        {subtitle && <p className="mt-0.5 text-sm text-[var(--color-ink-500)]">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
