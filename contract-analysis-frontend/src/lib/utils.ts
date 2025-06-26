import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "2-digit", 
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(date))
}

export function formatRiskScore(score: number): string {
  return `${Math.round(score * 100)}%`
}

export function getRiskLevel(score: number) {
  if (score < 0.3) return { level: 'Bajo', color: 'green', variant: 'success' as const }
  if (score < 0.7) return { level: 'Medio', color: 'yellow', variant: 'warning' as const }
  return { level: 'Alto', color: 'red', variant: 'destructive' as const }
} 