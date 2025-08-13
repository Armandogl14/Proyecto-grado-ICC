'use client'

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import type { 
  AuthState, 
  AuthContextType, 
  LoginCredentials, 
  RegisterData, 
  User, 
  AuthTokens 
} from '@/types/auth'
import { AuthService, AuthError } from '@/services/auth'

// **1.3 Auth Context & State Management** (según instrucciones)

// Actions para el reducer
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; tokens: AuthTokens } }
  | { type: 'AUTH_FAILURE' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'REFRESH_TOKEN'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }

// Estado inicial
const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
}

// Reducer para manejo de estados (según instrucciones)
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
      }
    
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isAuthenticated: true,
        isLoading: false,
      }
    
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
      }
    
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      }
    
    case 'REFRESH_TOKEN':
      return {
        ...state,
        tokens: state.tokens ? {
          ...state.tokens,
          access: action.payload
        } : null,
      }
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
      }
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }
    
    default:
      return state
  }
}

// Crear el contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Hooks personalizados (useAuth) - según instrucciones
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }
  return context
}

// Provider del contexto
interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Persistencia en localStorage y validación de sesión al inicializar
  useEffect(() => {
    const initializeAuth = async () => {
      dispatch({ type: 'SET_LOADING', payload: true })

      try {
        // Verificar si hay sesión guardada
        const storedUser = AuthService.getStoredUser()
        const accessToken = AuthService.getAccessToken()
        const refreshToken = AuthService.getRefreshToken()

        if (storedUser && accessToken && refreshToken) {
          // Intentar validar el token actual
          try {
            const currentUser = await AuthService.getCurrentUser(accessToken)
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: {
                user: currentUser,
                tokens: { access: accessToken, refresh: refreshToken }
              }
            })
          } catch (error) {
            // Token inválido, intentar refresh
            try {
              const newAccessToken = await AuthService.refreshToken(refreshToken)
              const currentUser = await AuthService.getCurrentUser(newAccessToken)
              
              const newTokens = { access: newAccessToken, refresh: refreshToken }
              AuthService.storeTokens(newTokens)
              AuthService.storeUser(currentUser)

              dispatch({
                type: 'AUTH_SUCCESS',
                payload: {
                  user: currentUser,
                  tokens: newTokens
                }
              })
            } catch (refreshError) {
              // Refresh también falló, limpiar sesión
              AuthService.clearSession()
              dispatch({ type: 'AUTH_FAILURE' })
            }
          }
        } else {
          // No hay sesión guardada
          dispatch({ type: 'AUTH_FAILURE' })
        }
      } catch (error) {
        console.error('Error inicializando auth:', error)
        AuthService.clearSession()
        dispatch({ type: 'AUTH_FAILURE' })
      }
    }

    initializeAuth()
  }, [])

  // **Login** - Función principal de autenticación
  const login = async (credentials: LoginCredentials): Promise<void> => {
    dispatch({ type: 'AUTH_START' })

    try {
      const response = await AuthService.login(credentials)
      
      // Guardar en localStorage
      AuthService.storeTokens(response.tokens)
      AuthService.storeUser(response.user)

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: response.user,
          tokens: response.tokens
        }
      })
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' })
      throw error // Re-lanzar para que los componentes puedan manejarlo
    }
  }

  // **Registro** - Crear nueva cuenta
  const register = async (data: RegisterData): Promise<void> => {
    dispatch({ type: 'AUTH_START' })

    try {
      const response = await AuthService.register(data)
      
      // Guardar en localStorage
      AuthService.storeTokens(response.tokens)
      AuthService.storeUser(response.user)

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: response.user,
          tokens: response.tokens
        }
      })
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' })
      throw error
    }
  }

  // **Logout** - Cerrar sesión
  const logout = async (): Promise<void> => {
    const accessToken = AuthService.getAccessToken()
    
    if (accessToken) {
      await AuthService.logout(accessToken)
    }
    
    AuthService.clearSession()
    dispatch({ type: 'LOGOUT' })
  }

  // **Refresh Token** - Renovar token de acceso
  const refreshToken = async (): Promise<string | null> => {
    const refreshTokenValue = AuthService.getRefreshToken()
    
    if (!refreshTokenValue) {
      return null
    }

    try {
      const newAccessToken = await AuthService.refreshToken(refreshTokenValue)
      
      // Actualizar token en localStorage
      const currentTokens = state.tokens
      if (currentTokens) {
        const newTokens = { ...currentTokens, access: newAccessToken }
        AuthService.storeTokens(newTokens)
      }
      
      dispatch({ type: 'REFRESH_TOKEN', payload: newAccessToken })
      return newAccessToken
    } catch (error) {
      // Refresh falló, cerrar sesión
      await logout()
      return null
    }
  }

  // **Actualizar Usuario** - Modificar datos del usuario
  const updateUser = (user: User): void => {
    AuthService.storeUser(user)
    dispatch({ type: 'UPDATE_USER', payload: user })
  }

  // Valor del contexto
  const contextValue: AuthContextType = {
    // Estado
    user: state.user,
    tokens: state.tokens,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    
    // Acciones
    login,
    register,
    logout,
    refreshToken,
    updateUser,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}
