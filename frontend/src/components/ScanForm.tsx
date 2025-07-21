'use client'

import { useState } from 'react'
import { ScanResult } from '@/types'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ScanFormProps {
  onScanComplete: (result: ScanResult) => void
  setLoading: (loading: boolean) => void
}

export function ScanForm({ onScanComplete, setLoading }: ScanFormProps) {
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)
  const [scanning, setScanning] = useState(false)
  const [showAllPackages, setShowAllPackages] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!repositoryUrl.trim()) {
      setError('Please enter a repository URL')
      return
    }

    if (!repositoryUrl.includes('github.com')) {
      setError('Please enter a valid GitHub repository URL')
      return
    }

    setScanning(true)
    setError('')
    setResult(null)

    try {
      const response = await axios.post(`${API_URL}/scan/repository`, {
        repository_url: repositoryUrl
      })
      
      const scanResult = response.data
      setResult(scanResult)
      onScanComplete(scanResult)
      
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error scanning repository')
    } finally {
      setScanning(false)
    }
  }

  const packagesToShow = showAllPackages 
    ? result?.missing_packages || []
    : (result?.missing_packages || []).slice(0, 10)

  const hasMorePackages = result?.missing_packages && result.missing_packages.length > 10

  return (
    <div className="space-y-8">
      {/* Scan Form */}
      <div className="bg-black/40 backdrop-blur-sm rounded-lg p-8 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-8 text-center">
          Scan Repository
        </h2>
        
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <input
              type="url"
              value={repositoryUrl}
              onChange={(e) => setRepositoryUrl(e.target.value)}
              placeholder="https://github.com/owner/repository"
              className="w-full bg-black/30 border border-white/20 rounded-lg px-4 py-4 pr-24 text-white placeholder-gray-400 focus:outline-none focus:border-white/40 transition-all"
              disabled={scanning}
            />
            <button
              type="submit"
              disabled={scanning || !repositoryUrl.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white text-black px-4 py-2 rounded-md font-medium hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {scanning ? 'Scanning...' : 'Scan'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
            <div className="text-red-300 text-sm">{error}</div>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-black/40 backdrop-blur-sm rounded-lg p-8 border border-white/20">
          {result.missing_dependencies === 0 ? (
            <div className="text-center">
              <div className="text-green-400 text-6xl mb-4">✓</div>
              <div className="text-white text-xl font-medium mb-2">Repository is secure</div>
              <div className="text-gray-400">No missing dependencies found</div>
            </div>
          ) : (
            <div className="text-center">
              <div className="text-white text-3xl font-bold mb-2">
                {result.missing_dependencies} packages published
              </div>
              <div className="text-gray-300 mb-6">
                Found and secured missing dependencies
              </div>
              
              {/* Show published packages */}
              <div className="space-y-3 mt-6">
                {packagesToShow.map((pkg: any, index: number) => (
                  <div key={index} className="bg-black/20 rounded p-3 border border-white/10 text-left">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="text-white font-mono">{pkg.name}</div>
                        <div className="text-gray-400 text-sm">{pkg.file_path}</div>
                        <div className="text-gray-500 text-xs">{pkg.ecosystem}</div>
                      </div>
                      <div className="text-blue-400 text-sm">Published</div>
                    </div>
                  </div>
                ))}
                
                {hasMorePackages && !showAllPackages && (
                  <button
                    onClick={() => setShowAllPackages(true)}
                    className="text-gray-400 hover:text-white text-sm mt-4 transition-colors"
                  >
                    Show all {result.missing_dependencies} packages...
                  </button>
                )}
                
                {hasMorePackages && showAllPackages && (
                  <button
                    onClick={() => setShowAllPackages(false)}
                    className="text-gray-400 hover:text-white text-sm mt-4 transition-colors"
                  >
                    Show less
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 