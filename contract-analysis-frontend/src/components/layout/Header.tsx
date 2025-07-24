'use client'

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"
import { LayoutDashboard, LogOut, User, FilePlus, Sparkles } from "lucide-react"

export function Header() {
  const { user, logout, isAuthenticated } = useAuth()

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
              <span className="hidden sm:inline text-sm text-muted-foreground">
                Bienvenido, {user?.username}
              </span>

              <Link href="/dashboard">
                <Button variant="ghost" size="sm" className="hidden sm:flex items-center gap-2 text-foreground hover:bg-secondary">
                  <LayoutDashboard className="h-4 w-4" />
                  Dashboard
                </Button>
              </Link>
              
              <Link href="/contracts/new">
                 <Button size="sm" className="group relative inline-flex h-9 items-center justify-center overflow-hidden rounded-md bg-primary font-medium text-primary-foreground transition-all duration-300 ease-in-out hover:bg-primary/90">
                   <span className="relative z-10 flex items-center gap-2">
                    <FilePlus className="h-4 w-4" />
                    Nuevo Análisis
                   </span>
                </Button>
              </Link>

              <Button onClick={logout} variant="ghost" size="icon" className="text-muted-foreground hover:bg-secondary hover:text-destructive">
                <LogOut className="h-5 w-5" />
              </Button>
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