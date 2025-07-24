'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RiskIndicator } from "@/components/contracts/RiskIndicator"
import { ClauseCard } from "@/components/contracts/ClauseCard"
import { Header } from "@/components/layout/Header"
import { 
  useRealTimeAnalysis, 
  useAnalyzeContract, 
  useClausesByContract,
  useDeleteContract // Importar el nuevo hook
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
  ListOrdered,
  Trash2 // Importar el icono de la papelera
} from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation" // Importar useRouter
import React from "react" // Added missing import for React

// Nuevo componente de Pestañas (Tabs) que usa elementos nativos para no añadir dependencias
const Tabs = ({ children }: { children: React.ReactNode }) => <div className="flex border-b border-border">{children}</div>
const Tab = ({ children, onClick, isActive }: { children: React.ReactNode; onClick: () => void; isActive: boolean; }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 -mb-px font-semibold border-b-2 transition-colors ${
      isActive
        ? 'border-primary text-primary'
        : 'border-transparent text-muted-foreground hover:text-foreground'
    }`}
  >
    {children}
  </button>
)

export default function ContractDetailPage({ params }: { params: { id: string } }) {
  const { data: contract, isLoading: isLoadingContract, error: contractError } = useRealTimeAnalysis(params.id)
  const { data: clausesData, isLoading: isLoadingClauses } = useClausesByContract(params.id)
  const analyzeContractMutation = useAnalyzeContract()
  const deleteContractMutation = useDeleteContract() // Usar el nuevo hook
  const router = useRouter() // Inicializar router

  const [activeTab, setActiveTab] = React.useState('summary')

  const handleAnalyze = () => analyzeContractMutation.mutate({ id: params.id })
  const handleReanalyze = () => analyzeContractMutation.mutate({ id: params.id, forceReanalysis: true })

  const handleDelete = () => {
    if (window.confirm("¿Estás seguro de que deseas eliminar este contrato? Esta acción es irreversible.")) {
      deleteContractMutation.mutate(params.id, {
        onSuccess: () => {
          router.push('/dashboard') // Redirigir al dashboard después de eliminar
        }
      })
    }
  }

  // --- Render Skeletons ---
  if (isLoadingContract) {
    return (
      <>
        <Header />
        <div className="container mx-auto p-4 md:p-8 animate-pulse">
            <div className="h-6 w-1/4 bg-muted/50 rounded mb-4"></div>
            <div className="h-10 w-1/2 bg-muted/50 rounded mb-2"></div>
            <div className="h-6 w-1/3 bg-muted/50 rounded mb-8"></div>
            <div className="h-40 bg-card/80 rounded-2xl"></div>
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
            <AlertTriangle className="w-16 h-16 text-destructive/50 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-foreground mb-4">
            {contractError ? "Error al cargar el contrato" : "Contrato no encontrado"}
            </h1>
            <p className="text-muted-foreground mb-6">
            {contractError?.message || "No pudimos encontrar el contrato que buscas."}
            </p>
            <Link href="/dashboard">
                <Button variant="outline" className="border-border hover:bg-secondary">
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
      case 'pending': return { icon: <FileClock className="w-5 h-5 text-yellow-500" />, text: 'Pendiente de análisis' }
      case 'analyzing': return { icon: <Loader2 className="w-5 h-5 text-primary animate-spin" />, text: 'Analizando...' }
      case 'completed': return { icon: <CheckCircle className="w-5 h-5 text-green-500" />, text: 'Análisis completado' }
      case 'error': return { icon: <AlertTriangle className="w-5 h-5 text-destructive" />, text: 'Error en análisis' }
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {/* --- Page Header --- */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
            <div>
                <Link href="/dashboard" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-2 text-sm">
                    <ArrowLeft size={16} />
                    Volver al Dashboard
                </Link>
                <h1 className="text-3xl font-bold text-foreground">{contract.title}</h1>
                <p className="text-muted-foreground mt-1">{contract.contract_type.name}</p>
            </div>
            <div className="flex items-center gap-3">
                {contract.status === 'pending' && (
                    <Button onClick={handleAnalyze} disabled={analyzeContractMutation.isPending}>
                        <Play className="w-4 h-4 mr-2" /> Analizar Ahora
                    </Button>
                )}
                {contract.status === 'completed' && (
                    <Button onClick={handleReanalyze} variant="outline" className="border-border hover:bg-secondary">
                        <RefreshCw className="w-4 h-4 mr-2" /> Re-analizar
                    </Button>
                )}
                 {contract.status === 'error' && (
                    <Button onClick={handleReanalyze} variant="destructive">
                        <RefreshCw className="w-4 h-4 mr-2" /> Intentar de nuevo
                    </Button>
                )}
                {/* Botón de Eliminar */}
                <Button 
                    onClick={handleDelete}
                    variant="destructive" 
                    size="icon" 
                    disabled={deleteContractMutation.isPending}
                    className="bg-destructive/10 text-destructive hover:bg-destructive/20 hover:text-destructive"
                    title="Eliminar Contrato"
                >
                    {deleteContractMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                </Button>
            </div>
        </div>

        {/* --- Summary Card --- */}
        <Card className="bg-card/80 border-border/60 backdrop-blur-sm p-6 rounded-2xl mb-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center md:text-left">
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-muted-foreground font-medium">Nivel de Riesgo</p>
                    <RiskIndicator riskScore={contract.risk_score} size="md" />
                </div>
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-muted-foreground font-medium">Estado</p>
                    <div className="flex items-center gap-2 text-foreground font-semibold">
                        {getStatusInfo()?.icon} {getStatusInfo()?.text}
                    </div>
                </div>
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-muted-foreground font-medium">Cláusulas Abusivas</p>
                    <p className="text-2xl font-bold text-destructive flex items-center gap-2">
                        <AlertOctagon /> {contract.abusive_clauses_count || 0}
                    </p>
                </div>
                <div className="flex flex-col items-center md:items-start gap-1">
                    <p className="text-sm text-muted-foreground font-medium">Total de Cláusulas</p>
                     <p className="text-2xl font-bold text-foreground flex items-center gap-2">
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
                <Card className="bg-card/80 border-border/60 p-6 rounded-2xl">
                    <h2 className="text-xl font-bold text-foreground mb-4">Resumen y Recomendaciones de la IA</h2>
                    <div className="prose prose-p:text-muted-foreground prose-strong:text-foreground">
                        <p>{contract.executive_summary || "El resumen ejecutivo aún no está disponible."}</p>
                        <p><strong>Recomendaciones:</strong> {contract.recommendations || "Las recomendaciones aún no están disponibles."}</p>
                    </div>
                </Card>
            )}

            {activeTab === 'clauses' && (
                <div className="space-y-4">
                    {isLoadingClauses ? (
                        <div className="text-center py-10 text-muted-foreground flex items-center justify-center gap-2">
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
                <Card className="bg-background/50 border-border/60 rounded-2xl">
                    <CardContent className="p-6">
                        <pre className="text-sm whitespace-pre-wrap leading-relaxed text-muted-foreground font-mono">
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