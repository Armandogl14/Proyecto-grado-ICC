'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RiskIndicator } from "@/components/contracts/RiskIndicator"
import { Header } from "@/components/layout/Header"
import { useDashboardStats, useContracts } from "@/hooks/useContracts"
import { formatDate } from "@/lib/utils"
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  TrendingUp,
  Plus,
  Eye
} from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  const { data: stats, isLoading: isLoadingStats } = useDashboardStats()
  const { data: contractsData, isLoading: isLoadingContracts } = useContracts({ 
    page_size: 5 
  })

  if (isLoadingStats || isLoadingContracts) {
    return (
      <div className="p-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const statsCards = [
    {
      title: "Total Contratos",
      value: stats?.total_contracts || 0,
      icon: FileText,
      color: "text-primary"
    },
    {
      title: "Pendientes",
      value: stats?.pending_analysis || 0,
      icon: Clock,
      color: "text-amber-500"
    },
    {
      title: "Completados",
      value: stats?.completed || 0,
      icon: CheckCircle,
      color: "text-emerald-500"
    },
    {
      title: "Alto Riesgo",
      value: stats?.high_risk || 0,
      icon: AlertTriangle,
      color: "text-destructive"
    }
  ]

  const GlassCard = ({ children, className }: { children: React.ReactNode, className?: string }) => (
    <div className={`
      bg-card/50 backdrop-blur-xl border border-white/10 rounded-2xl
      dark:bg-slate-800/20 dark:border-slate-700/50
      ${className}
    `}>
      {children}
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-900">
      <Header />
      <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Resumen de análisis de contratos y cláusulas abusivas
          </p>
        </div>
        <Link href="/contracts/new">
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Nuevo Contrato
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat, index) => (
          <GlassCard key={index}>
            <div className="p-5">
              <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                <h3 className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </h3>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">{stat.value}</div>
              </div>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Risk Distribution */}
      <div className="grid gap-6 md:grid-cols-3">
        <GlassCard>
          <div className="p-5">
            <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-500" />
              Bajo Riesgo
            </h3>
            <div className="mt-2 text-2xl font-bold text-emerald-500">
              {stats?.low_risk || 0}
            </div>
            <p className="text-xs text-muted-foreground">contratos</p>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-5">
            <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-500" />
              Riesgo Medio
            </h3>
            <div className="mt-2 text-2xl font-bold text-amber-500">
              {stats?.medium_risk || 0}
            </div>
            <p className="text-xs text-muted-foreground">contratos</p>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-5">
            <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-destructive" />
              Alto Riesgo
            </h3>
            <div className="mt-2 text-2xl font-bold text-destructive">
              {stats?.high_risk || 0}
            </div>
            <p className="text-xs text-muted-foreground">contratos</p>
          </div>
        </GlassCard>
      </div>

      {/* Recent Contracts */}
      <GlassCard>
        <div className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Contratos Recientes</h3>
            <Link href="/contracts">
              <Button variant="ghost" size="sm">
                Ver todos
              </Button>
            </Link>
          </div>
          <div>
            {contractsData?.results && contractsData.results.length > 0 ? (
              <div className="space-y-2">
                {contractsData.results.map((contract) => (
                  <div 
                    key={contract.id}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-200/50 dark:hover:bg-slate-700/50"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-foreground">{contract.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {contract.contract_type.name} • {formatDate(contract.created_at)}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      {contract.risk_score !== undefined && (
                        <RiskIndicator 
                          riskScore={contract.risk_score} 
                          showIcon={false}
                          showPercentage={true}
                        />
                      )}
                      
                      <div className="text-sm text-muted-foreground hidden md:block">
                        {contract.total_clauses} cláusulas
                      </div>
                      
                      <Link href={`/contracts/${contract.id}`}>
                        <Button size="icon" variant="ghost">
                          <Eye className="w-5 h-5" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
                <p className="text-muted-foreground">No hay contratos aún</p>
                <Link href="/contracts/new">
                  <Button variant="outline" className="mt-4">
                    Crear primer contrato
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </GlassCard>
      </div>
    </div>
  )
} 