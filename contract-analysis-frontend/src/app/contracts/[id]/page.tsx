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
import type { Clause } from "@/types/contracts"
import { formatDate } from "@/lib/utils"
import { 
  ArrowLeft, 
  Play, 
  RefreshCw, 
  Download,
  Clock,
  CheckCircle,
  AlertTriangle,
  Loader2,
  Brain,
  Bot
} from "lucide-react"
import Link from "next/link"

export default function ContractDetailPage({ params }: { params: { id: string } }) {
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
        return <Clock className="w-5 h-5 text-amber-500" />
      case 'analyzing':
        return <Loader2 className="w-5 h-5 text-primary animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-emerald-500" />
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-destructive" />
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
    <div className="p-6 bg-background">
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
              <h1 className="text-3xl font-bold text-foreground">
                {contract.title}
              </h1>
              <p className="text-muted-foreground mt-1">
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
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Cláusulas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{contract.total_clauses}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {contract.valid_clauses} válidas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Cláusulas Abusivas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">
                  {contract.abusive_clauses_count}
                </div>
                <div className="flex items-center gap-4 mt-1">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Brain className="w-3 h-3" /> ML
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Bot className="w-3 h-3" /> GPT
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
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
                  <div className="text-2xl font-bold text-muted-foreground/50">N/A</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Fecha Análisis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm">
                  {contract.analyzed_at ? formatDate(contract.analyzed_at) : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Tiempo: {contract.processing_time?.toFixed(1)}s
                </p>
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
              <div className="max-h-96 overflow-y-auto rounded-md border bg-secondary/30 p-4">
                <pre className="text-sm whitespace-pre-wrap leading-relaxed text-foreground">
                  {contract.original_text}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          <div className="space-y-6">
            {/* Executive Summary */}
            {contract.status === 'completed' && (
              <Card>
                <CardHeader>
                  <CardTitle>Resumen Ejecutivo</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-muted-foreground">
                      {contract.executive_summary}
                    </p>
                    {contract.recommendations && (
                      <>
                        <h4 className="text-sm font-medium mt-4 mb-2">Recomendaciones:</h4>
                        <p className="text-muted-foreground">
                          {contract.recommendations}
                        </p>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Clauses Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Análisis de Cláusulas</CardTitle>
              </CardHeader>
              <CardContent>
                {contract.status === 'analyzing' && (
                  <div className="text-center py-8">
                    <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
                    <p className="text-muted-foreground">Analizando cláusulas...</p>
                  </div>
                )}

                {contract.status === 'pending' && (
                  <div className="text-center py-8">
                    <Clock className="w-8 h-8 text-amber-500 mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      Haga clic en "Analizar" para comenzar el análisis
                    </p>
                  </div>
                )}

                {contract.status === 'error' && (
                  <div className="text-center py-8">
                    <AlertTriangle className="w-8 h-8 text-destructive mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      Error en el análisis. Intente nuevamente.
                    </p>
                  </div>
                )}

                {contract.status === 'completed' && clausesData?.results && (
                  <div className="space-y-4">
                    {clausesData.results.map((clause: Clause) => (
                      <ClauseCard key={clause.id} clause={clause} />
                    ))}
                  </div>
                )}

                {!isLoadingClauses && !clausesData?.results.length && contract.status === 'completed' && (
                  <div className="text-center py-8">
                    <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      El análisis se completó, pero no se encontraron cláusulas para mostrar.
                    </p>
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