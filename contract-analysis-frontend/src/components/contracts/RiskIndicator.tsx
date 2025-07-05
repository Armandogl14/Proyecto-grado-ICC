import { Badge } from "@/components/ui/badge"
import { formatRiskScore, getRiskLevel } from "@/lib/utils"
import { AlertTriangle, CheckCircle, AlertCircle } from "lucide-react"

interface RiskIndicatorProps {
  riskScore: number
  className?: string
  showIcon?: boolean
  showPercentage?: boolean
}

type RiskDetails = {
  label: string;
  variant: "secondary" | "success" | "warning" | "destructive";
  icon: React.ReactNode;
}

export function RiskIndicator({ 
  riskScore, 
  className = "",
  showIcon = true,
  showPercentage = true
}: RiskIndicatorProps) {
  const getRiskDetails = (): RiskDetails => {
    if (riskScore === undefined || riskScore === null || riskScore < 0) {
      return {
        label: "N/D",
        variant: "secondary",
        icon: null
      }
    }
    if (riskScore <= 3) {
      return {
        label: "Bajo",
        variant: "success",
        icon: <CheckCircle className="w-4 h-4" />
      }
    }
    if (riskScore <= 7) {
      return {
        label: "Medio",
        variant: "warning",
        icon: <AlertCircle className="w-4 h-4" />
      }
    }
    return {
      label: "Alto",
      variant: "destructive",
      icon: <AlertTriangle className="w-4 h-4" />
    }
  }

  const { label, variant, icon } = getRiskDetails()

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Badge variant={variant} className="flex items-center gap-1">
        {showIcon && icon}
        {label}
        {showPercentage && riskScore >= 0 && ` (${formatRiskScore(riskScore)})`}
      </Badge>
    </div>
  )
} 