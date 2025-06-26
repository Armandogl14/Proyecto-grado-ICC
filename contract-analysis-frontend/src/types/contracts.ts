export interface ContractType {
  id: number
  name: string
  code: string
  description: string
  created_at: string
}

export interface Entity {
  text: string
  label: string
  start_char: number
  end_char: number
  confidence: number
}

export interface Clause {
  id: string
  contract: string
  text: string
  clause_number: string
  clause_type: string
  is_abusive: boolean
  confidence_score: number
  start_position?: number
  end_position?: number
  created_at: string
  entities?: Entity[]
}

export interface Contract {
  id: string
  title: string
  contract_type: ContractType
  original_text: string
  file_upload?: string
  uploaded_by: string
  status: 'pending' | 'analyzing' | 'completed' | 'error'
  created_at: string
  updated_at: string
  analyzed_at?: string
  total_clauses: number
  abusive_clauses_count: number
  risk_score?: number
}

export interface AnalysisResult {
  contract: Contract
  clauses: Clause[]
  executive_summary?: string
  recommendations?: string
  processing_time: number
  model_version: string
}

export interface CreateContractData {
  title: string
  original_text: string
  contract_type: number
}

export interface ContractFilters {
  status?: string
  contract_type?: string
  search?: string
  page?: number
  page_size?: number
}

export interface DashboardStats {
  total_contracts: number
  pending_analysis: number
  analyzing: number
  completed: number
  high_risk: number
  medium_risk: number
  low_risk: number
  recent_contracts: Contract[]
}

export interface ApiResponse<T> {
  count: number
  next?: string
  previous?: string
  results: T[]
}

export interface AnalysisProgress {
  status: 'pending' | 'analyzing' | 'completed' | 'error'
  progress: number
  message?: string
} 