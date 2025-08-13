// Tipos básicos de autenticación según las instrucciones del documento

// Usuario - Estructura principal del usuario
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  date_joined: string
  last_login: string | null
  profile?: UserProfile
}

// Perfil de Usuario - Información adicional del usuario
export interface UserProfile {
  phone: string
  organization: string
  bio: string
  avatar?: string
  is_verified: boolean
  created_at: string
  updated_at: string
}

// Credenciales para login
export interface LoginCredentials {
  username: string
  password: string
}

// Datos para registro de usuario
export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
}

// Tokens de autenticación JWT
export interface AuthTokens {
  access: string
  refresh: string
}

// Respuesta del servidor para autenticación
export interface AuthResponse {
  message: string
  user: User
  tokens: AuthTokens
}

// Estados de autenticación para Context
export interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<string | null>
  updateUser: (user: User) => void
}
