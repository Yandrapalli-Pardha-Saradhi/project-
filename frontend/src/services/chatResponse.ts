import type { ChatResponse } from "../types/chat";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeAnswer(answer: string): string {
  const trimmed = answer.trim();
  const fenced = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  const candidate = fenced ? fenced[1].trim() : trimmed;
  const looksLikeStructuredPayload = candidate.startsWith("{") || Boolean(fenced);
  if (!looksLikeStructuredPayload) return answer;

  let parsed: unknown;
  try {
    parsed = JSON.parse(candidate) as unknown;
  } catch {
    throw new Error("The assistant returned malformed structured answer data.");
  }
  if (!isRecord(parsed) || typeof parsed.answer !== "string" || !parsed.answer.trim()) {
    throw new Error("The assistant returned an unexpected structured answer.");
  }

  // Citation IDs embedded in model output are not trusted or rendered as links.
  // The API's validated citation records remain the sole source of clickable citations.
  return parsed.answer.trim();
}

export function normalizeChatResponse(response: unknown): ChatResponse {
  if (!isRecord(response)
    || typeof response.answer !== "string"
    || !Array.isArray(response.citations)
    || !response.citations.every(citation => isRecord(citation)
      && typeof citation.source_id === "string"
      && typeof citation.source_title === "string"
      && typeof citation.source_url === "string"
      && /^https?:\/\//i.test(citation.source_url))
    || typeof response.insufficient_evidence !== "boolean"
    || typeof response.generation_disabled !== "boolean") {
    throw new Error("The assistant returned an incomplete response.");
  }

  return { ...response, answer: normalizeAnswer(response.answer) } as ChatResponse;
}
