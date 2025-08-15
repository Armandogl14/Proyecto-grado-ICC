'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Shield, Zap, Brain, ArrowRight, Bot, BarChart, Sparkles } from "lucide-react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { Header } from "@/components/layout/Header"

export default function Home() {
  return (
    <ProtectedRoute>
      <Header />
      <div className="min-h-screen w-full bg-background text-foreground">
      <div className="container mx-auto px-4 py-16">

        {/* --- Hero Section --- */}
        <div className="text-center mb-24 pt-10">
          <div className="inline-block bg-primary/10 text-primary rounded-full px-4 py-1.5 text-sm font-semibold mb-6">
            Inteligencia Artificial para tus Contratos
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
            Tus contratos,
            <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
              sin letra pequeña.
            </span>
          </h1>
          <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
            Sube tu contrato y deja que nuestra IA encuentre cláusulas raras o abusivas en segundos.
            Simple, rápido y seguro.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/contracts/new">
              <Button
                size="lg"
                className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-primary font-medium text-primary-foreground transition-all duration-300 ease-in-out hover:bg-primary/90"
              >
                <span className="relative z-10 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 transition-transform duration-300 group-hover:rotate-12" />
                  Analizar mi Contrato
                </span>
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="ghost" className="text-foreground hover:bg-secondary flex items-center gap-2">
                Ir al Dashboard
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>

        {/* --- Features - Bento Grid --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-24">
          {/* Feature 1 */}
          <Card className="md:col-span-2 bg-card/50 border-border/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-secondary transition-colors">
              <div>
                <CardHeader className="p-0 mb-4">
                  <div className="bg-primary/10 border border-primary/20 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                    <Bot className="w-6 h-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl font-bold">Análisis con IA de Vanguardia</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <p className="text-muted-foreground">
                    Nuestra IA, entrenada específicamente con leyes y contratos dominicanos,
                    identifica riesgos que otros pasarían por alto. No es magia, es tecnología.
                  </p>
                </CardContent>
              </div>
          </Card>
          
          {/* Feature 2 */}
          <Card className="bg-card/50 border-border/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-secondary transition-colors">
            <CardHeader className="p-0 mb-4">
              <div className="bg-accent/50 border border-accent/70 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-xl font-bold">Resultados al Instante</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <p className="text-muted-foreground">
                Pega el texto de tu contrato y obtén un reporte claro en menos de lo que tardas en pedir un café.
              </p>
            </CardContent>
          </Card>

          {/* Feature 3 */}
          <Card className="bg-card/50 border-border/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-secondary transition-colors">
            <CardHeader className="p-0 mb-4">
               <div className="bg-blue-400/10 border border-blue-400/20 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-blue-400" />
              </div>
              <CardTitle className="text-xl font-bold">Protección y Claridad</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <p className="text-muted-foreground">
                Te "traducimos" el lenguaje legal complicado y te damos recomendaciones para que firmes con confianza.
              </p>
            </CardContent>
          </Card>

          {/* Feature 4 */}
          <Card className="md:col-span-2 bg-card/50 border-border/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-secondary transition-colors">
             <div>
                <CardHeader className="p-0 mb-4">
                   <div className="bg-green-400/10 border border-green-400/20 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                    <BarChart className="w-6 h-6 text-green-400" />
                  </div>
                  <CardTitle className="text-xl font-bold">Dashboard Intuitivo</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <p className="text-muted-foreground">
                    Visualiza el riesgo de tu contrato, gestiona tus documentos y revisa análisis anteriores desde un solo lugar.
                  </p>
                </CardContent>
              </div>
          </Card>
        </div>

        {/* --- Final CTA --- */}
        <div className="text-center rounded-2xl p-12 bg-secondary/50 border border-border shadow-2xl shadow-primary/10">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            ¿Listo para tomar el control?
          </h2>
          <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
            No dejes que la letra pequeña te tome por sorpresa.
            Únete a cientos de usuarios que ya firman con total seguridad.
          </p>
          <Link href="/contracts/new">
             <Button
                size="lg"
                className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-primary font-medium text-primary-foreground transition-all duration-300 ease-in-out hover:bg-primary/90 text-lg px-8 py-3"
              >
                <span className="relative z-10 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 transition-transform duration-300 group-hover:rotate-12" />
                  Empezar ahora
                </span>
              </Button>
          </Link>
        </div>

        </div>
      </div>
    </ProtectedRoute>
  )
}
