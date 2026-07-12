import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import type { ChatMessage, MsmeProfile } from "../lib/types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Skeleton } from "../components/Skeleton";
import { JourneySteps } from "../components/JourneySteps";

const SUGGESTED_QUESTIONS = [
  "Why is this MSME classified as good?",
  "What factors reduced its score?",
  "How did consent-based data change the assessment?",
  "What is the biggest repayment risk?",
  "Which credit product is suitable?",
  "What additional information is needed?",
  "How can this MSME improve its financial health?",
];

export default function ChatAssistantPage() {
  const { id = "" } = useParams();
  const [profile, setProfile] = useState<MsmeProfile | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getProfile(id).then(setProfile).catch(() => undefined);
  }, [id]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || sending) return;
    setError(null);
    const userMessage: ChatMessage = { role: "user", content: text };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setSending(true);
    try {
      const res = await api.chat(id, text, messages);
      setMessages([...nextMessages, { role: "assistant", content: res.reply }]);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "The assistant could not respond. Please try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8 sm:px-6">
      <JourneySteps current="recommendation" />

      <div>
        <h1 className="font-display text-2xl font-semibold text-[var(--color-ink-900)]">AI Credit Assistant</h1>
        {profile ? (
          <p className="mt-1 text-sm text-[var(--color-ink-500)]">
            Answering only from {profile.master.business_name}'s assessment data.
          </p>
        ) : (
          <Skeleton className="mt-1 h-4 w-64" />
        )}
      </div>

      <Card className="flex h-[28rem] flex-col p-0">
        <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
              <p className="text-sm text-[var(--color-ink-500)]">Ask a question about this MSME's assessment.</p>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTED_QUESTIONS.slice(0, 4).map((q) => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="rounded-full border border-[var(--color-border)] px-3 py-1.5 text-xs text-[var(--color-ink-700)] hover:bg-[var(--color-surface-sunken)]"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-[var(--color-brand-700)] text-white"
                    : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-900)]"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="rounded-xl bg-[var(--color-surface-sunken)] px-3.5 py-2.5 text-sm text-[var(--color-ink-500)]">
                Thinking…
              </div>
            </div>
          )}
        </div>

        {messages.length > 0 && (
          <div className="flex flex-wrap gap-2 border-t border-[var(--color-border)] px-4 py-2">
            {SUGGESTED_QUESTIONS.filter((q) => !messages.some((m) => m.content === q)).slice(0, 3).map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="rounded-full border border-[var(--color-border)] px-2.5 py-1 text-xs text-[var(--color-ink-500)] hover:bg-[var(--color-surface-sunken)]"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {error && <p className="px-4 pb-1 text-xs text-[var(--color-band-highrisk)]">{error}</p>}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="flex gap-2 border-t border-[var(--color-border)] p-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this MSME's assessment…"
            className="flex-1 rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-500)]"
          />
          <Button type="submit" disabled={sending || !input.trim()}>
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
}
