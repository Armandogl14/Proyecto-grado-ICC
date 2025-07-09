import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from 'sonner'
import { QueryProvider } from "@/providers/QueryProvider";
import { AuthWrapper } from "@/components/auth/AuthWrapper";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Análisis de Contratos IA",
  description: "Análisis de contratos con IA para detectar cláusulas abusivas en República Dominicana",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${inter.className} bg-slate-900 text-slate-100`}>
        <QueryProvider>
          <AuthWrapper>
            {children}
          </AuthWrapper>
        </QueryProvider>
        <Toaster richColors theme="dark" />
      </body>
    </html>
  );
}
