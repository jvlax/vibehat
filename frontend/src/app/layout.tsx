import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'VibeHat - Dependency Confusion Scanner',
  description: 'Scan repositories for missing dependencies and prevent supply chain attacks',
  keywords: ['security', 'dependency', 'scanner', 'supply chain', 'vulnerability'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} dark bg-black text-white min-h-screen`}>
        {children}
      </body>
    </html>
  )
} 