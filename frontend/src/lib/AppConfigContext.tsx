import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "./api";
import type { AppConfig } from "./types";

const FALLBACK: AppConfig = { appName: "PulseMSME AI", appTagline: "MSME Financial Health Card" };

const AppConfigContext = createContext<AppConfig>(FALLBACK);

export function AppConfigProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<AppConfig>(FALLBACK);

  useEffect(() => {
    let cancelled = false;
    api
      .getConfig()
      .then((c) => {
        if (!cancelled) setConfig(c);
      })
      .catch(() => {
        /* keep fallback */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    document.title = `${config.appName} — ${config.appTagline}`;
  }, [config]);

  return <AppConfigContext.Provider value={config}>{children}</AppConfigContext.Provider>;
}

export function useAppConfig() {
  return useContext(AppConfigContext);
}
