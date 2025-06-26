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
      color: "text-blue-600"
    },
    {
      title: "Pendientes",
      value: stats?.pending_analysis || 0,
      icon: Clock,
      color: "text-yellow-600"
    },
    {
      title: "Completados",
      value: stats?.completed || 0,
      icon: CheckCircle,
      color: "text-green-600"
    },
    {
      title: "Alto Riesgo",
      value: stats?.high_risk || 0,
      icon: AlertTriangle,
      color: "text-red-600"
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
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
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.title}
              </CardTitle>
              <stat.icon className={`w-4 h-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Risk Distribution */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              Bajo Riesgo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats?.low_risk || 0}
            </div>
            <p className="text-xs text-gray-500">contratos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-yellow-600" />
              Riesgo Medio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats?.medium_risk || 0}
            </div>
            <p className="text-xs text-gray-500">contratos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              Alto Riesgo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {stats?.high_risk || 0}
            </div>
            <p className="text-xs text-gray-500">contratos</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Contracts */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Contratos Recientes</CardTitle>
            <Link href="/contracts">
              <Button variant="outline" size="sm">
                Ver todos
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {contractsData?.results && contractsData.results.length > 0 ? (
            <div className="space-y-4">
              {contractsData.results.map((contract) => (
                <div 
                  key={contract.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <h3 className="font-medium">{contract.title}</h3>
                    <p className="text-sm text-gray-500">
                      {contract.contract_type.name} • {formatDate(contract.created_at)}
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {contract.risk_score !== undefined && (
                      <RiskIndicator 
                        riskScore={contract.risk_score} 
                        showIcon={false}
                      />
                    )}
                    
                    <div className="text-sm text-gray-500">
                      {contract.total_clauses} cláusulas
                    </div>
                    
                    <Link href={`/contracts/${contract.id}`}>
                      <Button size="sm" variant="outline">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No hay contratos aún</p>
              <Link href="/contracts/new">
                <Button className="mt-4">
                  Crear primer contrato
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
      </div>
    </div>
  )
} 