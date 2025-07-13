import React from 'react'
import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query'
import { contractsApi, contractTypesApi, clausesApi } from '../lib/api'
import type { ContractFilters, CreateContractData } from '../types/contracts'
import { useIonToast } from '@ionic/react'

// Hook para obtener contratos
export function useContracts(filters?: ContractFilters) {
  return useQuery({
    queryKey: ['contracts', filters],
    queryFn: () => contractsApi.getContracts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos
  })
}

// Hook para obtener contratos con paginación infinita
export function useInfiniteContracts(filters: Omit<ContractFilters, 'page'> = {}) {
  return useInfiniteQuery({
    queryKey: ['contracts', 'infinite', filters],
    queryFn: ({ pageParam = 1 }) =>
      contractsApi.getContracts({ ...filters, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.next) {
        const url = new URL(lastPage.next);
        const nextPage = url.searchParams.get('page');
        return nextPage ? parseInt(nextPage, 10) : undefined;
      }
      return undefined;
    },
  });
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
  const [presentToast] = useIonToast()

  return useMutation({
    mutationFn: contractsApi.createContract,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      presentToast({
        message: 'Contrato creado exitosamente',
        duration: 2000,
        color: 'success',
      })
      return data
    },
    onError: (error: any) => {
      console.error('Error creating contract:', error)
      presentToast({
        message: 'Error al crear contrato: ' + (error.response?.data?.detail || error.message),
        duration: 3000,
        color: 'danger',
      })
    }
  })
}

// Hook para analizar contrato
export function useAnalyzeContract() {
  const queryClient = useQueryClient()
  const [presentToast] = useIonToast()

  return useMutation({
    mutationFn: ({ id, forceReanalysis = false }: { id: string, forceReanalysis?: boolean }) => {
      return contractsApi.analyzeContract(id, forceReanalysis)
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contract', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      presentToast({
        message: 'Análisis iniciado correctamente',
        duration: 2000,
        color: 'success',
      })
    },
    onError: (error: any) => {
      console.error('Error analyzing contract:', error)
      presentToast({
        message: 'Error al iniciar análisis: ' + (error.response?.data?.detail || error.message),
        duration: 3000,
        color: 'danger',
      })
    }
  })
}

// Hook para eliminar un contrato
export function useDeleteContract() {
  const queryClient = useQueryClient()
  const [presentToast] = useIonToast()

  return useMutation({
    mutationFn: contractsApi.deleteContract,
    onSuccess: () => {
      presentToast({
        message: 'Contrato eliminado correctamente',
        duration: 2000,
        color: 'success',
      })
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
    },
    onError: (error: any) => {
      console.error('Error deleting contract:', error)
      presentToast({
        message: 'Error al eliminar el contrato: ' + (error.response?.data?.detail || error.message),
        duration: 3000,
        color: 'danger',
      })
    },
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
  const [presentToast] = useIonToast()

  const query = useQuery({
    queryKey: ['contract', contractId],
    queryFn: () => contractsApi.getContract(contractId),
    enabled: !!contractId && contractId !== 'undefined',
    refetchInterval: (query) => {
      if (query.state.data?.status === 'analyzing') {
        return 3000
      }
      return false
    },
  })

  React.useEffect(() => {
    if (query.data?.status === 'completed') {
      queryClient.invalidateQueries({ queryKey: ['clauses', contractId] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
      presentToast({
        message: '¡Análisis completado!',
        duration: 2000,
        color: 'success',
      })
    } else if (query.data?.status === 'error') {
      console.error('Contract analysis failed for contract:', contractId, query.data)
      presentToast({
        message: 'Error en el análisis del contrato.',
        duration: 3000,
        color: 'danger',
      })
    }
  }, [query.data?.status, contractId, queryClient, presentToast])

  return query
} 