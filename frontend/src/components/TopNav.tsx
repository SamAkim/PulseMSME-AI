import { Link, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { PulseMark } from "./PulseMark";
import { useAppConfig } from "../lib/AppConfigContext";

export function TopNav() {
  const config = useAppConfig();
  const location = useLocation();

  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("theme");
      if (saved) return saved === "dark";
      return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    return false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  const navLink = (to: string, label: string) => {
    const active = location.pathname === to;
    return (
      <Link
        to={to}
        className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
          active
            ? "text-[var(--color-brand-500)] bg-[var(--color-surface-sunken)]"
            : "text-[var(--color-ink-500)] hover:text-[var(--color-ink-900)] hover:bg-[var(--color-surface-sunken)]/50"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="no-print sticky top-0 z-30 border-b border-[var(--color-border)] bg-[var(--color-surface)]/80 backdrop-blur-md transition-colors">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <PulseMark size={28} />
          <div className="leading-tight">
            <div className="font-display text-base font-semibold text-[var(--color-ink-900)]">{config.appName}</div>
            <div className="hidden text-[11px] text-[var(--color-ink-500)] sm:block">{config.appTagline}</div>
          </div>
        </Link>
        <div className="flex items-center gap-3">
          <nav className="flex items-center gap-1">
            {navLink("/", "Dashboard")}
            {navLink("/msme", "MSMEs")}
          </nav>
          
          <div className="h-4 w-px bg-[var(--color-border)]" />
          
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="rounded-lg p-2 text-[var(--color-ink-500)] hover:text-[var(--color-ink-900)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m12.728 12.728l.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
              </svg>
            ) : (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
