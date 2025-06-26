'use client'

import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"
import { User, LogOut, FileText } from "lucide-react"
import Link from "next/link"

export function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <FileText className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Análisis de Contratos
              </h1>
              <p className="text-xs text-gray-500">Sistema ML de Detección</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link 
              href="/dashboard" 
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Dashboard
            </Link>
            <Link 
              href="/contracts/new" 
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Nuevo Contrato
            </Link>
          </nav>

          {/* User Info */}
          {user && (
            <div className="flex items-center gap-4">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user.username}
                </p>
                <p className="text-xs text-gray-500">
                  {user.is_superuser ? 'Administrador' : 'Usuario'}
                </p>
              </div>
              
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-gray-600" />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-gray-600 hover:text-gray-900"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:ml-2 sm:inline">Salir</span>
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
} 