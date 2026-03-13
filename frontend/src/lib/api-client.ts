import type { Conversation, Document, Message, Workspace } from "@/types/api";

const API_BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Workspaces
export const workspacesApi = {
  list: () => request<Workspace[]>("/workspaces"),
  get: (id: string) => request<Workspace>(`/workspaces/${id}`),
  create: (data: { name: string; description?: string }) =>
    request<Workspace>("/workspaces", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: string, data: { name?: string; description?: string }) =>
    request<Workspace>(`/workspaces/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  delete: (id: string) =>
    request<void>(`/workspaces/${id}`, { method: "DELETE" }),
};

// Documents
export const documentsApi = {
  list: (workspaceId: string) =>
    request<Document[]>(`/workspaces/${workspaceId}/documents`),
  get: (id: string) => request<Document>(`/documents/${id}`),
  upload: async (workspaceId: string, file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(
      `${API_BASE}/workspaces/${workspaceId}/documents`,
      { method: "POST", body: formData }
    );
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Upload failed");
    }
    return res.json();
  },
  delete: (id: string) =>
    request<void>(`/documents/${id}`, { method: "DELETE" }),
  reindex: (id: string) =>
    request<{ message: string }>(`/documents/${id}/reindex`, {
      method: "POST",
    }),
  status: (id: string) =>
    request<{ id: string; status: string; chunk_count: number }>(
      `/documents/${id}/status`
    ),
};

// Conversations
export const conversationsApi = {
  list: (workspaceId: string) =>
    request<Conversation[]>(`/workspaces/${workspaceId}/conversations`),
  create: (workspaceId: string, title?: string) =>
    request<Conversation>(`/workspaces/${workspaceId}/conversations`, {
      method: "POST",
      body: JSON.stringify({ title }),
    }),
  messages: (id: string) => request<Message[]>(`/conversations/${id}/messages`),
  delete: (id: string) =>
    request<void>(`/conversations/${id}`, { method: "DELETE" }),
};

// Search
export const searchApi = {
  search: (
    workspaceId: string,
    query: string,
    topK = 5,
    threshold = 0.0
  ) =>
    request<{ results: import("@/types/api").SearchResult[] }>(
      `/workspaces/${workspaceId}/search`,
      {
        method: "POST",
        body: JSON.stringify({ query, top_k: topK, threshold }),
      }
    ),
};
