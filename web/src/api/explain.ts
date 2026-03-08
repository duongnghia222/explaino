import { apiFetch } from "./client"
import type { ExplainRequest, ExplainResponse, ExplainNode } from "@/types/explain"

export function postExplain(req: ExplainRequest) {
  return apiFetch<ExplainResponse>("/api/explain", {
    method: "POST",
    body: JSON.stringify(req),
  })
}

export function getExplanation(id: string) {
  return apiFetch<ExplainResponse>(`/api/explain/${id}`)
}

export function getExplanationTree(id: string) {
  return apiFetch<ExplainNode>(`/api/explain/${id}/tree`)
}

export function getExplanationChildren(id: string) {
  return apiFetch<ExplainResponse[]>(`/api/explain/${id}/children`)
}
