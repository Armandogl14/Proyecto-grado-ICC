'use client'

import { CreateContractForm } from "@/components/contracts/CreateContractForm"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function NewContractPage() {
  const router = useRouter()

  const handleSuccess = (contractId: string) => {
    router.push(`/contracts/${contractId}`)
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link href="/dashboard">
          <Button variant="ghost" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver al Dashboard
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">
          Crear Nuevo Contrato
        </h1>
        <p className="text-gray-600 mt-2">
          Cargue o pegue el texto del contrato para iniciar el análisis de cláusulas abusivas
        </p>
      </div>

      {/* Form */}
      <CreateContractForm onSuccess={handleSuccess} />
    </div>
  )
} 