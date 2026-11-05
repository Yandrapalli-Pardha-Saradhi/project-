export interface Citation {
  source_id: string;
  source_title: string;
  source_url: string;
  publisher: string | null;
  excerpt: string;
}

export interface ChatRequest {
  question: string;
  language: string;
  temple_id?: string | null;
  history?: ConversationMessage[];
}

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  context_temple_id?: string | null;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  language: string;
  insufficient_evidence: boolean;
  generation_disabled: boolean;
  context_temple_id?: string | null;
}

export interface HealthResponse {
  status: string;
  app: string;
  generation_enabled: boolean;
  llm_configured: boolean;
  collection: string;
  chroma_persist_dir: string;
  indexed_chunks: number;
}

export const SUPPORTED_LANGUAGES: { code: string; label: string }[] = [
  { code: "en", label: "English" },
  { code: "te", label: "Telugu" },
  { code: "ta", label: "Tamil" },
  { code: "hi", label: "Hindi" },
];
