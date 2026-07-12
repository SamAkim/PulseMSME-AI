import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../lib/api";
import type { AgentStatus, AssessmentResponse } from "../lib/types";
import { Card } from "../components/Card";
import { ErrorState } from "../components/States";
import { JourneySteps } from "../components/JourneySteps";
import { useAssessmentStore } from "../lib/AssessmentContext";

const AGENT_ORDER = [
  "Data Ingestion Agent",
  "Financial Scoring Agent",
  "Risk & Insight Agent",
  "Credit Recommendation Agent",
];

export default function AgentProcessingPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const { set } = useAssessmentStore();
  const [events, setEvents] = useState<AgentStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const doneRef = useRef(false);

  useEffect(() => {
    doneRef.current = false;
    setEvents([]);
    setError(null);

    const source = new EventSource(api.streamAssessUrl(id));

    source.addEventListener("agent_status", (e: MessageEvent) => {
      const status: AgentStatus = JSON.parse(e.data);
      setEvents((prev) => [...prev, status]);
    });

    source.addEventListener("final_result", (e: MessageEvent) => {
      const result: AssessmentResponse = JSON.parse(e.data);
      set(id, result);
      doneRef.current = true;
      source.close();
      window.setTimeout(() => navigate(`/msme/${id}/health-card`), 400);
    });

    source.onerror = () => {
      if (!doneRef.current) {
        setError("Lost connection to the assessment stream.");
      }
      source.close();
    };

    return () => source.close();
  }, [id, navigate, set]);

  const latestByAgent = new Map<string, AgentStatus>();
  for (const e of events) latestByAgent.set(e.agent, e);

  return (
    <div className="mx-auto max-w-2xl space-y-6 px-4 py-8 sm:px-6">
      <JourneySteps current="processing" />

      <div>
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">Running Agent Pipeline</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-500)]">
          The LangGraph pipeline is ingesting data, scoring, and generating insights in real time.
        </p>
      </div>

      {error && <ErrorState message={error} />}

      <Card>
        <ol className="space-y-3">
          {AGENT_ORDER.map((agentName) => {
            const status = latestByAgent.get(agentName);
            const state = status?.status ?? "pending";
            return (
              <li key={agentName} className="flex items-center gap-3">
                <StatusIcon state={state} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-[var(--color-ink-900)]">{agentName}</p>
                  <p className="truncate text-xs text-[var(--color-ink-500)]">
                    {status?.message ?? "Waiting…"}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      </Card>
    </div>
  );
}

function StatusIcon({ state }: { state: AgentStatus["status"] }) {
  if (state === "completed") {
    return (
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--color-band-good-bg)] text-[var(--color-band-good)]">
        ✓
      </span>
    );
  }
  if (state === "error") {
    return (
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--color-band-highrisk-bg)] text-[var(--color-band-highrisk)]">
        !
      </span>
    );
  }
  if (state === "running") {
    return (
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--color-brand-100)]">
        <span className="h-2.5 w-2.5 animate-ping rounded-full bg-[var(--color-brand-600)]" />
      </span>
    );
  }
  return <span className="h-6 w-6 shrink-0 rounded-full border-2 border-dashed border-[var(--color-border)]" />;
}
