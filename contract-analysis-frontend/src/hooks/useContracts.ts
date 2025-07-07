'use client'

import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contractsApi, contractTypesApi, clausesApi } from '@/lib/api'
import type { ContractFilters, CreateContractData } from '@/types/contracts'
import { toast } from 'sonner'

// Hook para obtener contratos
export function useContracts(filters?: ContractFilters) {
  return useQuery({
    queryKey: ['contracts', filters],
    queryFn: () => contractsApi.getContracts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos
  })
}

// Hook para obtener un contrato específico
export function useContract(id: string) {
  return useQuery({
    queryKey: ['contract', id],
    queryFn: () => contractsApi.getContract(id),
    enabled: !!id && id !== 'undefined',
  })
}

// Hook para crear contrato
export function useCreateContract() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: contractsApi.createContract,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      toast.success('Contrato creado exitosamente')
      return data
    },
    onError: (error: any) => {
      console.error('Error creating contract:', error)
      toast.error('Error al crear contrato: ' + (error.response?.data?.detail || error.message))
    }
  })
}

// Hook para analizar contrato
export function useAnalyzeContract() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, forceReanalysis = false }: { id: string, forceReanalysis?: boolean }) => {
      console.log('Starting contract analysis for:', id, 'forceReanalysis:', forceReanalysis)
      return contractsApi.analyzeContract(id, forceReanalysis)
    },
    onSuccess: (data, variables) => {
      console.log('Analysis request successful:', data)
      queryClient.invalidateQueries({ queryKey: ['contract', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      toast.success('Análisis iniciado correctamente')
    },
    onError: (error: any) => {
      console.error('Error analyzing contract:', error)
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      toast.error('Error al iniciar análisis: ' + (error.response?.data?.detail || error.message))
    }
  })
}

// Hook para obtener tipos de contrato
export function useContractTypes() {
  return useQuery({
    queryKey: ['contract-types'],
    queryFn: contractTypesApi.getContractTypes,
    staleTime: 30 * 60 * 1000, // 30 minutos
  })
}

// Hook para obtener cláusulas de un contrato
export function useClausesByContract(contractId: string) {
  return useQuery({
    queryKey: ['clauses', contractId],
    queryFn: () => clausesApi.getClausesByContract(contractId),
    enabled: !!contractId && contractId !== 'undefined',
  })
}

// Hook para estadísticas del dashboard
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: contractsApi.getDashboardStats,
    staleTime: 2 * 60 * 1000, // 2 minutos
  })
}

// Hook para análisis en tiempo real
export function useRealTimeAnalysis(contractId: string) {
  const queryClient = useQueryClient()
  
  const query = useQuery({
    queryKey: ['contract', contractId],
    queryFn: () => contractsApi.getContract(contractId),
    enabled: !!contractId && contractId !== 'undefined',
    refetchInterval: (query) => {
      // Si el contrato está en análisis, refrescar cada 3 segundos
      if (query.state.data?.status === 'analyzing') {
        return 3000
      }
      // Si está completado o con error, no refrescar más
      return false
    },
  })

  // Efecto para manejar cambios de estado
  React.useEffect(() => {
    if (query.data?.status === 'completed') {
      queryClient.invalidateQueries({ queryKey: ['clauses', contractId] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      toast.success('¡Análisis completado!')
    } else if (query.data?.status === 'error') {
      console.error('Contract analysis failed for contract:', contractId, query.data)
      toast.error('Error en el análisis del contrato. Revisa la consola para más detalles.')
    }
  }, [query.data?.status, contractId, queryClient])

  return query
} 