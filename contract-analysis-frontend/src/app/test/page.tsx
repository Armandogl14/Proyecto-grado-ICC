'use client'

import { useState } from 'react'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2, LogIn, LogOut, User, FileText, AlertCircle } from 'lucide-react'

// Componente interno que usa el contexto
function AuthTestComponent() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [contractsData, setContractsData] = useState<any>(null)
  const [contractsLoading, setContractsLoading] = useState(false)
  const [contractsError, setContractsError] = useState<string | null>(null)

  const handleLogin = async () => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      await login({
        username: 'admin',
        password: 'admin123'
      })
    } catch (err: any) {
      setError(err.message || 'Error desconocido')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      // Limpiar datos de contratos al hacer logout
      setContractsData(null)
      setContractsError(null)
    } catch (err: any) {
      console.error('Error en logout:', err)
    }
  }

  // Nueva función para probar el endpoint de contratos
  const testContractsEndpoint = async () => {
    if (!isAuthenticated) {
      setContractsError('Debe estar autenticado para acceder a contratos')
      return
    }

    setContractsLoading(true)
    setContractsError(null)
    setContractsData(null)

    try {
      const accessToken = localStorage.getItem('access_token')
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://172.245.214.69'
      
      const response = await fetch(`${backendUrl}/api/contracts/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setContractsData(data)
    } catch (err: any) {
      console.error('Error al obtener contratos:', err)
      setContractsError(err.message || 'Error desconocido')
    } finally {
      setContractsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
            <p className="text-gray-600">Verificando autenticación...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Prueba de Autenticación
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">
              Esta es una vista de prueba para verificar que el sistema de autenticación funciona correctamente.
            </p>
          </CardContent>
        </Card>

        {/* Estado de autenticación */}
        <Card>
          <CardHeader>
            <CardTitle>Estado Actual</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Estado:</label>
                <p className={`text-lg font-semibold ${isAuthenticated ? 'text-green-600' : 'text-red-600'}`}>
                  {isAuthenticated ? '✅ Autenticado' : '❌ No autenticado'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Usuario:</label>
                <p className="text-lg">
                  {user ? user.username : 'Sin usuario'}
                </p>
              </div>
            </div>

            {user && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Datos del Usuario:</h4>
                <div className="text-sm text-green-800 space-y-1">
                  <p><strong>ID:</strong> {user.id}</p>
                  <p><strong>Username:</strong> {user.username}</p>
                  <p><strong>Email:</strong> {user.email}</p>
                  <p><strong>Nombre:</strong> {user.first_name || 'No especificado'}</p>
                  <p><strong>Apellido:</strong> {user.last_name || 'No especificado'}</p>
                  <p><strong>Activo:</strong> {user.is_active ? 'Sí' : 'No'}</p>
                  <p><strong>Staff:</strong> {user.is_staff ? 'Sí' : 'No'}</p>
                  <p><strong>Fecha registro:</strong> {new Date(user.date_joined).toLocaleDateString()}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Prueba de Endpoints Protegidos */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Prueba de Endpoints Protegidos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              <p>Esta sección prueba si podemos acceder a endpoints protegidos cuando estamos autenticados.</p>
            </div>

            <div className="flex gap-4">
              <Button 
                onClick={testContractsEndpoint}
                disabled={contractsLoading || !isAuthenticated}
                className="flex items-center gap-2"
                variant={isAuthenticated ? "default" : "secondary"}
              >
                {contractsLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Obteniendo contratos...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    Probar GET /api/contracts/
                  </>
                )}
              </Button>
            </div>

            {!isAuthenticated && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-yellow-600" />
                  <p className="text-yellow-800 text-sm">
                    Debes estar autenticado para probar los endpoints protegidos
                  </p>
                </div>
              </div>
            )}

            {contractsError && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <p className="text-red-800 text-sm">
                    <strong>Error al acceder a contratos:</strong> {contractsError}
                  </p>
                </div>
              </div>
            )}

            {contractsData && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">✅ Endpoint de Contratos Accesible:</h4>
                <div className="text-sm text-green-800 space-y-2">
                  <p><strong>Respuesta exitosa del servidor:</strong></p>
                  <pre className="bg-green-100 p-2 rounded text-xs overflow-auto max-h-40">
                    {JSON.stringify(contractsData, null, 2)}
                  </pre>
                  {contractsData.results && (
                    <p><strong>Total de contratos:</strong> {contractsData.results.length}</p>
                  )}
                  {contractsData.count !== undefined && (
                    <p><strong>Count total:</strong> {contractsData.count}</p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Acciones */}
        <Card>
          <CardHeader>
            <CardTitle>Acciones</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">
                  <strong>Error:</strong> {error}
                </p>
              </div>
            )}

            <div className="flex gap-4">
              {!isAuthenticated ? (
                <Button 
                  onClick={handleLogin}
                  disabled={isSubmitting}
                  className="flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Iniciando sesión...
                    </>
                  ) : (
                    <>
                      <LogIn className="w-4 h-4" />
                      Login (admin/admin123)
                    </>
                  )}
                </Button>
              ) : (
                <Button 
                  onClick={handleLogout}
                  variant="destructive"
                  className="flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Cerrar Sesión
                </Button>
              )}
            </div>

            <div className="text-sm text-gray-600">
              <p><strong>Credenciales de prueba:</strong></p>
              <p>Usuario: admin</p>
              <p>Contraseña: admin123</p>
              <p>Endpoint: {process.env.NEXT_PUBLIC_BACKEND_URL || 'http://172.245.214.69'}/api/auth/login/</p>
            </div>
          </CardContent>
        </Card>

        {/* Información técnica */}
        <Card>
          <CardHeader>
            <CardTitle>Información Técnica</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-gray-600">
            <p><strong>Tokens en localStorage:</strong></p>
            <p>Access Token: {localStorage.getItem('access_token') ? '✅ Presente' : '❌ Ausente'}</p>
            <p>Refresh Token: {localStorage.getItem('refresh_token') ? '✅ Presente' : '❌ Ausente'}</p>
            <p>User Data: {localStorage.getItem('user_data') ? '✅ Presente' : '❌ Ausente'}</p>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}

// Componente principal con Provider
export default function AuthTestPage() {
  return (
    <AuthProvider>
      <AuthTestComponent />
    </AuthProvider>
  )
}
