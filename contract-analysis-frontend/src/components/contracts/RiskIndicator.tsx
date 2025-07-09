import { formatRiskScore, getRiskLevel } from "@/lib/utils"
import { AlertTriangle, CheckCircle, ShieldQuestion, ShieldAlert } from "lucide-react"

interface RiskIndicatorProps {
  riskScore: number
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function RiskIndicator({ 
  riskScore, 
  className = "",
  size = 'md'
}: RiskIndicatorProps) {
  
  if (riskScore === undefined || riskScore === null || riskScore < 0) {
    return (
      <div className={`flex items-center gap-2 text-slate-500 ${className}`}>
        <ShieldQuestion className="w-5 h-5" />
        <span className="font-semibold">N/A</span>
      </div>
    )
  }

  const { level, color, variant } = getRiskLevel(riskScore)
  
  const iconMap = {
    success: <CheckCircle />,
    warning: <ShieldAlert />,
    destructive: <AlertTriangle />,
  }

  const sizeStyles = {
    sm: {
      container: "px-2.5 py-1 text-sm rounded-md",
      icon: "w-4 h-4",
    },
    md: {
      container: "px-4 py-2 text-base rounded-lg",
      icon: "w-5 h-5",
    },
    lg: {
      container: "px-6 py-3 text-lg rounded-xl",
      icon: "w-6 h-6",
    }
  }

  const styles = sizeStyles[size]

  const colorStyles = {
    success: 'bg-green-500/10 text-green-400',
    warning: 'bg-amber-500/10 text-amber-400',
    destructive: 'bg-red-500/10 text-red-400',
  }

  return (
    <div className={`inline-flex items-center gap-2 font-semibold ${colorStyles[variant]} ${styles.container} ${className}`}>
      <div className={styles.icon}>
        {iconMap[variant]}
      </div>
      <span>{level} - {formatRiskScore(riskScore)}</span>
    </div>
  )
} 