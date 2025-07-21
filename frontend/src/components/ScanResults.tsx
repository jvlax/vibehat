'use client'

import { ScanResult, Dependency } from '@/types'
import { formatDistanceToNow } from 'date-fns'

interface ScanResultsProps {
  results: ScanResult[]
  loading: boolean
}

export function ScanResults({ results, loading }: ScanResultsProps) {
  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6 text-center">
        <p className="text-gray-500">No scan results yet. Start by scanning a repository above.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-medium text-gray-900">Scan Results</h2>
      
      {results.map((result) => (
        <div key={result.id} className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                {result.repository_owner}/{result.repository_name}
              </h3>
              <p className="text-sm text-gray-500">
                {formatDistanceToNow(new Date(result.created_at), { addSuffix: true })}
              </p>
            </div>
            
            <div className="flex space-x-4 text-sm">
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {result.total_dependencies}
                </div>
                <div className="text-gray-500">Total Deps</div>
              </div>
              <div className="text-center">
                <div className={`text-lg font-semibold ${
                  result.missing_dependencies > 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {result.missing_dependencies}
                </div>
                <div className="text-gray-500">Missing</div>
              </div>
            </div>
          </div>

          {result.missing_dependencies > 0 && (
            <div>
              <h4 className="text-md font-medium text-red-600 mb-2">
                Missing Dependencies (Potential Exploits)
              </h4>
              <div className="grid gap-2">
                {result.missing_packages.map((dep, index) => (
                  <MissingPackageCard key={index} dependency={dep} />
                ))}
              </div>
            </div>
          )}

          {result.missing_dependencies === 0 && (
            <div className="text-green-600 font-medium">
              ✅ All dependencies exist in their respective registries
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

function MissingPackageCard({ dependency }: { dependency: Dependency }) {
  const getEcosystemColor = (ecosystem: string) => {
    const colors = {
      npm: 'bg-red-100 text-red-800',
      pypi: 'bg-blue-100 text-blue-800',
      cargo: 'bg-orange-100 text-orange-800',
      go: 'bg-cyan-100 text-cyan-800',
    }
    return colors[ecosystem as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="border border-red-200 rounded-lg p-3 bg-red-50">
      <div className="flex justify-between items-start">
        <div>
          <div className="font-medium text-gray-900">{dependency.name}</div>
          <div className="text-sm text-gray-600">
            {dependency.version && `Version: ${dependency.version}`}
          </div>
          <div className="text-sm text-gray-500">
            Found in: {dependency.file_path}
          </div>
        </div>
        <span className={`inline-flex px-2 py-1 text-xs rounded-full ${getEcosystemColor(dependency.ecosystem)}`}>
          {dependency.ecosystem}
        </span>
      </div>
      
      <div className="mt-2 text-sm text-red-600">
        ⚠️ This package doesn't exist and could be exploited
      </div>
    </div>
  )
} 