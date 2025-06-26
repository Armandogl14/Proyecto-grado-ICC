import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { RiskIndicator } from "./RiskIndicator"
import type { Clause } from "@/types/contracts"
import { AlertTriangle, CheckCircle, Users, MapPin, DollarSign, Calendar } from "lucide-react"

interface ClauseCardProps {
  clause: Clause
  className?: string
}

export function ClauseCard({ clause, className = "" }: ClauseCardProps) {
  const getEntityIcon = (label: string) => {
    switch (label.toLowerCase()) {
      case 'person':
      case 'persona':
        return <Users className="w-3 h-3" />
      case 'money':
      case 'dinero':
        return <DollarSign className="w-3 h-3" />
      case 'date':
      case 'fecha':
        return <Calendar className="w-3 h-3" />
      case 'gpe':
      case 'lugar':
        return <MapPin className="w-3 h-3" />
      default:
        return null
    }
  }

  return (
    <Card className={`transition-all hover:shadow-md ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {clause.clause_number}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge 
              variant={clause.is_abusive ? "destructive" : "success"}
              className="flex items-center gap-1"
            >
              {clause.is_abusive ? (
                <AlertTriangle className="w-3 h-3" />
              ) : (
                <CheckCircle className="w-3 h-3" />
              )}
              {clause.is_abusive ? "Abusiva" : "Normal"}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {Math.round(clause.confidence_score * 100)}% confianza
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-sm leading-relaxed mb-4">
          {clause.text}
        </p>
        
        {clause.entities && clause.entities.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-medium text-muted-foreground">
              Entidades detectadas:
            </h4>
            <div className="flex flex-wrap gap-1">
              {clause.entities.map((entity, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="text-xs flex items-center gap-1"
                >
                  {getEntityIcon(entity.label)}
                  {entity.text}
                  <span className="text-muted-foreground">
                    ({entity.label})
                  </span>
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 