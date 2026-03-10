export type InputType = "text" | "file" | "url"

export interface ExplainRequest {
  text: string
  url?: string
  input_type?: InputType
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
  input_type: string
  source_url: string | null
  created_at: string
}

export interface ExplainNode {
  id: string
  text: string
  explanation: string
  key_terms: string[]
  parent_id: string | null
  is_follow_up: boolean
  input_type: string
  source_url: string | null
  children: ExplainNode[]
  depth: number
}
