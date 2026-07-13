import { Link, useLocation } from "react-router-dom";
import { PulseMark } from "./PulseMark";
import { useAppConfig } from "../lib/AppConfigContext";

export function TopNav() {
  const config = useAppConfig();
  const location = useLocation();

  const navLink = (to: string, label: string) => {
    const active = location.pathname === to;
    return (
      <Link
        to={to}
        className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
          active ? "bg-white/10 text-white" : "text-white/70 hover:text-white"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="no-print sticky top-0 z-30 border-b border-black/20 bg-[var(--color-ink-900)]">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <PulseMark size={28} />
          <div className="leading-tight">
            <div className="font-display text-base font-semibold text-white">{config.appName}</div>
            <div className="hidden text-[11px] text-white/60 sm:block">{config.appTagline}</div>
          </div>
        </Link>
        <nav className="flex items-center gap-1">
          {navLink("/", "Dashboard")}
          {navLink("/msme", "MSMEs")}
        </nav>
      </div>
    </header>
  );
}
