'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LegalAnalysis } from "@/types/contracts"
import { 
  Scale,
  FileText,
  AlertTriangle,
  CheckCircle,
  BookOpen,
  Gavel,
  Info
} from "lucide-react"

interface LegalAnalysisSectionProps {
  legalAnalysis: LegalAnalysis | null
  isLoading?: boolean
}

export function LegalAnalysisSection({ legalAnalysis, isLoading }: LegalAnalysisSectionProps) {
  // Estado de carga
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted/50 rounded w-1/3 animate-pulse"></div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="bg-card/80 border-border/60 animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-muted/50 rounded w-3/4 mb-2"></div>
                <div className="h-20 bg-muted/50 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  // Sin análisis legal disponible
  if (!legalAnalysis) {
    return (
      <Card className="bg-card/80 border-border/60 p-8 rounded-2xl text-center">
        <Scale className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Análisis Legal No Disponible
        </h3>
        <p className="text-muted-foreground mb-4">
          El análisis legal detallado aún no está disponible para este contrato. 
          El análisis se genera automáticamente después del procesamiento del contrato.
        </p>
        <Badge variant="secondary" className="text-sm">
          <Info className="w-4 h-4 mr-1" />
          Funcionalidad en desarrollo
        </Badge>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header del análisis legal */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Scale className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold text-foreground">Análisis Legal</h2>
          <Badge variant="default" className="bg-green-500/10 text-green-600 border-green-500/20">
            <CheckCircle className="w-3 h-3 mr-1" />
            Disponible
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          Generado el {new Date(legalAnalysis.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Resumen Ejecutivo */}
      <ExecutiveSummary executiveSummary={legalAnalysis.executive_summary} />

      {/* Leyes Afectadas */}
      <AffectedLaws laws={legalAnalysis.affected_laws} />
    </div>
  )
}

// Componente para el resumen ejecutivo
function ExecutiveSummary({ 
  executiveSummary 
}: { 
  executiveSummary: LegalAnalysis['executive_summary'] 
}) {
  const summaryItems = [
    {
      key: "La naturaleza jurídica del contrato",
      icon: FileText,
      color: "text-blue-600",
      bgColor: "bg-blue-500/10"
    },
    {
      key: "Los principales riesgos legales identificados",
      icon: AlertTriangle,
      color: "text-orange-600",
      bgColor: "bg-orange-500/10"
    },
    {
      key: "El nivel de cumplimiento normativo",
      icon: CheckCircle,
      color: "text-green-600",
      bgColor: "bg-green-500/10"
    },
    {
      key: "Otros puntos importantes",
      icon: Info,
      color: "text-purple-600",
      bgColor: "bg-purple-500/10"
    }
  ]

  return (
    <Card className="bg-card/80 border-border/60 rounded-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookOpen className="w-5 h-5" />
          Resumen Ejecutivo Legal
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {summaryItems.map((item) => {
          const content = executiveSummary[item.key as keyof typeof executiveSummary]
          if (!content) return null

          return (
            <div key={item.key} className="border border-border/60 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className={`rounded-full p-2 ${item.bgColor}`}>
                  <item.icon className={`w-4 h-4 ${item.color}`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-foreground mb-2">{item.key}</h4>
                  <p className="text-muted-foreground leading-relaxed">{content}</p>
                </div>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

// Componente para las leyes afectadas
function AffectedLaws({ laws }: { laws: string[] }) {
  if (!laws || laws.length === 0) {
    return (
      <Card className="bg-card/80 border-border/60 rounded-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gavel className="w-5 h-5" />
            Leyes y Regulaciones Aplicables
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-4">
            No se identificaron leyes específicas aplicables a este contrato.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-card/80 border-border/60 rounded-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gavel className="w-5 h-5" />
          Leyes y Regulaciones Aplicables
          <Badge variant="secondary" className="ml-auto">
            {laws.length} {laws.length === 1 ? 'referencia' : 'referencias'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          {laws.map((law, index) => (
            <div 
              key={index}
              className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg border border-border/40"
            >
              <div className="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                <span className="text-sm font-semibold text-primary">{index + 1}</span>
              </div>
              <div className="flex-1">
                <p className="text-foreground font-medium">{law}</p>
              </div>
              <Badge variant="outline">
                Aplicable
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
