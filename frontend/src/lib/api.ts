import type {
  AppConfig,
  AssessmentResponse,
  ChatMessage,
  ChatResponse,
  ConsentSource,
  ConsentStatus,
  CreateMsmeRequest,
  DashboardMetrics,
  MsmeListItem,
  MsmeProfile,
  PublicScoreResult,
  ReportPayload,
} from "./types";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getConfig: () => request<AppConfig>("/config"),

  listMsmes: (params?: { search?: string; sector?: string; city?: string; riskBand?: string }) => {
    const qs = new URLSearchParams();
    if (params?.search) qs.set("search", params.search);
    if (params?.sector) qs.set("sector", params.sector);
    if (params?.city) qs.set("city", params.city);
    if (params?.riskBand) qs.set("riskBand", params.riskBand);
    const suffix = qs.toString() ? `?${qs.toString()}` : "";
    return request<MsmeListItem[]>(`/msme${suffix}`);
  },

  getProfile: (id: string) => request<MsmeProfile>(`/msme/${id}`),

  getPublicAssessment: (id: string) => request<PublicScoreResult>(`/msme/${id}/public-assessment`),

  grantConsent: (id: string, sources: ConsentSource[]) =>
    request<{ msmeId: string; consentStatus: ConsentStatus; grantedSources: ConsentSource[] }>(
      `/msme/${id}/consent`,
      { method: "POST", body: JSON.stringify({ sources }) },
    ),

  assess: (id: string) => request<AssessmentResponse>(`/msme/${id}/assess`, { method: "POST" }),

  chat: (id: string, message: string, history: ChatMessage[]) =>
    request<ChatResponse>(`/msme/${id}/chat`, {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),

  getReport: (id: string) => request<ReportPayload>(`/msme/${id}/report`),

  getDashboard: () => request<DashboardMetrics>("/dashboard"),

  streamAssessUrl: (id: string) => `/api/msme/${id}/assess/stream`,

  createMsme: (data: CreateMsmeRequest) =>
    request<MsmeListItem>("/msme", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

