export interface ExplainRequest {
  text: string
  parent_id?: string
  is_follow_up?: boolean
}

export interface ExplainResponse {
  id: string
  text: string
  explanation: string
  key_terms: string[]
  parent_id: string | null
  is_follow_up: boolean
  created_at: string
}

export interface ExplainNode {
  id: string
  text: string
  explanation: string
  key_terms: string[]
  parent_id: string | null
  is_follow_up: boolean
  children: ExplainNode[]
  depth: number
}
