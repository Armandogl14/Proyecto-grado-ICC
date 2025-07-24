'use client'

import { useRouter } from 'next/navigation'
import { CreateContractForm } from "@/components/contracts/CreateContractForm"
import { Header } from "@/components/layout/Header"
import { ArrowLeft } from "lucide-react"

export default function NewContractPage() {
  const router = useRouter()

  const handleSuccess = (contractId: string) => {
    router.push(`/contracts/${contractId}`)
  }

  return (
    <>
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        <div className="mb-8">
            <button
                onClick={() => router.back()}
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4"
            >
                <ArrowLeft size={16} />
                Volver
            </button>
            <h1 className="text-3xl font-bold text-foreground">Nuevo Análisis</h1>
            <p className="text-muted-foreground mt-1">
                Completa los datos para analizar un nuevo contrato con nuestra IA.
            </p>
        </div>
        <CreateContractForm onSuccess={handleSuccess} />
      </main>
    </>
  )
} 