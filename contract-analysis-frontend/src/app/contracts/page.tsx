'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RiskIndicator } from "@/components/contracts/RiskIndicator"
import { useContracts, useContractTypes } from "@/hooks/useContracts"
import { formatDate } from "@/lib/utils"
import { 
  Plus, 
  Search, 
  Filter,
  Eye,
  Clock,
  CheckCircle,
  AlertTriangle,
  Loader2,
  FileText,
  ArrowLeft
} from "lucide-react"
import Link from "next/link"
import { Contract } from "@/types/contracts"

export default function ContractsPage() {
  const [filters, setFilters] = useState({
    status: '',
    contract_type: undefined as number | undefined,
    search: '',
    page: 1,
    page_size: 10
  })

  const { data: contractsData, isLoading } = useContracts(filters)
  const { data: contractTypesData } = useContractTypes()

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-amber-500" />
      case 'analyzing':
        return <Loader2 className="w-4 h-4 text-primary animate-spin" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-destructive" />
      default:
        return <FileText className="w-4 h-4 text-muted-foreground" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pendiente'
      case 'analyzing':
        return 'Analizando'
      case 'completed':
        return 'Completado'
      case 'error':
        return 'Error'
      default:
        return 'Desconocido'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-amber-100 text-amber-800 border-amber-200'
      case 'analyzing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'completed':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200'
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid gap-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-background">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Contratos
              </h1>
              <p className="text-muted-foreground mt-1">
                Gestiona y analiza tus contratos
              </p>
            </div>
          </div>

          <Link href="/contracts/new">
            <Button className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Nuevo Contrato
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="w-5 h-5" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Buscar
                </label>
                <div className="relative mt-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Buscar contratos..."
                    className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background"
                    value={filters.search}
                    onChange={(e) => setFilters({...filters, search: e.target.value, page: 1})}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Estado
                </label>
                <select
                  className="w-full mt-1 px-3 py-2 border border-input rounded-md bg-background"
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value, page: 1})}
                  aria-label="Filtrar por estado"
                >
                  <option value="">Todos los estados</option>
                  <option value="pending">Pendiente</option>
                  <option value="analyzing">Analizando</option>
                  <option value="completed">Completado</option>
                  <option value="error">Error</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Tipo de Contrato
                </label>
                <select
                  className="w-full mt-1 px-3 py-2 border border-input rounded-md bg-background"
                  value={filters.contract_type || ''}
                  onChange={(e) => setFilters({...filters, contract_type: e.target.value ? parseInt(e.target.value) : undefined, page: 1})}
                  aria-label="Filtrar por tipo de contrato"
                >
                  <option value="">Todos los tipos</option>
                  {contractTypesData?.results?.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <Button
                  variant="outline"
                  onClick={() => setFilters({
                    status: '',
                    contract_type: undefined,
                    search: '',
                    page: 1,
                    page_size: 10
                  })}
                  className="w-full"
                >
                  Limpiar Filtros
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contracts List */}
        <div className="space-y-4">
          {contractsData?.results && contractsData.results.length > 0 ? (
            contractsData.results.map((contract: Contract) => (
              <Card key={contract.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-foreground">
                          {contract.title}
                        </h3>
                        <Badge className={`flex items-center gap-1 ${getStatusColor(contract.status)}`}>
                          {getStatusIcon(contract.status)}
                          {getStatusText(contract.status)}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                        <span>{contract.contract_type.name}</span>
                        <span>•</span>
                        <span>Creado el {formatDate(contract.created_at)}</span>
                        {contract.analyzed_at && (
                          <>
                            <span>•</span>
                            <span>Analizado el {formatDate(contract.analyzed_at)}</span>
                          </>
                        )}
                      </div>

                      {contract.status === 'completed' && (
                        <div className="flex items-center gap-6 text-sm">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-muted-foreground" />
                            <span>{contract.total_clauses} cláusulas</span>
                          </div>
                          
                          {contract.abusive_clauses_count > 0 && (
                            <div className="flex items-center gap-2">
                              <AlertTriangle className="w-4 h-4 text-destructive" />
                              <span className="text-destructive">
                                {contract.abusive_clauses_count} abusivas
                              </span>
                            </div>
                          )}

                          {contract.risk_score !== undefined && (
                            <RiskIndicator 
                              riskScore={contract.risk_score} 
                              showPercentage={true}
                            />
                          )}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <Link href={`/contracts/${contract.id}`}>
                        <Button size="sm" variant="outline">
                          <Eye className="w-4 h-4 mr-2" />
                          Ver Detalles
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <FileText className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  No hay contratos
                </h3>
                <p className="text-muted-foreground mb-6">
                  {filters.search || filters.status || filters.contract_type
                    ? "No se encontraron contratos que coincidan con los filtros."
                    : "Aún no has creado ningún contrato."}
                </p>
                <Link href="/contracts/new">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Crear Primer Contrato
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Pagination */}
        {contractsData && contractsData.count > filters.page_size && (
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Mostrando {((filters.page - 1) * filters.page_size) + 1} a{' '}
              {Math.min(filters.page * filters.page_size, contractsData.count)} de{' '}
              {contractsData.count} contratos
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={!contractsData.previous}
                onClick={() => setFilters({...filters, page: filters.page - 1})}
              >
                Anterior
              </Button>
              
              <span className="text-sm text-muted-foreground px-3">
                Página {filters.page}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                disabled={!contractsData.next}
                onClick={() => setFilters({...filters, page: filters.page + 1})}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 