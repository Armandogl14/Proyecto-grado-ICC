import { Badge } from "@/components/ui/badge"
import { formatRiskScore, getRiskLevel } from "@/lib/utils"
import { AlertTriangle, CheckCircle, AlertCircle } from "lucide-react"

interface RiskIndicatorProps {
  riskScore: number
  className?: string
  showIcon?: boolean
  showPercentage?: boolean
}

export function RiskIndicator({ 
  riskScore, 
  className = "",
  showIcon = true,
  showPercentage = true
}: RiskIndicatorProps) {
  const { level, variant } = getRiskLevel(riskScore)
  
  const getIcon = () => {
    if (!showIcon) return null
    
    switch (variant) {
      case 'success':
        return <CheckCircle className="w-4 h-4" />
      case 'warning':
        return <AlertCircle className="w-4 h-4" />
      case 'destructive':
        return <AlertTriangle className="w-4 h-4" />
      default:
        return null
    }
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Badge variant={variant} className="flex items-center gap-1">
        {getIcon()}
        {level}
        {showPercentage && ` (${formatRiskScore(riskScore)})`}
      </Badge>
    </div>
  )
} 