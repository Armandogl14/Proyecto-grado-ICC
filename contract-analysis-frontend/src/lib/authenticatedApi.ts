import type { 
  Contract, 
  ContractType, 
  Clause, 
  CreateContractData, 
  ContractFilters, 
  DashboardStats,
  ApiResponse 
} from '@/types/contracts'
import { AuthService } from '@/services/auth'

// Configuración base para las llamadas API
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://172.245.214.69'

// Función helper para hacer llamadas autenticadas
async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const accessToken = AuthService.getAccessToken()
  const refreshToken = AuthService.getRefreshToken()
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  // Añadir token de autorización si existe
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  } else {
    // Fallback a Basic Auth para desarrollo
    const basicAuth = btoa('admin:admin123')
    headers['Authorization'] = `Basic ${basicAuth}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  // Manejar errores de autenticación
  if (response.status === 401) {
    // Intentar refresh del token
    if (refreshToken) {
      try {
        const newAccessToken = await AuthService.refreshToken(refreshToken)
        // Actualizar solo el access token
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', newAccessToken)
        }
        
        // Reintentar la llamada original con el nuevo token
        headers['Authorization'] = `Bearer ${newAccessToken}`
        return fetch(url, { ...options, headers })
      } catch (error) {
        // Si el refresh falla, limpiar tokens
        AuthService.clearSession()
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.')
      }
    } else {
      // No hay refresh token, limpiar sesión
      AuthService.clearSession()
      throw new Error('No autorizado. Por favor, inicia sesión.')
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.message || `Error HTTP: ${response.status}`)
  }

  return response
}

// API para contratos
export const contractsApi = {
  // Obtener lista de contratos
  async getContracts(filters?: ContractFilters): Promise<ApiResponse<Contract>> {
    const params = new URLSearchParams()
    
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.page_size) params.append('page_size', filters.page_size.toString())
    if (filters?.status) params.append('status', filters.status)
    if (filters?.contract_type) params.append('contract_type', filters.contract_type.toString())
    if (filters?.search) params.append('search', filters.search)

    const url = `${API_BASE_URL}/api/contracts/?${params.toString()}`
    const response = await authenticatedFetch(url)
    return response.json()
  },

  // Obtener un contrato específico
  async getContract(id: string): Promise<Contract> {
    const url = `${API_BASE_URL}/api/contracts/${id}/`
    const response = await authenticatedFetch(url)
    return response.json()
  },

  // Crear nuevo contrato
  async createContract(data: CreateContractData): Promise<Contract> {
    const url = `${API_BASE_URL}/api/contracts/`
    const response = await authenticatedFetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return response.json()
  },

  // Actualizar contrato
  async updateContract(id: string, data: Partial<CreateContractData>): Promise<Contract> {
    const url = `${API_BASE_URL}/api/contracts/${id}/`
    const response = await authenticatedFetch(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return response.json()
  },

  // Eliminar contrato
  async deleteContract(id: string): Promise<void> {
    const url = `${API_BASE_URL}/api/contracts/${id}/`
    await authenticatedFetch(url, {
      method: 'DELETE',
    })
  },

  // Analizar contrato
  async analyzeContract(id: string): Promise<Contract> {
    const url = `${API_BASE_URL}/api/contracts/${id}/analyze/`
    const response = await authenticatedFetch(url, {
      method: 'POST',
    })
    return response.json()
  },

  // Exportar reporte
  async exportReport(id: string, format: 'pdf' | 'docx' = 'pdf'): Promise<Blob> {
    const url = `${API_BASE_URL}/api/contracts/${id}/export_report/?format=${format}`
    const response = await authenticatedFetch(url)
    return response.blob()
  },

  // Obtener estadísticas del dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const url = `${API_BASE_URL}/api/contracts/dashboard_stats/`
    const response = await authenticatedFetch(url)
    return response.json()
  },
}

// API para tipos de contratos
export const contractTypesApi = {
  async getContractTypes(): Promise<ContractType[]> {
    const url = `${API_BASE_URL}/api/contract-types/`
    const response = await authenticatedFetch(url)
    const data = await response.json()
    
    // Si el backend devuelve un objeto con results, extraer el array
    if (data && typeof data === 'object' && Array.isArray(data.results)) {
      return data.results
    }
    
    // Si ya es un array, devolverlo directamente
    if (Array.isArray(data)) {
      return data
    }
    
    // Fallback: devolver array vacío
    console.warn('Contract types response is not in expected format:', data)
    return []
  },
}

// API para cláusulas
export const clausesApi = {
  async getClausesByContract(contractId: string): Promise<Clause[]> {
    const url = `${API_BASE_URL}/api/contracts/${contractId}/clauses/`
    const response = await authenticatedFetch(url)
    return response.json()
  },
}
