'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Header } from "@/components/layout/Header"
import { useDashboardStats, useContracts } from "@/hooks/useContracts"
import { formatDate } from "@/lib/utils"
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  FileUp,
  ArrowRight,
  Eye,
  ShieldCheck,
  ShieldAlert,
  BarChart
} from "lucide-react"
import Link from "next/link"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

export default function DashboardPage() {
  const { data: stats, isLoading: isLoadingStats } = useDashboardStats()
  const { data: contractsData, isLoading: isLoadingContracts } = useContracts({ 
    page_size: 5 
  })

  // Skeleton Loader
  if (isLoadingStats || isLoadingContracts) {
    return (
      <>
        <Header />
        <div className="container mx-auto p-4 md:p-8 space-y-8">
          <div className="h-8 bg-slate-700/50 rounded w-1/4 animate-pulse"></div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-28 bg-slate-800/80 rounded-2xl animate-pulse"></div>
            ))}
          </div>
          <div className="grid gap-6 md:grid-cols-5">
            <div className="md:col-span-3 h-80 bg-slate-800/80 rounded-2xl animate-pulse"></div>
            <div className="md:col-span-2 h-80 bg-slate-800/80 rounded-2xl animate-pulse"></div>
          </div>
        </div>
      </>
    )
  }

  const statsCards = [
    {
      title: "Total Contratos",
      value: stats?.total_contracts || 0,
      icon: FileText,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10"
    },
    {
      title: "Pendientes",
      value: stats?.pending_analysis || 0,
      icon: Clock,
      color: "text-amber-400",
      bgColor: "bg-amber-500/10"
    },
    {
      title: "Completados",
      value: stats?.completed || 0,
      icon: CheckCircle,
      color: "text-green-400",
      bgColor: "bg-green-500/10"
    },
    {
      title: "Alto Riesgo",
      value: stats?.high_risk || 0,
      icon: ShieldAlert,
      color: "text-red-400",
      bgColor: "bg-red-500/10"
    }
  ]

  const riskData = [
    { name: 'Bajo', value: stats?.low_risk || 0, color: '#34d399' },
    { name: 'Medio', value: stats?.medium_risk || 0, color: '#f59e0b' },
    { name: 'Alto', value: stats?.high_risk || 0, color: '#f87171' },
  ]
  const totalRiskContracts = riskData.reduce((acc, item) => acc + item.value, 0)

  return (
    <>
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Dashboard</h1>
            <p className="text-slate-400 mt-1">
              Aquí tienes un resumen de tus análisis.
            </p>
          </div>
          <Link href="/contracts/new">
            <Button
              size="sm"
              className="group relative inline-flex h-9 items-center justify-center overflow-hidden rounded-md bg-gradient-to-r from-purple-500 to-pink-500 font-medium text-white transition-all duration-300 ease-in-out hover:from-purple-600 hover:to-pink-600">
               <span className="relative z-10 flex items-center gap-2">
                <FileUp className="w-4 h-4" />
                Analizar Contrato
               </span>
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4 mb-8">
          {statsCards.map((stat) => (
            <Card key={stat.title} className="bg-slate-800/80 border-slate-700/60 backdrop-blur-sm p-5 rounded-2xl hover:bg-slate-800 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex flex-col space-y-1.5">
                  <p className="text-sm font-medium text-slate-400">{stat.title}</p>
                  <p className="text-3xl font-bold">{stat.value}</p>
                </div>
                <div className={`rounded-full p-3 ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Recent Contracts & Risk Distribution */}
        <div className="grid gap-8 lg:grid-cols-5">
          {/* Recent Contracts List */}
          <div className="lg:col-span-3">
             <Card className="bg-slate-800/80 border-slate-700/60 backdrop-blur-sm p-6 rounded-2xl h-full">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Contratos Recientes</h3>
                  <Link href="/contracts">
                    <Button variant="ghost" size="sm" className="text-slate-300 hover:bg-slate-700 hover:text-white group">
                      Ver todos <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </Link>
                </div>
                <div className="space-y-2">
                  {contractsData?.results && contractsData.results.length > 0 ? (
                    contractsData.results.map((contract) => (
                      <Link href={`/contracts/${contract.id}`} key={contract.id} className="block">
                        <div
                          className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-700/50 transition-colors cursor-pointer"
                        >
                          <div className="flex-1">
                            <h4 className="font-medium text-white">{contract.title}</h4>
                            <p className="text-sm text-slate-400">
                              {contract.contract_type.name} • {formatDate(contract.created_at)}
                            </p>
                          </div>
                          <div className="flex items-center gap-6">
                             <div className={`text-sm font-semibold hidden sm:flex items-center gap-2 ${
                                contract.risk_score < 0.3 ? 'text-green-400' :
                                contract.risk_score < 0.7 ? 'text-amber-400' : 'text-red-400'
                              }`}>
                                {contract.risk_score < 0.3 ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />}
                                {`${(contract.risk_score * 100).toFixed(0)}% Riesgo`}
                             </div>
                            <Eye className="w-5 h-5 text-slate-500" />
                          </div>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="text-center py-10">
                      <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                      <p className="text-slate-400">Aún no has analizado ningún contrato.</p>
                    </div>
                  )}
                </div>
             </Card>
          </div>

          {/* Risk Distribution Chart */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-800/80 border-slate-700/60 backdrop-blur-sm p-6 rounded-2xl h-full">
              <h3 className="text-lg font-semibold text-white mb-4">Distribución de Riesgo</h3>
              {totalRiskContracts > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={100}
                      innerRadius={60}
                      fill="#8884d8"
                      dataKey="value"
                      stroke="none"
                    >
                      {riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(30, 41, 59, 0.8)',
                        borderColor: 'rgb(51, 65, 85)',
                        borderRadius: '0.75rem',
                        color: 'white'
                      }}
                      cursor={{ fill: 'rgba(100, 116, 139, 0.2)' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                 <div className="text-center py-10 flex flex-col items-center justify-center h-[250px]">
                    <BarChart className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">No hay datos de riesgo para mostrar.</p>
                  </div>
              )}
            </Card>
          </div>
        </div>
      </main>
    </>
  )
} 