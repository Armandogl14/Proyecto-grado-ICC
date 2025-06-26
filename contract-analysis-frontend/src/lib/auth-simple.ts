import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export interface LoginCredentials {
  username: string
  password: string
}

export interface User {
  id: number
  username: string
  email: string
  is_staff: boolean
  is_superuser: boolean
}

export interface AuthResponse {
  access: string
  refresh: string
  user: User
}

// Función simple de login para desarrollo
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  // Validar credenciales conocidas
  if (credentials.username === 'admin' && credentials.password === 'admin123') {
    // Simular delay de red
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    return {
      access: 'dev-session-token',
      refresh: 'dev-refresh-token',
      user: {
        id: 1,
        username: credentials.username,
        email: 'admin@example.com',
        is_staff: true,
        is_superuser: true
      }
    }
  } else {
    throw new Error('Credenciales incorrectas. Use admin/admin123')
  }
}

// Configurar Basic Auth para todas las peticiones de desarrollo
export const setupDevAuth = () => {
  const token = btoa('admin:admin123') // Base64 encode
  return `Basic ${token}`
}

// Función para obtener el token almacenado
export const getStoredToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token')
  }
  return null
}

// Función para almacenar el token
export const storeToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token)
  }
}

// Función para almacenar el refresh token
export const storeRefreshToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('refresh_token', token)
  }
}

// Función para limpiar tokens
export const clearTokens = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
  }
}

// Función para almacenar datos del usuario
export const storeUserData = (user: User) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user_data', JSON.stringify(user))
  }
}

// Función para obtener datos del usuario
export const getStoredUserData = (): User | null => {
  if (typeof window !== 'undefined') {
    const userData = localStorage.getItem('user_data')
    return userData ? JSON.parse(userData) : null
  }
  return null
}

// Función para verificar si el usuario está autenticado
export const isAuthenticated = (): boolean => {
  return !!getStoredToken()
} 