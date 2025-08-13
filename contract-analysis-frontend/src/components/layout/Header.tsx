'use client'

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { LayoutDashboard, LogOut, User, FilePlus, Sparkles, Settings, ChevronDown } from "lucide-react"
import { useState, useEffect, useRef } from "react"

export function Header() {
  const { user, logout, isAuthenticated } = useAuth()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Cerrar menú cuando se hace clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    setIsUserMenuOpen(false)
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/80 bg-background/50 backdrop-blur-sm">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold text-foreground">LegalAI</span>
        </Link>
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              {/* Navegación Principal */}
              <div className="hidden md:flex items-center gap-2">
                <Link href="/dashboard">
                  <Button variant="ghost" size="sm" className="flex items-center gap-2 text-foreground hover:bg-secondary">
                    <LayoutDashboard className="h-4 w-4" />
                    Dashboard
                  </Button>
                </Link>
                
                <Link href="/contracts">
                  <Button variant="ghost" size="sm" className="flex items-center gap-2 text-foreground hover:bg-secondary">
                    <User className="h-4 w-4" />
                    Contratos
                  </Button>
                </Link>
              </div>

              {/* Botón Nuevo Análisis */}
              <Link href="/contracts/new">
                 <Button size="sm" className="group relative inline-flex h-9 items-center justify-center overflow-hidden rounded-md bg-primary font-medium text-primary-foreground transition-all duration-300 ease-in-out hover:bg-primary/90">
                   <span className="relative z-10 flex items-center gap-2">
                    <FilePlus className="h-4 w-4" />
                    <span className="hidden sm:inline">Nuevo Análisis</span>
                   </span>
                </Button>
              </Link>

              {/* Menú de Usuario */}
              <div className="relative" ref={menuRef}>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="flex items-center gap-2 text-foreground hover:bg-secondary"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                >
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">{user?.username || user?.first_name || 'Usuario'}</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>

                {/* Dropdown Menu */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-background border border-border rounded-md shadow-lg z-50">
                    <div className="py-1">
                      <div className="px-4 py-2 text-sm text-muted-foreground border-b border-border">
                        <div className="font-medium">{user?.username}</div>
                        <div className="text-xs">{user?.email}</div>
                      </div>
                      
                      <Link href="/profile" onClick={() => setIsUserMenuOpen(false)}>
                        <div className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-secondary cursor-pointer">
                          <Settings className="h-4 w-4" />
                          Mi Perfil
                        </div>
                      </Link>
                      
                      <Link href="/dashboard" onClick={() => setIsUserMenuOpen(false)}>
                        <div className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-secondary cursor-pointer md:hidden">
                          <LayoutDashboard className="h-4 w-4" />
                          Dashboard
                        </div>
                      </Link>
                      
                      <button 
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-secondary cursor-pointer w-full text-left text-destructive"
                      >
                        <LogOut className="h-4 w-4" />
                        Cerrar Sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <Link href="/#"> 
              <Button>
                <User className="mr-2 h-4 w-4" />
                Iniciar Sesión
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  )
} 