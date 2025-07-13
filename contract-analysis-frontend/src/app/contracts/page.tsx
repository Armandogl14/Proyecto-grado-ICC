'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RiskIndicator } from "@/components/contracts/RiskIndicator"
import { useContracts, useContractTypes } from "@/hooks/useContracts"
import { formatDate } from "@/lib/utils"
import { 
  Plus, 
  Search, 
  Filter,
  Eye,
  FileClock,
  CheckCircle,
  AlertTriangle,
  Loader2,
  FileText,
  ArrowLeft,
  ListRestart
} from "lucide-react"
import Link from "next/link"
import { Contract } from "@/types/contracts"
import { Header } from '@/components/layout/Header'

export default function ContractsPage() {
  const [filters, setFilters] = useState({
    status: '',
    contract_type: undefined as number | undefined,
    search: '',
    page: 1,
    page_size: 10
  })

  const { data: contractsData, isLoading, refetch } = useContracts(filters)
  const { data: contractTypesData, isLoading: isLoadingTypes } = useContractTypes()

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }))
  }

  const handleClearFilters = () => {
    setFilters({
      status: '',
      contract_type: undefined,
      search: '',
      page: 1,
      page_size: 10
    })
  }
  
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'pending': return { icon: <FileClock className="w-4 h-4" />, text: 'Pendiente', color: 'text-amber-400' }
      case 'analyzing': return { icon: <Loader2 className="w-4 h-4 animate-spin" />, text: 'Analizando', color: 'text-purple-400' }
      case 'completed': return { icon: <CheckCircle className="w-4 h-4" />, text: 'Completado', color: 'text-green-400' }
      case 'error': return { icon: <AlertTriangle className="w-4 h-4" />, text: 'Error', color: 'text-red-400' }
      default: return { icon: <FileText className="w-4 h-4" />, text: 'Desconocido', color: 'text-slate-400' }
    }
  }

  return (
    <>
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
              <h1 className="text-3xl font-bold text-white">Mis Contratos</h1>
              <p className="text-slate-400 mt-1">
                Gestiona y revisa todos tus contratos analizados.
              </p>
          </div>
          <Link href="/contracts/new">
            <Button
                size="sm"
                className="group relative inline-flex h-9 items-center justify-center overflow-hidden rounded-md bg-gradient-to-r from-purple-500 to-pink-500 font-medium text-white transition-all duration-300 ease-in-out hover:from-purple-600 hover:to-pink-600">
                <span className="relative z-10 flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Nuevo Análisis
                </span>
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <Card className="bg-slate-800/80 border-slate-700/60 backdrop-blur-sm p-5 rounded-2xl mb-8">
          <div className="grid gap-4 md:grid-cols-4">
              <div className="relative">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Buscar por título..."
                  className="w-full pl-11 pr-4 py-2.5 bg-slate-900/70 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder:text-slate-500"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </div>

              <select
                className="w-full px-3 py-2.5 bg-slate-900/70 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <option value="">Todos los estados</option>
                <option value="pending">Pendiente</option>
                <option value="analyzing">Analizando</option>
                <option value="completed">Completado</option>
                <option value="error">Error</option>
              </select>

              <select
                className="w-full px-3 py-2.5 bg-slate-900/70 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
                value={filters.contract_type || ''}
                disabled={isLoadingTypes}
                onChange={(e) => handleFilterChange('contract_type', e.target.value ? parseInt(e.target.value) : undefined)}
              >
                <option value="">{isLoadingTypes ? 'Cargando...' : 'Todos los tipos'}</option>
                {contractTypesData?.results?.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>

              <Button
                variant="outline"
                onClick={handleClearFilters}
                className="border-slate-600 hover:bg-slate-800 h-full"
              >
                <ListRestart className="w-4 h-4 mr-2"/>
                Limpiar
              </Button>
          </div>
        </Card>

        {/* Contracts List */}
        <div className="space-y-4">
          {isLoading ? (
             [...Array(5)].map((_, i) => (
                <Card key={i} className="bg-slate-800/80 border-slate-700/60 p-5 rounded-2xl animate-pulse h-24"></Card>
             ))
          ) : contractsData?.results && contractsData.results.length > 0 ? (
            contractsData.results.map((contract: Contract) => {
              const status = getStatusInfo(contract.status)
              return (
              <Card key={contract.id} className="bg-slate-800/80 border-slate-700/60 backdrop-blur-sm rounded-2xl hover:border-slate-600 transition-colors">
                <CardContent className="p-4 md:p-5">
                  <div className="grid md:grid-cols-4 items-center gap-4">
                      {/* Title and Type */}
                      <div className="md:col-span-2">
                        <Link href={`/contracts/${contract.id}`}>
                            <h3 className="font-semibold text-white hover:text-purple-400 transition-colors line-clamp-1">
                                {contract.title}
                            </h3>
                        </Link>
                        <p className="text-sm text-slate-400">{contract.contract_type.name}</p>
                      </div>

                      {/* Status and Risk */}
                      <div className="flex items-center gap-4 md:gap-6">
                        <div className={`flex items-center gap-2 font-medium text-sm ${status.color}`}>
                            {status.icon}
                            <span>{status.text}</span>
                        </div>
                         {contract.status === 'completed' && (
                           <RiskIndicator 
                              riskScore={contract.risk_score} 
                              size="sm"
                           />
                         )}
                      </div>
                      
                      {/* Dates and Actions */}
                      <div className="flex items-center justify-end gap-4">
                         <div className="text-right hidden lg:block">
                            <p className="text-sm text-slate-300">Creado</p>
                            <p className="text-xs text-slate-500">{formatDate(contract.created_at)}</p>
                         </div>
                         <Link href={`/contracts/${contract.id}`}>
                           <Button size="icon" variant="ghost" className="text-slate-400 hover:bg-slate-700 hover:text-white">
                             <Eye className="w-5 h-5" />
                           </Button>
                         </Link>
                      </div>
                  </div>
                </CardContent>
              </Card>
            )})
          ) : (
             <Card className="bg-slate-800/80 border-slate-700/60 p-12 rounded-2xl text-center">
                <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white">No se encontraron contratos</h3>
                <p className="text-slate-400 mt-2 mb-6">Prueba a ajustar los filtros o crea tu primer contrato.</p>
                <Button onClick={handleClearFilters} variant="outline" className="border-slate-600">Limpiar filtros</Button>
            </Card>
          )}
        </div>

        {/* Pagination */}
        {contractsData && contractsData.count > filters.page_size && (
          <div className="flex justify-center items-center gap-4 mt-8">
              <Button
                variant="outline"
                disabled={!contractsData.previous}
                onClick={() => handleFilterChange('page', filters.page - 1)}
                className="border-slate-600"
              >
                Anterior
              </Button>
              <span className="text-sm text-slate-400">
                Página {filters.page} de {Math.ceil(contractsData.count / filters.page_size)}
              </span>
               <Button
                variant="outline"
                disabled={!contractsData.next}
                onClick={() => handleFilterChange('page', filters.page + 1)}
                className="border-slate-600"
              >
                Siguiente
              </Button>
          </div>
        )}
      </main>
    </>
  )
} 