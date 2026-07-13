import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react";
import type { AssessmentResponse } from "./types";

interface AssessmentContextValue {
  get: (msmeId: string) => AssessmentResponse | undefined;
  set: (msmeId: string, data: AssessmentResponse) => void;
}

const AssessmentContext = createContext<AssessmentContextValue | null>(null);

export function AssessmentProvider({ children }: { children: ReactNode }) {
  const storeRef = useRef<Map<string, AssessmentResponse>>(new Map());
  const [, forceRender] = useState(0);

  const get = useCallback((msmeId: string) => storeRef.current.get(msmeId), []);
  const set = useCallback((msmeId: string, data: AssessmentResponse) => {
    storeRef.current.set(msmeId, data);
    forceRender((n) => n + 1);
  }, []);

  return <AssessmentContext.Provider value={{ get, set }}>{children}</AssessmentContext.Provider>;
}

export function useAssessmentStore() {
  const ctx = useContext(AssessmentContext);
  if (!ctx) throw new Error("useAssessmentStore must be used within AssessmentProvider");
  return ctx;
}
