'use client'

import { useState } from 'react'
import { useForm, SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useCreateContract, useContractTypes } from "@/hooks/useContracts"
import { Loader2, FileText, Upload, Sparkles, AlertCircle } from "lucide-react"
import pdfToText from 'react-pdftotext'
import type { CreateContractData } from '@/types/contracts'

// Esquema para la validación del formulario (datos de entrada)
const contractFormSchema = z.object({
  title: z.string().min(3, 'El título es requerido y debe tener al menos 3 caracteres.'),
  original_text: z.string().min(50, 'El texto debe tener al menos 50 caracteres.'),
  contract_type: z.string().min(1, 'Debe seleccionar un tipo de contrato')
})

// Esquema transformado que se usará para el submit (datos de salida)
const contractSubmitSchema = contractFormSchema.transform(data => ({
    ...data,
    contract_type: Number(data.contract_type)
}))

// Tipos inferidos de los esquemas
type ContractFormInput = z.infer<typeof contractFormSchema>
type ContractFormData = z.infer<typeof contractSubmitSchema>

interface CreateContractFormProps {
  onSuccess?: (contractId: string) => void
  className?: string
}

export function CreateContractForm({ onSuccess, className = "" }: CreateContractFormProps) {
  const [isParsing, setIsParsing] = useState(false)
  const { data: contractTypesData, isLoading: isLoadingTypes } = useContractTypes()
  const createContractMutation = useCreateContract()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue
  } = useForm<ContractFormInput>({
    resolver: zodResolver(contractFormSchema)
  })

  const watchedText = watch('original_text', '')

  const onSubmit: SubmitHandler<ContractFormInput> = async (data) => {
    try {
      // Validar y transformar los datos antes de enviarlos
      const validatedData = contractSubmitSchema.parse(data)
      const newContract = await createContractMutation.mutateAsync(validatedData)
      reset()
      if (newContract?.id) {
        onSuccess?.(newContract.id)
      } else {
        window.location.href = '/dashboard'
      }
    } catch (error) {
      console.error('Error al crear o validar contrato:', error)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsParsing(true)
    if (!watch('title')) {
      setValue('title', file.name.replace(/\.(txt|pdf)$/i, ''))
    }

    try {
      if (file.type === 'application/pdf') {
        const text = await pdfToText(file)
        setValue('original_text', text, { shouldValidate: true })
      } else if (file.type === 'text/plain') {
        const reader = new FileReader()
        reader.onload = (e) => {
          const text = e.target?.result as string
          setValue('original_text', text, { shouldValidate: true })
        }
        reader.readAsText(file)
      } else {
        alert("Por favor, sube un archivo .txt o .pdf")
      }
    } catch (error) {
        console.error("No se pudo extraer el texto del archivo.", error)
        alert("No se pudo extraer el texto del archivo.")
    } finally {
        setIsParsing(false)
    }
  }

  return (
    <Card className={`w-full max-w-3xl mx-auto bg-slate-800/80 border border-slate-700/60 rounded-2xl backdrop-blur-sm ${className}`}>
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-3">
          <FileText className="w-6 h-6 text-purple-400" />
          <span className="text-2xl font-bold">Analizar un Contrato</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          
          {/* Título */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium mb-2 text-slate-300">
              Título del Contrato
            </label>
            <input
              id="title"
              type="text"
              {...register('title')}
              className="w-full px-4 py-2 bg-slate-900/70 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder:text-slate-500"
              placeholder="Ej: Contrato de Alquiler de Apartamento"
            />
            {errors.title && <p className="text-red-400 text-sm mt-2 flex items-center gap-1.5"><AlertCircle size={14}/> {errors.title.message}</p>}
          </div>

          {/* Tipo de Contrato */}
          <div>
            <label htmlFor="contract_type" className="block text-sm font-medium mb-2 text-slate-300">
              Tipo de Contrato
            </label>
            <select
              id="contract_type"
              {...register('contract_type')}
              className="w-full px-3 py-2.5 bg-slate-900/70 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
              disabled={isLoadingTypes}
            >
              <option value="">
                {isLoadingTypes ? 'Cargando tipos...' : 'Seleccione un tipo'}
              </option>
              {contractTypesData?.results?.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
              ))}
            </select>
            {errors.contract_type && <p className="text-red-400 text-sm mt-2 flex items-center gap-1.5"><AlertCircle size={14}/> {errors.contract_type.message}</p>}
          </div>

          {/* Upload & Paste Area */}
          <div>
            <label className="block text-sm font-medium mb-2 text-slate-300">
              Texto del Contrato
            </label>
            <div className="p-4 bg-slate-900/70 border border-slate-700 rounded-lg">
                <textarea
                  {...register('original_text')}
                  rows={10}
                  className="w-full bg-transparent focus:outline-none text-slate-300 placeholder:text-slate-500 resize-none"
                  placeholder="Pega aquí el texto completo del contrato..."
                />
                <div className="flex justify-between items-center mt-3 pt-3 border-t border-slate-700">
                    <div>
                        <input
                            type="file"
                            accept=".txt,.pdf"
                            onChange={handleFileUpload}
                            className="hidden"
                            id="file-upload"
                            disabled={isParsing}
                        />
                        <label
                            htmlFor="file-upload"
                            className={`flex items-center gap-2 px-4 py-2 border border-slate-600 rounded-md cursor-pointer transition-colors ${isParsing ? 'bg-slate-700 cursor-wait' : 'hover:bg-slate-700/50'}`}
                        >
                            {isParsing ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                                    Procesando...
                                </>
                            ) : (
                                <>
                                    <Upload className="w-4 h-4 text-purple-400" />
                                    Cargar archivo
                                </>
                            )}
                        </label>
                    </div>
                    <div className="flex flex-col items-end">
                        {errors.original_text && (
                            <p className="text-red-400 text-xs flex items-center gap-1">{errors.original_text.message}</p>
                        )}
                        <p className="text-xs text-slate-500 ml-auto mt-1">
                            {watchedText.length} caracteres
                        </p>
                    </div>
                </div>
            </div>
          </div>
          
          {/* Submit Button */}
          <div className="pt-4">
           <Button
              type="submit"
              size="lg"
              disabled={isSubmitting || createContractMutation.isPending || isParsing}
              className="w-full group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-gradient-to-r from-purple-500 to-pink-500 font-medium text-white transition-all duration-300 ease-in-out hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting || createContractMutation.isPending ? (
                <span className="relative z-10 flex items-center gap-2">
                   <Loader2 className="w-5 h-5 animate-spin" />
                   Creando Contrato...
                </span>
              ) : (
                 <span className="relative z-10 flex items-center gap-2">
                   <Sparkles className="w-5 h-5 transition-transform duration-300 group-hover:rotate-12" />
                   Analizar Contrato
                </span>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
} 