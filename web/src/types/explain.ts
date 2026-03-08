export interface ExplainRequest {
  text: string
  context?: string
  parent_id?: string
}

export interface ExplainResponse {
  id: string
  text: string
  explanation: string
  key_terms: string[]
  parent_id: string | null
  created_at: string
}

export interface ExplainNode {
  id: string
  text: string
  explanation: string
  key_terms: string[]
  parent_id: string | null
  children: ExplainNode[]
  depth: number
}
