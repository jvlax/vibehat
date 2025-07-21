'use client'

import { ScanResult, Dependency } from '@/types'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

interface ScanResultsProps {
  results: ScanResult[]
  loading: boolean
}

type FilterType = 'all' | 'package-files' | 'source-code'

export function ScanResults({ results, loading }: ScanResultsProps) {
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set())
  const [filter, setFilter] = useState<FilterType>('all')

  const toggleExpanded = (resultId: number) => {
    const newExpanded = new Set(expandedResults)
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId)
    } else {
      newExpanded.add(resultId)
    }
    setExpandedResults(newExpanded)
  }

  const filterDependencies = (dependencies: Dependency[], filterType: FilterType) => {
    if (filterType === 'all') return dependencies
    
    if (filterType === 'package-files') {
      return dependencies.filter(dep => 
        dep.file_path.endsWith('package.json') || 
        dep.file_path.endsWith('requirements.txt') ||
        dep.file_path.endsWith('Cargo.toml') ||
        dep.file_path.endsWith('go.mod') ||
        dep.file_path.endsWith('composer.json') ||
        dep.file_path.endsWith('Gemfile')
      )
    }
    
    if (filterType === 'source-code') {
      return dependencies.filter(dep => 
        dep.file_path.endsWith('.js') || 
        dep.file_path.endsWith('.jsx') ||
        dep.file_path.endsWith('.ts') ||
        dep.file_path.endsWith('.tsx') ||
        dep.file_path.endsWith('.py') ||
        dep.file_path.endsWith('.go') ||
        dep.file_path.endsWith('.rs') ||
        dep.file_path.endsWith('.php') ||
        dep.file_path.endsWith('.rb')
      )
    }
    
    return dependencies
  }

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
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium text-gray-900">Scan Results</h2>
        
        {/* Filter Controls */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 text-sm rounded-md ${
              filter === 'all' 
                ? 'bg-blue-100 text-blue-700 border border-blue-300' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All ({results[0]?.missing_dependencies || 0})
          </button>
          <button
            onClick={() => setFilter('package-files')}
            className={`px-3 py-1 text-sm rounded-md ${
              filter === 'package-files' 
                ? 'bg-orange-100 text-orange-700 border border-orange-300' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Package Files ({results[0] ? filterDependencies(results[0].missing_packages, 'package-files').length : 0})
          </button>
          <button
            onClick={() => setFilter('source-code')}
            className={`px-3 py-1 text-sm rounded-md ${
              filter === 'source-code' 
                ? 'bg-green-100 text-green-700 border border-green-300' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Source Code ({results[0] ? filterDependencies(results[0].missing_packages, 'source-code').length : 0})
          </button>
        </div>
      </div>
      
      {results.map((result) => {
        const isExpanded = expandedResults.has(result.id)
        const filteredPackages = filterDependencies(result.missing_packages, filter)
        const packageFileDeps = filterDependencies(result.missing_packages, 'package-files')
        const sourceCodeDeps = filterDependencies(result.missing_packages, 'source-code')
        
        return (
          <div key={result.id} className="bg-white shadow rounded-lg">
            {/* Compact Header - Always Visible */}
            <div 
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleExpanded(result.id)}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-4">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {result.repository_owner}/{result.repository_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {formatDistanceToNow(new Date(result.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  
                  {/* Quick Stats */}
                  <div className="flex space-x-6 text-sm">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">
                        {result.total_dependencies}
                      </div>
                      <div className="text-gray-500 text-xs">Total</div>
                    </div>
                    <div className="text-center">
                      <div className={`text-lg font-semibold ${
                        result.missing_dependencies > 0 ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {result.missing_dependencies}
                      </div>
                      <div className="text-gray-500 text-xs">Missing</div>
                    </div>
                    {packageFileDeps.length > 0 && (
                      <div className="text-center">
                        <div className="text-lg font-semibold text-orange-600">
                          {packageFileDeps.length}
                        </div>
                        <div className="text-gray-500 text-xs">Package Files</div>
                      </div>
                    )}
                    {sourceCodeDeps.length > 0 && (
                      <div className="text-center">
                        <div className="text-lg font-semibold text-green-600">
                          {sourceCodeDeps.length}
                        </div>
                        <div className="text-gray-500 text-xs">Source Code</div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {result.missing_dependencies === 0 ? (
                    <span className="text-green-600 font-medium text-sm">✅ Secure</span>
                  ) : (
                    <span className="text-red-600 font-medium text-sm">⚠️ Vulnerable</span>
                  )}
                  <svg 
                    className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Expanded Details */}
            {isExpanded && result.missing_dependencies > 0 && (
              <div className="border-t border-gray-200 p-4">
                <h4 className="text-md font-medium text-red-600 mb-3">
                  Missing Dependencies - {filter === 'all' ? 'All' : filter === 'package-files' ? 'Package Files' : 'Source Code'} 
                  ({filteredPackages.length})
                </h4>
                
                {filteredPackages.length === 0 ? (
                  <p className="text-gray-500 text-sm">No dependencies match the current filter.</p>
                ) : (
                  <div className="grid gap-2 max-h-96 overflow-y-auto">
                    {filteredPackages.map((dep, index) => (
                      <MissingPackageCard key={index} dependency={dep} />
                    ))}
                  </div>
                )}
              </div>
            )}

            {isExpanded && result.missing_dependencies === 0 && (
              <div className="border-t border-gray-200 p-4">
                <div className="text-green-600 font-medium">
                  ✅ All dependencies exist in their respective registries
                </div>
              </div>
            )}
          </div>
        )
      })}
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