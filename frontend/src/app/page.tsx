'use client'

import { useState, useEffect } from 'react'
import { ScanForm } from '@/components/ScanForm'
import { ScanResults } from '@/components/ScanResults'
import { PublishedPackagesDashboard } from '@/components/PublishedPackagesDashboard'
import { ScanResult, DashboardStats } from '@/types'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'scan' | 'dashboard'>('dashboard')
  const [scanResults, setScanResults] = useState<ScanResult[]>([])
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchDashboardData = async () => {
    try {
      const [scansResponse] = await Promise.all([
        axios.get(`${API_URL}/scans`)
      ])
      
      const scans = scansResponse.data || []
      const publishedPackages = scans
        .filter((scan: ScanResult) => scan.published_packages && scan.published_packages.length > 0)
        .flatMap((scan: ScanResult) => scan.published_packages?.map(pkg => ({
          ...pkg,
          repository: `${scan.repository_owner}/${scan.repository_name}`,
          repository_url: scan.repository_url
        })) || [])

      setDashboardStats({
        total_scans: scans.length,
        total_published_packages: publishedPackages.length,
        vulnerable_repos: scans.filter((scan: ScanResult) => scan.missing_dependencies > 0).length,
        recent_scans: scans.slice(0, 5),
        recent_published: publishedPackages.slice(0, 10)
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    }
  }

  const fetchScanResults = async () => {
    try {
      const response = await axios.get(`${API_URL}/scans`)
      setScanResults(response.data || [])
    } catch (error) {
      console.error('Error fetching scan results:', error)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    fetchScanResults()
  }, [])

  const handleScanComplete = (newResult: ScanResult) => {
    setScanResults(prev => [newResult, ...prev])
    fetchDashboardData() // Refresh dashboard after new scan
  }

  return (
    <div className="min-h-screen relative">
      {/* Background Image */}
      <div className="fixed inset-0 z-0">
        <img 
          src="/vibehat-hero.webp" 
          alt="VibeHat Security"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/60"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="text-center py-16">
          <h1 className="text-6xl font-bold text-white mb-4">
            VibeHat
          </h1>
          <p className="text-xl text-gray-200">
            Dependency Confusion Scanner
          </p>
        </div>

        {/* Navigation */}
        <div className="max-w-4xl mx-auto px-6 mb-12">
          <div className="flex justify-center">
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-1 border border-white/20">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-8 py-3 rounded-md font-medium transition-all ${
                  activeTab === 'dashboard'
                    ? 'bg-white/20 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('scan')}
                className={`px-8 py-3 rounded-md font-medium transition-all ${
                  activeTab === 'scan'
                    ? 'bg-white/20 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Scan Repository
              </button>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="max-w-6xl mx-auto px-6 pb-24">
          {activeTab === 'dashboard' && (
            <PublishedPackagesDashboard stats={dashboardStats} />
          )}
          
          {activeTab === 'scan' && (
            <ScanForm onScanComplete={handleScanComplete} setLoading={setLoading} />
          )}
        </div>
      </div>
    </div>
  )
} 