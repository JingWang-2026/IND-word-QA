import type { DocumentRecord, Project, ProjectDetail, QAIssue } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listProjects: () => request<Project[]>("/api/projects"),
  createProject: (payload: { name: string; description?: string }) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify(payload) }),
  getProject: (projectId: string) => request<ProjectDetail>(`/api/projects/${projectId}`),
  listDocuments: (projectId: string) => request<DocumentRecord[]>(`/api/projects/${projectId}/documents`),
  uploadDocument: async (projectId: string, file: File) => {
    const data = new FormData();
    data.append("file", file);
    const response = await fetch(`${API_BASE}/api/projects/${projectId}/documents`, { method: "POST", body: data });
    if (!response.ok) throw new Error(await response.text());
    return response.json() as Promise<DocumentRecord>;
  },
  parseDocument: (documentId: string) => request(`/api/documents/${documentId}/parse`, { method: "POST" }),
  runDocumentQa: (documentId: string) => request(`/api/documents/${documentId}/qa/run`, { method: "POST" }),
  runProjectQa: (projectId: string) => request(`/api/projects/${projectId}/qa/run`, { method: "POST" }),
  listIssues: (projectId: string, filters: Record<string, string> = {}) => {
    const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
    const suffix = params.toString() ? `?${params}` : "";
    return request<QAIssue[]>(`/api/projects/${projectId}/issues${suffix}`);
  },
  getIssue: (issueId: string) => request<QAIssue>(`/api/issues/${issueId}`),
  updateIssue: (issueId: string, payload: { status?: string; reviewer_comment?: string }) =>
    request<QAIssue>(`/api/issues/${issueId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  exportIssuesUrl: (projectId: string, filters: Record<string, string> = {}) => {
    const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
    const suffix = params.toString() ? `?${params}` : "";
    return `${API_BASE}/api/projects/${projectId}/export/issues.xlsx${suffix}`;
  },
};
