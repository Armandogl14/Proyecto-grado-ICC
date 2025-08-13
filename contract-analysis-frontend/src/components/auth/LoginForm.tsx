'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { Loader2, LogIn, User } from "lucide-react"

interface LoginFormProps {
  onSuccess?: () => void
  showRegisterLink?: boolean
}

export function LoginForm({ onSuccess, showRegisterLink }: LoginFormProps) {
  const [credentials, setCredentials] = useState({
    username: 'admin',
    password: 'admin123'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { login, isLoading } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)
    
    try {
      await login(credentials)
      onSuccess?.()
    } catch (err: any) {
      setError(err.message || 'Error desconocido')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleAutoLogin = async () => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      await login({
        username: 'admin',
        password: 'admin123'
      })
      onSuccess?.()
    } catch (err: any) {
      setError(err.message || 'Error desconocido')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="flex items-center justify-center gap-2 text-2xl">
          <User className="w-6 h-6" />
          Iniciar Sesión
        </CardTitle>
        <p className="text-gray-600">
          Accede al sistema de análisis de contratos
        </p>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Usuario
            </label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nombre de usuario"
              disabled={isSubmitting || isLoading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Contraseña
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Contraseña"
              disabled={isSubmitting || isLoading}
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}
          
          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting || isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Iniciando sesión...
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4 mr-2" />
                Iniciar Sesión
              </>
            )}
          </Button>
          
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={handleAutoLogin}
            disabled={isSubmitting || isLoading}
          >
            <User className="w-4 h-4 mr-2" />
            Login Rápido (Admin)
          </Button>

          {/* Link a registro si está habilitado */}
          {showRegisterLink && (
            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                ¿No tienes una cuenta?{' '}
                <button 
                  type="button"
                  className="text-blue-600 hover:text-blue-700 font-semibold hover:underline"
                  onClick={() => {
                    // Implementar navegación al registro más adelante
                    console.log('Ir a registro - por implementar')
                  }}
                >
                  Regístrate aquí
                </button>
              </p>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  )
}