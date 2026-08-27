import type {
  AskResponse,
  DocumentDetail,
  DocumentSummary,
  SearchResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      "X-Correlation-ID": crypto.randomUUID(),
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "The request failed.");
  }

  return response.json() as Promise<T>;
}

export const api = {
  getDocuments: () => apiRequest<DocumentSummary[]>("/api/v1/documents"),

  getDocument: (documentId: string) =>
    apiRequest<DocumentDetail>(`/api/v1/documents/${documentId}`),

  search: (query: string) =>
    apiRequest<SearchResponse>(`/api/v1/search?query=${encodeURIComponent(query)}`),

  ask: (question: string) =>
    apiRequest<AskResponse>("/api/v1/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
};