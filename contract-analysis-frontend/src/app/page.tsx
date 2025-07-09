'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Shield, Zap, Brain, ArrowRight, Bot, BarChart, Sparkles } from "lucide-react"
import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen w-full bg-slate-900 text-white">
      <div className="container mx-auto px-4 py-16">

        {/* --- Hero Section --- */}
        <div className="text-center mb-24 pt-10">
          <div className="inline-block bg-gradient-to-r from-fuchsia-500 to-cyan-500 rounded-full px-4 py-1.5 text-sm font-semibold mb-6">
            Inteligencia Artificial para tus Contratos
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
            Tus contratos,
            <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
              sin letra pequeña.
            </span>
          </h1>
          <p className="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            Sube tu contrato y deja que nuestra IA encuentre cláusulas raras o abusivas en segundos.
            Simple, rápido y seguro.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/contracts/new">
              <Button
                size="lg"
                className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-gradient-to-r from-purple-500 to-pink-500 font-medium text-white transition-all duration-300 ease-in-out hover:from-purple-600 hover:to-pink-600"
              >
                <span className="relative z-10 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 transition-transform duration-300 group-hover:rotate-12" />
                  Analizar mi Contrato
                </span>
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="ghost" className="text-slate-300 hover:bg-slate-800 hover:text-white flex items-center gap-2">
                Ir al Dashboard
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>

        {/* --- Features - Bento Grid --- */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-24">
          {/* Feature 1 */}
          <Card className="md:col-span-2 bg-slate-800/50 border-slate-700/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-slate-800 transition-colors">
              <div>
                <CardHeader className="p-0 mb-4">
                  <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                    <Bot className="w-6 h-6 text-purple-400" />
                  </div>
                  <CardTitle className="text-xl font-bold">Análisis con IA de Vanguardia</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <p className="text-slate-400">
                    Nuestra IA, entrenada específicamente con leyes y contratos dominicanos,
                    identifica riesgos que otros pasarían por alto. No es magia, es tecnología.
                  </p>
                </CardContent>
              </div>
          </Card>
          
          {/* Feature 2 */}
          <Card className="bg-slate-800/50 border-slate-700/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-slate-800 transition-colors">
            <CardHeader className="p-0 mb-4">
              <div className="bg-pink-500/10 border border-pink-500/30 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-pink-400" />
              </div>
              <CardTitle className="text-xl font-bold">Resultados al Instante</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <p className="text-slate-400">
                Pega el texto de tu contrato y obtén un reporte claro en menos de lo que tardas en pedir un café.
              </p>
            </CardContent>
          </Card>

          {/* Feature 3 */}
          <Card className="bg-slate-800/50 border-slate-700/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-slate-800 transition-colors">
            <CardHeader className="p-0 mb-4">
               <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-cyan-400" />
              </div>
              <CardTitle className="text-xl font-bold">Protección y Claridad</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <p className="text-slate-400">
                Te "traducimos" el lenguaje legal complicado y te damos recomendaciones para que firmes con confianza.
              </p>
            </CardContent>
          </Card>

          {/* Feature 4 */}
          <Card className="md:col-span-2 bg-slate-800/50 border-slate-700/80 p-6 rounded-2xl flex flex-col justify-between hover:bg-slate-800 transition-colors">
             <div>
                <CardHeader className="p-0 mb-4">
                   <div className="bg-green-500/10 border border-green-500/30 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
                    <BarChart className="w-6 h-6 text-green-400" />
                  </div>
                  <CardTitle className="text-xl font-bold">Dashboard Intuitivo</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <p className="text-slate-400">
                    Visualiza el riesgo de tu contrato, gestiona tus documentos y revisa análisis anteriores desde un solo lugar.
                  </p>
                </CardContent>
              </div>
          </Card>
        </div>

        {/* --- Final CTA --- */}
        <div className="text-center rounded-2xl p-12 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 shadow-2xl shadow-purple-500/10">
          <h2 className="text-4xl font-bold text-white mb-4">
            ¿Listo para tomar el control?
          </h2>
          <p className="text-slate-400 mb-8 max-w-xl mx-auto">
            No dejes que la letra pequeña te tome por sorpresa.
            Únete a cientos de usuarios que ya firman con total seguridad.
          </p>
          <Link href="/contracts/new">
             <Button
                size="lg"
                className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-gradient-to-r from-purple-500 to-pink-500 font-medium text-white transition-all duration-300 ease-in-out hover:from-purple-600 hover:to-pink-600 text-lg px-8 py-3"
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
  )
}
