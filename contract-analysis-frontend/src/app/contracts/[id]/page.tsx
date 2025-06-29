'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RiskIndicator } from "@/components/contracts/RiskIndicator"
import { ClauseCard } from "@/components/contracts/ClauseCard"
import { 
  useRealTimeAnalysis, 
  useAnalyzeContract, 
  useClausesByContract 
} from "@/hooks/useContracts"
import { formatDate } from "@/lib/utils"
import { 
  ArrowLeft, 
  Play, 
  RefreshCw, 
  Download,
  Clock,
  CheckCircle,
  AlertTriangle,
  Loader2
} from "lucide-react"
import Link from "next/link"

interface ContractDetailPageProps {
  params: {
    id: string
  }
}

export default function ContractDetailPage({ params }: ContractDetailPageProps) {
  const { data: contract, isLoading: isLoadingContract } = useRealTimeAnalysis(params.id)
  const { data: clausesData, isLoading: isLoadingClauses } = useClausesByContract(params.id)
  const analyzeContractMutation = useAnalyzeContract()

  const handleAnalyze = () => {
    analyzeContractMutation.mutate({ id: params.id })
  }

  const handleReanalyze = () => {
    analyzeContractMutation.mutate({ id: params.id, forceReanalysis: true })
  }

  if (isLoadingContract) {
    return (
      <div className="p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!contract) {
    return (
      <div className="p-6">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Contrato no encontrado
          </h1>
          <Link href="/dashboard">
            <Button>Volver al Dashboard</Button>
          </Link>
        </div>
      </div>
    )
  }

  const getStatusIcon = () => {
    switch (contract.status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />
      case 'analyzing':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-600" />
      default:
        return null
    }
  }

  const getStatusText = () => {
    switch (contract.status) {
      case 'pending':
        return 'Pendiente de análisis'
      case 'analyzing':
        return 'Analizando...'
      case 'completed':
        return 'Análisis completado'
      case 'error':
        return 'Error en análisis'
      default:
        return 'Estado desconocido'
    }
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {contract.title}
              </h1>
              <p className="text-gray-600 mt-1">
                {contract.contract_type.name} • Creado el {formatDate(contract.created_at)}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Badge className="flex items-center gap-2">
              {getStatusIcon()}
              {getStatusText()}
            </Badge>

            {contract.status === 'pending' && (
              <Button 
                onClick={handleAnalyze}
                disabled={analyzeContractMutation.isPending}
                className="flex items-center gap-2"
              >
                {analyzeContractMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                Analizar
              </Button>
            )}

            {contract.status === 'completed' && (
              <div className="flex gap-2">
                <Button 
                  variant="outline"
                  onClick={handleReanalyze}
                  disabled={analyzeContractMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Re-analizar
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Stats Summary */}
        {contract.status === 'completed' && (
          <div className="grid gap-6 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Total Cláusulas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{contract.total_clauses}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Cláusulas Abusivas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {contract.abusive_clauses_count}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Nivel de Riesgo
                </CardTitle>
              </CardHeader>
              <CardContent>
                {contract.risk_score !== undefined ? (
                  <RiskIndicator 
                    riskScore={contract.risk_score} 
                    showIcon={false}
                  />
                ) : (
                  <div className="text-2xl font-bold text-gray-400">N/A</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Fecha Análisis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm">
                  {contract.analyzed_at ? formatDate(contract.analyzed_at) : 'N/A'}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Content */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Original Text */}
          <Card>
            <CardHeader>
              <CardTitle>Texto Original</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="max-h-96 overflow-y-auto">
                <pre className="text-sm whitespace-pre-wrap leading-relaxed">
                  {contract.original_text}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Clauses Analysis */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Análisis de Cláusulas</CardTitle>
              </CardHeader>
              <CardContent>
                {contract.status === 'analyzing' && (
                  <div className="text-center py-8">
                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Analizando cláusulas...</p>
                  </div>
                )}

                {contract.status === 'pending' && (
                  <div className="text-center py-8">
                    <Clock className="w-8 h-8 text-yellow-600 mx-auto mb-4" />
                    <p className="text-gray-600">
                      Haga clic en "Analizar" para comenzar el análisis
                    </p>
                  </div>
                )}

                {contract.status === 'error' && (
                  <div className="text-center py-8">
                    <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-4" />
                    <p className="text-gray-600">
                      Error en el análisis. Intente nuevamente.
                    </p>
                  </div>
                )}

                {contract.status === 'completed' && clausesData?.results && (
                  <div className="space-y-4">
                    {clausesData.results.map((clause) => (
                      <ClauseCard key={clause.id} clause={clause} />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
} 