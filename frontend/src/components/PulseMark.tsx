interface PulseMarkProps {
  size?: number;
  className?: string;
  animate?: boolean;
}

export function PulseMark({ size = 24, className = "", animate = false }: PulseMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      className={className}
      role="img"
      aria-label="PulseMSME AI"
    >
      <rect width="32" height="32" rx="7" fill="var(--color-ink-900)" />
      <path
        d="M3 17h5l2.5-8 4 15 3-11 2 4h9.5"
        fill="none"
        stroke="var(--color-brand-500)"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={animate ? "pulse-trace-path" : undefined}
      />
    </svg>
  );
}
