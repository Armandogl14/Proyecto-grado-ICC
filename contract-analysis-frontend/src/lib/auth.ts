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

// Función para hacer login usando múltiples métodos
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  // Método 1: Intentar con JWT si existe
  try {
    const jwtResponse = await axios.post(`${API_BASE_URL}/api/token/`, credentials)
    if (jwtResponse.data.access) {
      return {
        access: jwtResponse.data.access,
        refresh: jwtResponse.data.refresh,
        user: {
          id: 1,
          username: credentials.username,
          email: '',
          is_staff: true,
          is_superuser: true
        }
      }
    }
  } catch (jwtError) {
    console.log('JWT login no disponible, intentando Django session...')
  }
  
  // Método 2: Django session auth
  try {
    // Crear una instancia de axios específica para login con configuración especial
    const loginAxios = axios.create({
      baseURL: API_BASE_URL,
      withCredentials: true,
      headers: {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    })

    console.log('Intentando obtener CSRF token...')
    
    // Primero obtener el CSRF token
    const csrfResponse = await loginAxios.get('/admin/login/')
    
    console.log('Response status:', csrfResponse.status)
    console.log('Response headers:', csrfResponse.headers)
    
    // Extraer CSRF token del HTML con múltiples patrones
    let csrfToken = ''
    const patterns = [
      /name=['"]csrfmiddlewaretoken['"] value=['"]([^'"]+)['"]/,
      /csrfmiddlewaretoken['"] value=['"]([^'"]+)['"]/,
      /'csrfmiddlewaretoken': '([^']+)'/,
      /name="csrfmiddlewaretoken" value="([^"]+)"/
    ]
    
    for (const pattern of patterns) {
      const match = csrfResponse.data.match(pattern)
      if (match && match[1]) {
        csrfToken = match[1]
        break
      }
    }
    
    console.log('CSRF Token found:', csrfToken ? 'Yes' : 'No')
    
    if (!csrfToken) {
      throw new Error('No se pudo obtener el token CSRF')
    }
    
    // Preparar datos del formulario como URLSearchParams
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    formData.append('csrfmiddlewaretoken', csrfToken)
    formData.append('next', '/admin/')
    
    console.log('Intentando login con credenciales:', credentials.username)
    
    // Hacer login con autenticación de Django
    const loginResponse = await loginAxios.post('/admin/login/', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
        'Referer': `${API_BASE_URL}/admin/login/`,
        'Origin': API_BASE_URL
      },
      maxRedirects: 0, // No seguir redirects automáticamente
      validateStatus: (status) => status < 400 || status === 302 // Aceptar redirects como éxito
    })
    
    console.log('Login response status:', loginResponse.status)
    console.log('Login response headers:', loginResponse.headers)
    
    // Un redirect (302) indica login exitoso
    if (loginResponse.status === 302 || loginResponse.status === 200) {
      return {
        access: 'session-auth',
        refresh: 'session-auth',
        user: {
          id: 1,
          username: credentials.username,
          email: '',
          is_staff: true,
          is_superuser: true
        }
      }
    }
    
    throw new Error('Login no exitoso')
    
  } catch (error: any) {
    console.error('Login error:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)
    
    if (error.response?.status === 403) {
      throw new Error('Error CSRF o permisos. Verifique configuración del backend.')
    } else if (error.response?.status === 302) {
      // Un 302 es realmente un éxito para el login
      return {
        access: 'session-auth',
        refresh: 'session-auth',
        user: {
          id: 1,
          username: credentials.username,
          email: '',
          is_staff: true,
          is_superuser: true
        }
      }
    }
    
    throw new Error('Credenciales incorrectas o error del servidor')
  }
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