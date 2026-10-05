import type {
  CampaignDraftData,
  CampaignDraftInput,
  OperationPreview,
  OperationResult,
  Platform,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function generateDraft(input: CampaignDraftInput): Promise<CampaignDraftData> {
  return request<CampaignDraftData>("/campaign-drafts/generate", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function previewOperation(
  platform: Platform,
  budgetCeiling: string,
  draft: CampaignDraftInput,
): Promise<OperationPreview> {
  return request<OperationPreview>("/operations/preview", {
    method: "POST",
    body: JSON.stringify({ platform, budget_ceiling: budgetCeiling, draft }),
  });
}

export function approveOperation(operationId: string, token: string): Promise<OperationResult> {
  return request<OperationResult>(`/operations/${operationId}/approve`, {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}
