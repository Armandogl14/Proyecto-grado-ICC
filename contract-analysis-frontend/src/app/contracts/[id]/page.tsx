'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RiskIndicator } from "@/components/contracts/RiskIndicator"
import { ClauseCard } from "@/components/contracts/ClauseCard"
import { Header } from "@/components/layout/Header"
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
  FileText,
  ShieldCheck,
  AlertOctagon,
  Clock,
  Loader2,
  CheckCircle,
  AlertTriangle,
  FileClock,
  BookText,
  ListOrdered
} from "lucide-react"
import Link from "next/link"
import React from "react" // Added missing import for React

// Nuevo componente de Pestañas (Tabs) que usa elementos nativos para no añadir dependencias
const Tabs = ({ children }: { children: React.ReactNode }) => <div className="flex border-b border-slate-700">{children}</div>
const Tab = ({ children, onClick, isActive }: { children: React.ReactNode; onClick: () => void; isActive: boolean; }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 -mb-px font-semibold border-b-2 transition-colors ${
      isActive
        ? 'border-purple-400 text-purple-300'
        : 'border-transparent text-slate-400 hover:text-white'
    }`}
  >
    {children}
  </button>
)

export default function ContractDetailPage({ params }: { params: { id: string } }) {
  const { data: contract, isLoading: isLoadingContract, error: contractError } = useRealTimeAnalysis(params.id)
  const { data: clausesData, isLoading: isLoadingClauses } = useClausesByContract(params.id)
  const analyzeContractMutation = useAnalyzeContract()

  const [activeTab, setActiveTab] = React.useState('summary')

  const handleAnalyze = () => analyzeContractMutation.mutate({ id: params.id })
  const handleReanalyze = () => analyzeContractMutation.mutate({ id: params.id, forceReanalysis: true })

  // --- Render Skeletons ---
  if (isLoadingContract) {
    return (
      <>
        <Header />
        <div className="container mx-auto p-4 md:p-8 animate-pulse">
            <div className="h-6 w-1/4 bg-slate-700 rounded mb-4"></div>
            <div className="h-10 w-1/2 bg-slate-700 rounded mb-2"></div>
            <div className="h-6 w-1/3 bg-slate-700 rounded mb-8"></div>
            <div className="h-40 bg-slate-800 rounded-2xl"></div>
        </div>
      </>
    )
  }

  // --- Render Error or Not Found ---
  if (contractError || !contract) {
    return (
      <>
        <Header />
        <div className="container mx-auto p-4 md:p-8 text-center">
            <AlertTriangle className="w-16 h-16 text-red-500/50 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-white mb-4">
            {contractError ? "Error al cargar el contrato" : "Contrato no encontrado"}
            </h1>
            <p className="text-slate-400 mb-6">
            {contractError?.message || "No pudimos encontrar el contrato que buscas."}
            </p>
            <Link href="/dashboard">
                <Button variant="outline" className="border-slate-600 hover:bg-slate-800">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Volver al Dashboard
                </Button>
            </Link>
        </div>
      </>
    )
  }

  const getStatusInfo = () => {
    switch (contract.status) {
      case 'pending': return { icon: <FileClock className="w-5 h-5 text-amber-400" />, text: 'Pendiente de análisis' }
      case 'analyzing': return { icon: <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />, text: 'Analizando...' }
      case 'completed': return { icon: <CheckCircle className="w-5 h-5 text-green-400" />, text: 'Análisis completado' }
      case 'error': return { icon: <AlertTriangle className="w-5 h-5 text-red-400" />, text: 'Error en análisis' }
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {/* --- Page Header --- */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
            <div>
                <Link href="/dashboard" className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors mb-2 text-sm">
                    <ArrowLeft size={16} />
                    Volver al Dashboard
                </Link>
                <h1 className="text-3xl font-bold text-white">{contract.title}</h1>
                <p className="text-slate-400 mt-1">{contract.contract_type.name}</p>
            </div>
            <div className="flex items-center gap-3">
                {contract.status === 'pending' && (
                    <Button onClick={handleAnalyze} disabled={analyzeContractMutation.isPending}>
                        <Play className="w-4 h-4 mr-2" /> Analizar Ahora
                    </Button>
                )}
                {contract.status === 'completed' && (
                    <Button onClick={handleReanalyze} variant="outline" className="border-slate-600 hover:bg-slate-800">
                        <RefreshCw className="w-4 h-4 mr-2" /> Re-analizar
                    </Button>
                )}
                 {contract.status === 'error' && (
                    <Button onClick={handleReanalyze} variant="destructive">
                        <RefreshCw className="w-4 h-4 mr-2" /> Intentar de nuevo
                    </Button>
                )}
            </div>
        </div>

        {/* --- Summary Card --- */}
        <Card className="bg-slate-800/80 border-slate-700/60 backdrop-blur-sm p-6 rounded-2xl mb-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center md:text-left">
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-slate-400 font-medium">Nivel de Riesgo</p>
                    <RiskIndicator riskScore={contract.risk_score} size="md" />
                </div>
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-slate-400 font-medium">Estado</p>
                    <div className="flex items-center gap-2 text-white font-semibold">
                        {getStatusInfo()?.icon} {getStatusInfo()?.text}
                    </div>
                </div>
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-slate-400 font-medium">Cláusulas Abusivas</p>
                    <p className="text-2xl font-bold text-red-400 flex items-center gap-2">
                        <AlertOctagon /> {contract.abusive_clauses_count || 0}
                    </p>
                </div>
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-slate-400 font-medium">Total de Cláusulas</p>
                     <p className="text-2xl font-bold text-white flex items-center gap-2">
                        <ListOrdered /> {contract.total_clauses || 0}
                    </p>
                </div>
            </div>
        </Card>

        {/* --- Tabs --- */}
        <div className="mb-6">
          <Tabs>
              <Tab onClick={() => setActiveTab('summary')} isActive={activeTab === 'summary'}>Resumen Ejecutivo</Tab>
              <Tab onClick={() => setActiveTab('clauses')} isActive={activeTab === 'clauses'}>Análisis de Cláusulas</Tab>
              <Tab onClick={() => setActiveTab('text')} isActive={activeTab === 'text'}>Texto Original</Tab>
          </Tabs>
        </div>

        {/* --- Tab Content --- */}
        <div>
            {activeTab === 'summary' && (
                <Card className="bg-slate-800/80 border-slate-700/60 p-6 rounded-2xl">
                    <h2 className="text-xl font-bold text-white mb-4">Resumen y Recomendaciones de la IA</h2>
                    <div className="prose prose-invert prose-p:text-slate-300 prose-strong:text-white">
                        <p>{contract.executive_summary || "El resumen ejecutivo aún no está disponible."}</p>
                        <p><strong>Recomendaciones:</strong> {contract.recommendations || "Las recomendaciones aún no están disponibles."}</p>
                    </div>
                </Card>
            )}

            {activeTab === 'clauses' && (
                <div className="space-y-4">
                    {isLoadingClauses ? (
                        <div className="text-center py-10 text-slate-400 flex items-center justify-center gap-2">
                            <Loader2 className="w-5 h-5 animate-spin" /> Cargando cláusulas...
                        </div>
                    ) : (
                        clausesData?.results?.map((clause) => (
                            <ClauseCard key={clause.id} clause={clause} />
                        ))
                    )}
                </div>
            )}
            
            {activeTab === 'text' && (
                <Card className="bg-slate-900/50 border-slate-700/60 rounded-2xl">
                    <CardContent className="p-6">
                        <pre className="text-sm whitespace-pre-wrap leading-relaxed text-slate-300 font-mono">
                            {contract.original_text}
                        </pre>
                    </CardContent>
                </Card>
            )}
        </div>
      </main>
    </>
  )
} 