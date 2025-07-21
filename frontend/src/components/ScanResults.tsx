'use client'

import { ScanResult, Dependency, PublishedPackage } from '@/types'
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
      <div className="glass rounded-xl p-8 border border-white/10">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-700 rounded w-1/4 mb-6"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-700 rounded"></div>
            <div className="h-4 bg-gray-700 rounded w-5/6"></div>
            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          </div>
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="glass rounded-xl p-12 text-center border border-white/10">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-white mb-2">No Scan Results Yet</h3>
        <p className="text-gray-400">Scan a repository above to see dependency analysis results</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <span className="mr-3">📊</span>
          Scan Results
        </h2>
        
        {/* Filter Controls */}
        {results.length > 0 && results[0].missing_dependencies > 0 && (
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 text-sm rounded-lg transition-all ${
                filter === 'all' 
                  ? 'bg-blue-600 text-white glow-blue' 
                  : 'glass text-gray-300 hover:text-white hover:bg-white/5'
              }`}
            >
              All ({results[0]?.missing_dependencies || 0})
            </button>
            <button
              onClick={() => setFilter('package-files')}
              className={`px-4 py-2 text-sm rounded-lg transition-all ${
                filter === 'package-files' 
                  ? 'bg-orange-600 text-white glow-red' 
                  : 'glass text-gray-300 hover:text-white hover:bg-white/5'
              }`}
            >
              Package Files ({results[0] ? filterDependencies(results[0].missing_packages, 'package-files').length : 0})
            </button>
            <button
              onClick={() => setFilter('source-code')}
              className={`px-4 py-2 text-sm rounded-lg transition-all ${
                filter === 'source-code' 
                  ? 'bg-green-600 text-white glow-green' 
                  : 'glass text-gray-300 hover:text-white hover:bg-white/5'
              }`}
            >
              Source Code ({results[0] ? filterDependencies(results[0].missing_packages, 'source-code').length : 0})
            </button>
          </div>
        )}
      </div>
      
      {results.map((result) => {
        const isExpanded = expandedResults.has(result.id)
        const filteredPackages = filterDependencies(result.missing_packages, filter)
        const packageFileDeps = filterDependencies(result.missing_packages, 'package-files')
        const sourceCodeDeps = filterDependencies(result.missing_packages, 'source-code')
        
        return (
          <div key={result.id} className="glass rounded-xl border border-white/10 card-hover">
            {/* Compact Header - Always Visible */}
            <div 
              className="p-6 cursor-pointer transition-all"
              onClick={() => toggleExpanded(result.id)}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-6">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-1">
                      {result.repository_owner}/{result.repository_name}
                    </h3>
                    <p className="text-sm text-gray-400">
                      Scanned {formatDistanceToNow(new Date(result.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  
                  {/* Quick Stats */}
                  <div className="flex space-x-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">
                        {result.total_dependencies}
                      </div>
                      <div className="text-gray-400 text-xs">Total</div>
                    </div>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${
                        result.missing_dependencies > 0 ? 'text-red-400' : 'text-green-400'
                      }`}>
                        {result.missing_dependencies}
                      </div>
                      <div className="text-gray-400 text-xs">Missing</div>
                    </div>
                    {packageFileDeps.length > 0 && (
                      <div className="text-center">
                        <div className="text-xl font-bold text-orange-400">
                          {packageFileDeps.length}
                        </div>
                        <div className="text-gray-400 text-xs">Package Files</div>
                      </div>
                    )}
                    {sourceCodeDeps.length > 0 && (
                      <div className="text-center">
                        <div className="text-xl font-bold text-green-400">
                          {sourceCodeDeps.length}
                        </div>
                        <div className="text-gray-400 text-xs">Source Code</div>
                      </div>
                    )}
                    {result.published_packages && result.published_packages.length > 0 && (
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-400">
                          {result.published_packages.length}
                        </div>
                        <div className="text-gray-400 text-xs">Published</div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  {result.missing_dependencies === 0 ? (
                    <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
                      <span className="text-green-400">✅</span>
                      <span className="text-green-300 font-medium text-sm">Secure</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-red-500/20 border border-red-500/30">
                      <span className="text-red-400">⚠️</span>
                      <span className="text-red-300 font-medium text-sm">Vulnerable</span>
                    </div>
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
            {isExpanded && (
              <div className="border-t border-white/10">
                {/* Published Packages Section */}
                {result.published_packages && result.published_packages.length > 0 && (
                  <div className="p-6 border-b border-white/10">
                    <h4 className="text-lg font-semibold text-blue-400 mb-4 flex items-center">
                      <span className="mr-2">🚀</span>
                      Published Warning Packages ({result.published_packages.length})
                    </h4>
                    <div className="grid gap-3">
                      {result.published_packages.map((pkg, index) => (
                        <PublishedPackageCard key={index} package={pkg} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing Dependencies Section */}
                {result.missing_dependencies > 0 && (
                  <div className="p-6">
                    <h4 className="text-lg font-semibold text-red-400 mb-4 flex items-center">
                      <span className="mr-2">⚠️</span>
                      Missing Dependencies - {filter === 'all' ? 'All' : filter === 'package-files' ? 'Package Files' : 'Source Code'} 
                      ({filteredPackages.length})
                    </h4>
                    
                    {filteredPackages.length === 0 ? (
                      <p className="text-gray-400 text-sm">No dependencies match the current filter.</p>
                    ) : (
                      <div className="grid gap-3 max-h-96 overflow-y-auto">
                        {filteredPackages.map((dep, index) => (
                          <MissingPackageCard key={index} dependency={dep} />
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {result.missing_dependencies === 0 && (
                  <div className="p-6">
                    <div className="text-center py-8">
                      <div className="text-4xl mb-2">🛡️</div>
                      <div className="text-green-400 font-semibold text-lg">
                        All dependencies exist in their respective registries
                      </div>
                      <p className="text-gray-400 text-sm mt-1">
                        No dependency confusion vulnerabilities detected
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function PublishedPackageCard({ package: pkg }: { package: PublishedPackage }) {
  const getEcosystemIcon = (ecosystem: string) => {
    const icons = {
      npm: '📦',
      pypi: '🐍',
      cargo: '⚙️',
      go: '🐹'
    }
    return icons[ecosystem as keyof typeof icons] || '📦'
  }

  const getEcosystemColor = (ecosystem: string) => {
    const colors = {
      npm: 'text-red-400 bg-red-500/10 border-red-500/20',
      pypi: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
      cargo: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      go: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20'
    }
    return colors[ecosystem as keyof typeof colors] || 'text-gray-400 bg-gray-500/10 border-gray-500/20'
  }

  return (
    <div className="glass rounded-lg p-4 border border-green-500/20 bg-green-500/5">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <span className="text-xl">{getEcosystemIcon(pkg.ecosystem)}</span>
          <div>
            <div className="font-mono font-semibold text-white">{pkg.name}</div>
            <div className="text-sm text-gray-400">v{pkg.version}</div>
          </div>
          <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getEcosystemColor(pkg.ecosystem)}`}>
            {pkg.ecosystem}
          </span>
        </div>
        <a
          href={pkg.registry_url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-1"
        >
          <span>View</span>
          <span>↗</span>
        </a>
      </div>
    </div>
  )
}

function MissingPackageCard({ dependency }: { dependency: Dependency }) {
  const getEcosystemIcon = (ecosystem: string) => {
    const icons = {
      npm: '📦',
      pypi: '🐍',
      cargo: '⚙️',
      go: '🐹'
    }
    return icons[ecosystem as keyof typeof icons] || '📦'
  }

  const getEcosystemColor = (ecosystem: string) => {
    const colors = {
      npm: 'text-red-400 bg-red-500/10 border-red-500/20',
      pypi: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
      cargo: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      go: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20'
    }
    return colors[ecosystem as keyof typeof colors] || 'text-gray-400 bg-gray-500/10 border-gray-500/20'
  }

  return (
    <div className="glass rounded-lg p-4 border border-red-500/20 bg-red-500/5">
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-3">
          <span className="text-xl">{getEcosystemIcon(dependency.ecosystem)}</span>
          <div className="flex-1">
            <div className="font-mono font-semibold text-white">{dependency.name}</div>
            {dependency.version && (
              <div className="text-sm text-gray-400">Version: {dependency.version}</div>
            )}
            <div className="text-sm text-gray-400 mt-1">
              📄 {dependency.file_path}
            </div>
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getEcosystemColor(dependency.ecosystem)}`}>
          {dependency.ecosystem}
        </span>
      </div>
      
      <div className="mt-3 flex items-center space-x-2 text-sm text-red-400">
        <span>⚠️</span>
        <span>Package doesn't exist - potential dependency confusion target</span>
      </div>
    </div>
  )
} 