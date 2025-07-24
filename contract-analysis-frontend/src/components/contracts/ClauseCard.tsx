import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, CheckCircle, Brain, Bot, ChevronDown, MessageSquareQuote, FileSignature } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"

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
  const [isExpanded, setIsExpanded] = useState(false)

  const isAbusiveByML = clause.ml_analysis?.is_abusive ?? false
  const isAbusiveByGPT = clause.gpt_analysis?.is_abusive ?? false
  const isAbusive = isAbusiveByML || isAbusiveByGPT;
  
  const riskLevel = clause.risk_score >= 0.8 ? 'high' : clause.risk_score >= 0.7 ? 'medium' : 'low';

  const riskStyles = {
    high: {
      border: "border-destructive/40 hover:border-destructive/80",
      iconBg: "bg-destructive/10",
      iconColor: "text-destructive",
      icon: <AlertTriangle />,
    },
    medium: {
      border: "border-yellow-500/40 hover:border-yellow-500/80",
      iconBg: "bg-yellow-500/10",
      iconColor: "text-yellow-500",
      icon: <AlertTriangle />,
    },
    low: {
      border: "border-border hover:border-green-500/80",
      iconBg: "bg-green-500/10",
      iconColor: "text-green-500",
      icon: <CheckCircle />,
    },
  }

  const currentRisk = riskStyles[riskLevel]

  return (
    <div
      className={cn(
        "w-full bg-card/60 border rounded-xl transition-all duration-300",
        currentRisk.border
      )}
    >
      {/* --- Card Header --- */}
      <div
        className="flex items-center p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className={cn("w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-lg mr-4", currentRisk.iconBg, currentRisk.iconColor)}>
          {currentRisk.icon}
        </div>
        <div className="flex-grow">
          <h3 className="font-semibold text-foreground">
            Cláusula {clause.clause_number}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-1">
            {clause.text}
          </p>
        </div>
        <div className="ml-4 flex items-center gap-2 text-muted-foreground">
           <span className="text-xs font-mono bg-secondary/60 px-2 py-0.5 rounded">
            Riesgo: {(clause.risk_score * 100).toFixed(0)}%
          </span>
          <ChevronDown
            className={cn(
              "w-5 h-5 transition-transform duration-300",
              isExpanded && "rotate-180"
            )}
          />
        </div>
      </div>
      
      {/* --- Expandable Content --- */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-border/80">
          <div className="space-y-6 pt-4">
            
            {/* Clause Text */}
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Texto Completo</h4>
              <p className="text-sm text-muted-foreground leading-relaxed bg-secondary/50 p-3 rounded-md">
                {clause.text}
              </p>
            </div>
            
            {/* AI Analysis Section */}
            {clause.gpt_analysis && (
              <div className="p-4 bg-secondary/50 rounded-lg border border-border">
                <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                  <Bot className="w-5 h-5 text-primary"/>
                  Análisis de IA
                </h4>

                <div className="space-y-4">
                   {/* Explanation */}
                   <div className="flex items-start gap-3">
                     <MessageSquareQuote className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5"/>
                     <div>
                       <p className="text-sm text-foreground font-medium">Explicación:</p>
                       <p className="text-sm text-muted-foreground">{clause.gpt_analysis.explanation}</p>
                     </div>
                   </div>

                   {/* Suggested Fix -> Abusive Reason */}
                   {clause.gpt_analysis.suggested_fix && (
                      <div className="flex items-start gap-3">
                         <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5"/>
                         <div>
                           <p className="text-sm text-foreground font-medium">Razón de la Abusividad (según IA):</p>
                           <p className="text-sm text-destructive/80 bg-destructive/10 p-2 rounded-md font-mono">
                             {clause.gpt_analysis.suggested_fix}
                           </p>
                         </div>
                      </div>
                   )}
                </div>
              </div>
            )}
            
            {/* ML Analysis */}
            {clause.ml_analysis && (
              <div className="text-xs text-muted-foreground flex items-center justify-end gap-2">
                  <Brain size={14} />
                  <span>Modelo ML: {isAbusiveByML ? 'Detecta Abusiva' : 'No detecta abusiva'} ({(clause.ml_analysis.abuse_probability * 100).toFixed(1)}% prob.)</span>
              </div>
            )}
            
          </div>
        </div>
      )}
    </div>
  )
} 