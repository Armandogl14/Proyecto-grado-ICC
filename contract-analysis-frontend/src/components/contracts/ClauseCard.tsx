import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, CheckCircle, Brain, Bot, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface ClauseCardProps {
  clause: {
    text: string
    ml_analysis?: {
      is_abusive: boolean
      abuse_probability: number
    }
    gpt_analysis?: {
      is_valid_clause: boolean
      is_abusive: boolean
      explanation: string
      suggested_fix?: string
    }
    entities: Array<{
      text: string
      label: string
    }>
    risk_score: number
    clause_number: number
  }
}

export function ClauseCard({ clause }: ClauseCardProps) {
  const [showDetails, setShowDetails] = useState(false)

  // Determinar el estado general de la cláusula con validaciones
  const isAbusive = clause.ml_analysis?.is_abusive || clause.gpt_analysis?.is_abusive
  
  const isInvalid = clause.gpt_analysis?.is_valid_clause === false
  
  return (
    <Card className={`overflow-hidden transition-all ${isAbusive ? 'border-destructive/50' : ''}`}>
      <CardContent className="p-4">
        {/* Header con número y badges */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold">Cláusula {clause.clause_number}</span>
            <div className="flex gap-2">
              {isInvalid && (
                <Badge variant="outline" className="text-amber-500 border-amber-500">
                  No es cláusula válida
                </Badge>
              )}
              {isAbusive && (
                <Badge variant="destructive" className="flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  Abusiva
                </Badge>
              )}
              {!isAbusive && !isInvalid && (
                <Badge variant="outline" className="text-emerald-500 border-emerald-500 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  No abusiva
                </Badge>
              )}
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs"
          >
            {showDetails ? 'Ocultar detalles' : 'Ver detalles'}
          </Button>
        </div>

        {/* Texto de la cláusula */}
        <div className="text-sm text-muted-foreground mb-4">
          {clause.text}
        </div>

        {/* Detalles del análisis */}
        {showDetails && (
          <div className="space-y-4 mt-4 pt-4 border-t">
            {/* Análisis ML */}
            {clause.ml_analysis && (
              <div className="flex items-start gap-2">
                <Brain className="w-4 h-4 text-primary mt-1" />
                <div>
                  <h4 className="text-sm font-medium mb-1">Análisis ML</h4>
                  <div className="text-sm text-muted-foreground">
                    <div className="flex items-center gap-2 mb-1">
                      <span>Resultado:</span>
                      <Badge variant={clause.ml_analysis.is_abusive ? "destructive" : "outline"}>
                        {clause.ml_analysis.is_abusive ? "Abusiva" : "No abusiva"}
                      </Badge>
                    </div>
                    <div>
                      Probabilidad de ser abusiva: {(clause.ml_analysis.abuse_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Análisis GPT */}
            {clause.gpt_analysis && (
              <div className="flex items-start gap-2">
                <Bot className="w-4 h-4 text-primary mt-1" />
                <div>
                  <h4 className="text-sm font-medium mb-1">Análisis GPT</h4>
                  <div className="text-sm text-muted-foreground space-y-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span>Resultado:</span>
                      <Badge variant={clause.gpt_analysis.is_abusive ? "destructive" : "outline"}>
                        {clause.gpt_analysis.is_abusive ? "Abusiva" : "No abusiva"}
                      </Badge>
                    </div>
                    <p>{clause.gpt_analysis.explanation}</p>
                    
                    {clause.gpt_analysis.suggested_fix && (
                      <div className="mt-2 p-3 bg-secondary/30 rounded-md">
                        <p className="font-medium mb-1">Sugerencia de corrección:</p>
                        <p className="text-sm">{clause.gpt_analysis.suggested_fix}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Entidades detectadas */}
            {clause.entities && clause.entities.length > 0 && (
              <div className="flex items-start gap-2">
                <ArrowRight className="w-4 h-4 text-primary mt-1" />
                <div>
                  <h4 className="text-sm font-medium mb-1">Entidades Detectadas</h4>
                  <div className="flex flex-wrap gap-2">
                    {clause.entities.map((entity, index) => (
                      <Badge key={index} variant="secondary">
                        {entity.text} ({entity.label})
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Score de riesgo */}
            <div className="flex items-center gap-2 mt-2">
              <span className="text-sm text-muted-foreground">
                Score de riesgo: {clause.risk_score !== null && !isNaN(clause.risk_score) ? (clause.risk_score * 100).toFixed(1) : '0.0'}%
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 