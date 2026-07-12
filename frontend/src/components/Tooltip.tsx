import { useState, type ReactNode } from "react";

export function Tooltip({ text, children }: { text: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <span
      className="relative inline-flex"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      {children}
      {open && (
        <span
          role="tooltip"
          className="pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 w-max max-w-64 -translate-x-1/2 rounded-md bg-[var(--color-ink-900)] px-2.5 py-1.5 text-xs text-white shadow-lg"
        >
          {text}
        </span>
      )}
    </span>
  );
}

export function InfoDot({ text }: { text: string }) {
  return (
    <Tooltip text={text}>
      <button
        type="button"
        aria-label="More information"
        className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-[var(--color-surface-sunken)] text-[10px] font-semibold text-[var(--color-ink-500)] hover:bg-[var(--color-border)]"
      >
        i
      </button>
    </Tooltip>
  );
}
