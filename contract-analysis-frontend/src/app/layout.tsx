import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/providers/QueryProvider";
import { AuthWrapper } from "@/components/auth/AuthWrapper";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "Análisis de Contratos - Sistema de Detección de Cláusulas Abusivas",
  description: "Sistema inteligente para el análisis de contratos y detección de cláusulas abusivas usando Machine Learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50 antialiased">
        <QueryProvider>
          <AuthWrapper>
            {children}
          </AuthWrapper>
          <Toaster position="top-right" richColors />
        </QueryProvider>
      </body>
    </html>
  );
}
