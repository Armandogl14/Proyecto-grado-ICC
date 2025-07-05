'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useCreateContract, useContractTypes } from "@/hooks/useContracts"
import { Loader2, FileText, Upload } from "lucide-react"
import type { CreateContractData } from "@/types/contracts"
import pdfToText from 'react-pdftotext'

const contractSchema = z.object({
  title: z.string().min(1, 'El título es requerido'),
  original_text: z.string().min(50, 'El texto debe tener al menos 50 caracteres'),
  contract_type: z.number().min(1, 'Debe seleccionar un tipo de contrato')
})

type ContractFormData = z.infer<typeof contractSchema>

interface CreateContractFormProps {
  onSuccess?: (contractId: string) => void
  className?: string
}

export function CreateContractForm({ onSuccess, className = "" }: CreateContractFormProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isParsingPdf, setIsParsingPdf] = useState(false)
  const { data: contractTypesData, isLoading: isLoadingTypes, error: typesError } = useContractTypes()
  const createContractMutation = useCreateContract()

  // Tipos de contrato por defecto como fallback
  const defaultContractTypes = [
    { id: 1, name: 'Contrato de Alquiler', code: 'ALC', description: 'Contrato de alquiler de inmueble' },
    { id: 2, name: 'Contrato de Venta de Vehículo', code: 'VM', description: 'Contrato de venta de vehículo de motor' },
    { id: 3, name: 'Contrato de Hipoteca', code: 'HIP', description: 'Contrato de hipoteca convencional' },
    { id: 4, name: 'Contrato de Sociedad', code: 'CSP', description: 'Contrato de sociedad en participación' },
    { id: 5, name: 'Contrato de Venta de Arma', code: 'VTAF', description: 'Contrato de venta y traspaso de arma de fuego' },
    { id: 6, name: 'Rescisión de Contrato', code: 'RC', description: 'Modelo de rescisión de contrato' }
  ]

  // Usar datos del backend o fallback
  const contractTypes = contractTypesData?.results || defaultContractTypes

  // Debug: Log para verificar datos
  console.log('Contract types data:', contractTypesData)
  console.log('Loading types:', isLoadingTypes)
  console.log('Types error:', typesError)
  console.log('Using contract types:', contractTypes)
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue
  } = useForm<ContractFormData>({
    resolver: zodResolver(contractSchema)
  })

  const watchedText = watch('original_text', '')

  const onSubmit = async (data: ContractFormData) => {
    try {
      const newContract = await createContractMutation.mutateAsync(data)
      console.log('Contract created:', newContract) // Debug log
      reset()
      
      // Verificar que el ID existe antes de redirigir
      if (newContract?.id) {
        onSuccess?.(newContract.id)
      } else {
        console.error('Contract created but no ID returned:', newContract)
        // En caso de que no haya ID, redirigir al dashboard
        window.location.href = '/dashboard'
      }
    } catch (error) {
      console.error('Error creating contract:', error)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!watch('title')) {
      setValue('title', file.name.replace(/\.(txt|pdf)$/i, ''))
    }

    if (file.type === 'application/pdf') {
      setIsParsingPdf(true)
      try {
        const text = await pdfToText(file)
        setValue('original_text', text)
      } catch (error) {
        console.error("Failed to extract text from pdf", error)
        alert("No se pudo extraer el texto del PDF.")
      } finally {
        setIsParsingPdf(false)
      }
    } else if (file.type === 'text/plain') {
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        setValue('original_text', text)
      }
      reader.readAsText(file)
    } else {
      alert("Por favor, sube un archivo .txt o .pdf")
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Nuevo Contrato
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Título */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Título del Contrato
            </label>
            <input
              type="text"
              {...register('title')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ej: Contrato de Alquiler - Propiedad Centro"
            />
            {errors.title && (
              <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>
            )}
          </div>

          {/* Tipo de Contrato */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Tipo de Contrato
            </label>
            <select
              {...register('contract_type', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoadingTypes}
            >
              <option value="">
                {isLoadingTypes ? 'Cargando tipos...' : 'Seleccione un tipo'}
              </option>
              {contractTypes && contractTypes.length > 0 ? (
                contractTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))
              ) : (
                <option value="" disabled>
                  No hay tipos disponibles
                </option>
              )}
            </select>
            {errors.contract_type && (
              <p className="text-red-500 text-sm mt-1">{errors.contract_type.message}</p>
            )}
            {typesError && (
              <p className="text-red-500 text-sm mt-1">
                Error cargando tipos: {typesError.message}
              </p>
            )}
                         {/* Debug info */}
             {process.env.NODE_ENV === 'development' && (
               <div className="text-xs text-gray-500 mt-1">
                 Debug: {contractTypes?.length || 0} tipos cargados
                 {!contractTypesData?.results && ' (usando fallback)'}
               </div>
             )}
          </div>

          {/* Upload de archivo */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Cargar desde archivo
            </label>
            <div className="flex items-center gap-4">
              <input
                type="file"
                accept=".txt,.pdf"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                disabled={isParsingPdf}
              />
              <label
                htmlFor="file-upload"
                className={`flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md cursor-pointer hover:bg-gray-50 ${isParsingPdf ? 'bg-gray-200 cursor-not-allowed' : ''}`}
              >
                {isParsingPdf ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Procesando PDF...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Seleccionar archivo .txt o .pdf
                  </>
                )}
              </label>
            </div>
          </div>

          {/* Texto del contrato */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Texto del Contrato
            </label>
            <textarea
              {...register('original_text')}
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Pegue aquí el texto completo del contrato..."
            />
            <div className="flex justify-between items-center mt-2">
              {errors.original_text && (
                <p className="text-red-500 text-sm">{errors.original_text.message}</p>
              )}
              <p className="text-sm text-gray-500 ml-auto">
                {watchedText.length} caracteres
              </p>
            </div>
          </div>

          {/* Botones */}
          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={isSubmitting || createContractMutation.isPending}
              className="flex-1"
            >
              {isSubmitting || createContractMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creando...
                </>
              ) : (
                'Crear Contrato'
              )}
            </Button>
            
            <Button
              type="button"
              variant="outline"
              onClick={() => reset()}
              disabled={isSubmitting}
            >
              Limpiar
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
} 