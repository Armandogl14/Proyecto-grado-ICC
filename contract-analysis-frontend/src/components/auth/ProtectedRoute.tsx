'use client'

import { ReactNode } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { LoginForm } from '@/components/auth/LoginForm'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth()

  // Si está cargando, mostrar spinner
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    )
  }

  // Si no está autenticado, mostrar formularios de autenticación
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AuthenticationFlow />
      </div>
    )
  }

  // Usuario autenticado, mostrar contenido protegido
  return <>{children}</>
}

// Componente interno para manejar el flujo de autenticación
function AuthenticationFlow() {
  // Por ahora solo mostramos el login, más adelante implementaremos navegación
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            LegalAI
          </h1>
          <p className="text-gray-600">
            Análisis inteligente de contratos
          </p>
        </div>
        
        <LoginForm 
          onSuccess={() => {
            // El Context manejará la navegación automáticamente
            console.log('Login exitoso')
          }}
          showRegisterLink={true}
        />
      </div>
    </div>
  )
}
