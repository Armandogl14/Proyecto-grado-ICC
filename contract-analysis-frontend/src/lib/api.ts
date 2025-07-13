import axios from 'axios'
import type { 
  Contract, 
  ContractType, 
  Clause, 
  CreateContractData, 
  ContractFilters, 
  DashboardStats,
  ApiResponse 
} from '@/types/contracts'
import { getStoredToken } from './auth-simple'
 
// Configuración base de axios
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Incluir cookies de sesión automáticamente
})

// Interceptor para manejar autenticación
api.interceptors.request.use(
  async (config) => {
    const token = getStoredToken()
    if (token === 'dev-session-token') {
      // Usar Basic Auth para desarrollo
      const basicAuth = btoa('admin:admin123')
      config.headers.Authorization = `Basic ${basicAuth}`
    } else if (token && token !== 'session-auth') {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Servicios de API
export const contractsApi = {
  // Obtener todos los contratos
  getContracts: async (filters?: ContractFilters): Promise<ApiResponse<Contract>> => {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.contract_type) params.append('contract_type', filters.contract_type.toString())
    if (filters?.search) params.append('search', filters.search)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.page_size) params.append('page_size', filters.page_size.toString())
    
    const response = await api.get(`/api/contracts/?${params}`)
    return response.data
  },

  // Obtener un contrato específico
  getContract: async (id: string): Promise<Contract> => {
    const response = await api.get(`/api/contracts/${id}/`)
    return response.data
  },

  // Crear nuevo contrato
  createContract: async (data: CreateContractData): Promise<Contract> => {
    const response = await api.post('/api/contracts/', data)
    return response.data
  },

  // Analizar contrato
  analyzeContract: async (id: string, forceReanalysis = false): Promise<{ message: string, task_id: string }> => {
    const response = await api.post(`/api/contracts/${id}/analyze/`, {
      force_reanalysis: forceReanalysis
    })
    return response.data
  },

  // Obtener estadísticas del dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/contracts/dashboard_stats/')
    return response.data
  },

  // Exportar reporte
  exportReport: async (id: string): Promise<Blob> => {
    const response = await api.get(`/api/contracts/${id}/export_report/`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Eliminar un contrato
  deleteContract: async (id: string): Promise<void> => {
    await api.delete(`/api/contracts/${id}/`)
  }
}

export const contractTypesApi = {
  // Obtener tipos de contrato
  getContractTypes: async (): Promise<ApiResponse<ContractType>> => {
    try {
      const response = await api.get('/api/contract-types/')
      return response.data
    } catch (error: any) {
      console.error('Error fetching contract types:', error)
      // Si es error de autenticación, intentar sin token
      if (error.response?.status === 401) {
        try {
          const responseNoAuth = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/contract-types/`)
          return responseNoAuth.data
        } catch (noAuthError) {
          console.error('Error even without auth:', noAuthError)
          throw error
        }
      }
      throw error
    }
  }
}

export const clausesApi = {
  // Obtener cláusulas de un contrato
  getClausesByContract: async (contractId: string): Promise<ApiResponse<Clause>> => {
    const response = await api.get(`/api/clauses/?contract=${contractId}`)
    return response.data
  },

  // Obtener patrones de cláusulas abusivas
  getAbusivePatterns: async (): Promise<any> => {
    const response = await api.get('/api/clauses/abusive_patterns/')
    return response.data
  }
}

// Helper para configurar el token de autenticación
export const setAuthToken = (token: string) => {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// Helper para remover el token
export const removeAuthToken = () => {
  delete api.defaults.headers.common['Authorization']
}

export default api 