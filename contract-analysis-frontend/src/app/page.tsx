'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Shield, Zap, Brain, ArrowRight } from "lucide-react"
import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Análisis Inteligente de
            <span className="text-blue-600"> Contratos</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Sistema avanzado de Machine Learning para detectar cláusulas abusivas 
            en contratos dominicanos. Protege tus derechos con tecnología de punta.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard">
              <Button size="lg" className="flex items-center gap-2">
                Ir al Dashboard
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/contracts/new">
              <Button size="lg" variant="outline" className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Analizar Contrato
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <Brain className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <CardTitle>IA Avanzada</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Modelo entrenado con contratos dominicanos para detectar 
                patrones abusivos con alta precisión.
              </p>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <Zap className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
              <CardTitle>Análisis Rápido</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Resultados en segundos. Identifica cláusulas problemáticas 
                y extrae entidades importantes automáticamente.
              </p>
            </CardContent>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <Shield className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <CardTitle>Protección Legal</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Detecta cláusulas que pueden ser perjudiciales para tus 
                intereses y recibe recomendaciones expertas.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white rounded-2xl p-12 shadow-xl">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            ¿Listo para analizar tu contrato?
          </h2>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Carga tu contrato y recibe un análisis completo en tiempo real. 
            Identifica riesgos y protege tus derechos con nuestra tecnología avanzada.
          </p>
          <Link href="/contracts/new">
            <Button size="lg" className="text-lg px-8 py-3">
              Comenzar Análisis Gratuito
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
