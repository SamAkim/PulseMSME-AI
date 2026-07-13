import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md";
}

const VARIANTS: Record<string, string> = {
  primary:
    "bg-[var(--color-brand-500)] text-[var(--color-ink-950)] font-semibold hover:bg-[var(--color-brand-600)] focus-visible:outline-[var(--color-brand-500)] shadow-sm shadow-[var(--color-brand-500)]/10",
  secondary:
    "bg-transparent text-[var(--color-ink-900)] border border-[var(--color-border)] hover:bg-[var(--color-surface-raised)] focus-visible:outline-[var(--color-brand-500)]",
  ghost:
    "bg-transparent text-[var(--color-ink-700)] hover:bg-[var(--color-surface-raised)]/50 focus-visible:outline-[var(--color-brand-500)]",
};

const SIZES: Record<string, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2.5 text-sm",
};

export function Button({ variant = "primary", size = "md", className = "", ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...props}
    />
  );
}
