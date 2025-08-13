// **1.2 Servicio de Autenticación** (según instrucciones)

import type { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User, 
  AuthTokens 
} from '@/types/auth'

// URL base del backend (confirmada en pruebas)
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://172.245.214.69'

// Clase de errores personalizada para autenticación
export class AuthError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message)
    this.name = 'AuthError'
  }
}

// **Servicio de Autenticación** - Sin dependencias externas
export class AuthService {
  
  // **Login** - Endpoint probado y funcional
  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new AuthError(
          errorData.message || 'Credenciales incorrectas',
          response.status
        )
      }

      const data: AuthResponse = await response.json()
      return data
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Error de conexión con el servidor')
    }
  }

  // **Registro** - Endpoint por implementar
  static async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new AuthError(
          errorData.message || 'Error al crear la cuenta',
          response.status
        )
      }

      const responseData: AuthResponse = await response.json()
      return responseData
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Error de conexión con el servidor')
    }
  }

  // **Refresh Token** - Renovar token de acceso
  static async refreshToken(refreshToken: string): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      })

      if (!response.ok) {
        throw new AuthError('Token de actualización inválido', response.status)
      }

      const data = await response.json()
      return data.access
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Error al renovar token')
    }
  }

  // **Obtener Usuario Actual** - Con token de acceso
  static async getCurrentUser(accessToken: string): Promise<User> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/user/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new AuthError('Token inválido', response.status)
      }

      const user: User = await response.json()
      return user
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Error al obtener datos del usuario')
    }
  }

  // **Logout** - Invalidar token en el servidor
  static async logout(accessToken: string): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      })
      // No importa si falla, limpiamos local de todas formas
    } catch (error) {
      // Error silencioso - el logout local siempre debe funcionar
      console.warn('Error al hacer logout en el servidor:', error)
    }
  }

  // **Gestión de Tokens en localStorage** - Persistencia local

  // Guardar tokens
  static storeTokens(tokens: AuthTokens): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
    }
  }

  // Obtener token de acceso
  static getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token')
    }
    return null
  }

  // Obtener token de refresh
  static getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token')
    }
    return null
  }

  // Guardar datos del usuario
  static storeUser(user: User): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user_data', JSON.stringify(user))
    }
  }

  // Obtener datos del usuario
  static getStoredUser(): User | null {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user_data')
      return userData ? JSON.parse(userData) : null
    }
    return null
  }

  // Limpiar toda la sesión
  static clearSession(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')
    }
  }

  // Verificar si hay una sesión válida
  static hasValidSession(): boolean {
    const accessToken = this.getAccessToken()
    const user = this.getStoredUser()
    return !!(accessToken && user)
  }
}
