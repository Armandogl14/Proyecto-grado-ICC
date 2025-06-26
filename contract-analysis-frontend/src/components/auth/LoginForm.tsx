'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"
import { Loader2, LogIn, User } from "lucide-react"

interface LoginFormProps {
  onSuccess?: () => void
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const [credentials, setCredentials] = useState({
    username: 'admin',
    password: 'admin123'
  })
  
  const { login, loginLoading, loginError, autoLogin } = useAuth()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    login(credentials)
  }

  const handleAutoLogin = () => {
    autoLogin()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
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
                onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="admin"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Contraseña
              </label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="admin123"
                required
              />
            </div>

            {loginError && (
              <div className="text-red-500 text-sm text-center">
                {loginError.message}
              </div>
            )}

            <div className="space-y-3">
              <Button
                type="submit"
                disabled={loginLoading}
                className="w-full"
              >
                {loginLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
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
                onClick={handleAutoLogin}
                disabled={loginLoading}
                className="w-full"
              >
                Acceso Rápido (Admin)
              </Button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            <p><strong>Credenciales por defecto:</strong></p>
            <p>Usuario: admin | Contraseña: admin123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 