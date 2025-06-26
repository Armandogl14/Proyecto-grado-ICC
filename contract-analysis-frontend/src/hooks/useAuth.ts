'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  login as apiLogin, 
  getStoredUserData, 
  getStoredToken, 
  storeToken, 
  storeRefreshToken, 
  storeUserData, 
  clearTokens,
  isAuthenticated as checkIsAuthenticated,
  type LoginCredentials, 
  type User 
} from '@/lib/auth-simple'
import { toast } from 'sonner'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  // Verificar autenticación al cargar
  useEffect(() => {
    const token = getStoredToken()
    const userData = getStoredUserData()
    
    if (token && userData) {
      setUser(userData)
      setIsAuthenticated(true)
    }
    setIsLoading(false)
  }, [])

  // Mutation para login
  const loginMutation = useMutation({
    mutationFn: apiLogin,
    onSuccess: (data) => {
      storeToken(data.access)
      storeRefreshToken(data.refresh)
      storeUserData(data.user)
      setUser(data.user)
      setIsAuthenticated(true)
      toast.success(`¡Bienvenido, ${data.user.username}!`)
      
      // Limpiar y refrescar queries
      queryClient.clear()
    },
    onError: (error: Error) => {
      toast.error(error.message)
    }
  })

  // Función de logout
  const logout = () => {
    clearTokens()
    setUser(null)
    setIsAuthenticated(false)
    queryClient.clear()
    toast.success('Sesión cerrada correctamente')
  }

  // Auto-login con credenciales por defecto si no está autenticado
  const autoLogin = () => {
    if (!isAuthenticated) {
      loginMutation.mutate({
        username: 'admin',
        password: 'admin123'
      })
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutate,
    loginLoading: loginMutation.isPending,
    loginError: loginMutation.error,
    logout,
    autoLogin
  }
} 