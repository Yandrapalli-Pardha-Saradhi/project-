import type { ChatRequest, ChatResponse, HealthResponse } from "../types/chat";

// Vercel builds must point at the separately deployed API. During local Vite
// development, an unset value keeps requests same-origin for the /api proxy.
const configuredApiOrigin = import.meta.env.VITE_API_BASE_URL?.trim().replace(/\/+$/, "");
const API_BASE = `${configuredApiOrigin || ""}/api`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail || `Request failed (${response.status})`);
  }
  try {
    return await response.json() as T;
  } catch {
    throw new Error("The server returned an invalid response.");
  }
}

export interface Temple {
  id: string;
  names: string[];
  state: string | null;
  district: string | null;
  area: string | null;
  description: string;
  history?: string;
  sources: { title: string; url: string; publisher?: string | null }[];
  location_source?: { title: string; url: string; publisher?: string | null } | null;
}
export interface TemplePage { items: Temple[]; total: number; limit: number; offset: number }
export interface TempleFacets { districts: string[]; temples: Temple[] }

export const checkHealth = () => request<HealthResponse>("/health");
export const sendChat = async (payload: ChatRequest, signal?: AbortSignal): Promise<ChatResponse> => {
  const result = await request<ChatResponse>("/chat", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), signal,
  });
  if (!result || typeof result.answer !== "string" || !Array.isArray(result.citations)
    || !result.citations.every(citation => citation && typeof citation.source_id === "string"
      && typeof citation.source_title === "string" && typeof citation.source_url === "string"
      && /^https?:\/\//i.test(citation.source_url))
    || typeof result.insufficient_evidence !== "boolean" || typeof result.generation_disabled !== "boolean") {
    throw new Error("The assistant returned an incomplete response.");
  }
  return result;
};
export const getStates = async (): Promise<string[]> => {
  const result = await request<unknown>("/temples/states");
  if (!Array.isArray(result) || !result.every(state => typeof state === "string")) {
    throw new Error("The temple catalogue returned invalid state data.");
  }
  return result;
};
export const getTemples = (filters: { query?: string; search?: string; state?: string; district?: string; area?: string; limit?: number; offset?: number }, signal?: AbortSignal) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (typeof value === "number") params.set(key, String(value));
    else if (value?.trim()) params.set(key, value.trim());
  });
  return request<unknown>(`/temples/?${params}`, { signal }).then(result => {
    const page = result as Partial<TemplePage> | null;
    if (!page || !Array.isArray(page.items) || typeof page.total !== "number"
      || !Number.isInteger(page.total) || !page.items.every(item => item && typeof item.id === "string"
        && Array.isArray(item.names) && item.names.length > 0 && item.names.every(name => typeof name === "string")
        && typeof item.description === "string" && Array.isArray(item.sources)
        && item.sources.every(source => source && typeof source.title === "string" && typeof source.url === "string" && /^https?:\/\//i.test(source.url)))) {
      throw new Error("The temple catalogue returned invalid data.");
    }
    return page as TemplePage;
  });
};
export const getTempleFacets = (filters: { state?: string; district?: string }, signal?: AbortSignal): Promise<TempleFacets> => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => { if (value?.trim()) params.set(key, value.trim()); });
  return request<TempleFacets>(`/temples/facets?${params}`, { signal }).then(result => {
    if (!result || !Array.isArray(result.districts) || !result.districts.every(x => typeof x === "string") || !Array.isArray(result.temples)) {
      throw new Error("The temple catalogue returned invalid filter data.");
    }
    return result;
  });
};
export const getTemple = async (id: string, signal?: AbortSignal): Promise<Temple> => {
  const temple = await request<Temple>(`/temples/${encodeURIComponent(id)}`, { signal });
  if (!temple || typeof temple.id !== "string" || !Array.isArray(temple.names)
    || !temple.names.length || !temple.names.every(name => typeof name === "string")
    || typeof temple.description !== "string" || !Array.isArray(temple.sources)
    || !temple.sources.every(source => source && typeof source.title === "string" && typeof source.url === "string" && /^https?:\/\//i.test(source.url))) {
    throw new Error("The temple details returned invalid data.");
  }
  return temple;
};
