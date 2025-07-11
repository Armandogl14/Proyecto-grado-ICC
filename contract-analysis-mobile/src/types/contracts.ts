export interface ContractType {
  id: number
  name: string
  code: string
  description: string
}

export interface MLAnalysis {
  is_abusive: boolean
  abuse_probability: number
}

export interface GPTAnalysis {
  is_valid_clause: boolean
  is_abusive: boolean
  explanation: string
  suggested_fix?: string
}

export interface Entity {
  text: string
  label: string
}

export interface Clause {
  id: string
  text: string
  clause_number: number
  ml_analysis: MLAnalysis
  gpt_analysis: GPTAnalysis
  entities: Entity[]
  risk_score: number
}

export interface Contract {
  id: string
  title: string
  original_text: string
  contract_type: ContractType
  status: 'pending' | 'analyzing' | 'completed' | 'error'
  created_at: string
  updated_at: string
  analyzed_at?: string
  total_clauses: number
  valid_clauses: number
  abusive_clauses_count: number
  risk_score: number
  processing_time: number
  executive_summary: string
  recommendations: string
}

export interface ContractFilters {
  status?: string
  contract_type?: number
  search?: string
  page?: number
  page_size?: number
}

export interface CreateContractData {
  title: string
  original_text: string
  contract_type: number
  file?: File
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface DashboardStats {
  total_contracts: number
  pending_analysis: number
  analyzing: number
  completed: number
  low_risk: number
  medium_risk: number
  high_risk: number
  recent_contracts: Contract[]
} 