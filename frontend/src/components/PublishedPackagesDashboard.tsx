'use client'

import { DashboardStats, PublishedPackage } from '@/types'
import { formatDistanceToNow } from 'date-fns'
import { useState } from 'react'

interface PublishedPackagesDashboardProps {
  stats: DashboardStats | null
}

export function PublishedPackagesDashboard({ stats }: PublishedPackagesDashboardProps) {
  const [selectedScan, setSelectedScan] = useState<any>(null)

  if (!stats) {
    return (
      <div className="space-y-8">
        <div className="bg-black/40 backdrop-blur-sm rounded-lg p-8 border border-white/20 animate-pulse">
          <div className="h-6 bg-gray-600 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-600 rounded w-1/4"></div>
        </div>
      </div>
    )
  }

  // Mock data for now since we don't have real published packages yet
  const mockPublishedPackages = [
    {
      name: 'super-react-helper',
      ecosystem: 'npm',
      version: '1.0.0',
      registry_url: 'https://www.npmjs.com/package/super-react-helper',
      published_at: new Date().toISOString(),
      source_file: 'test-demo-imports.js',
      repository: 'jvlax/vibehat'
    },
    {
      name: 'awesome-frontend-utils',
      ecosystem: 'npm', 
      version: '1.0.0',
      registry_url: 'https://www.npmjs.com/package/awesome-frontend-utils',
      published_at: new Date().toISOString(),
      source_file: 'test-demo-imports.js',
      repository: 'jvlax/vibehat'
    },
    {
      name: 'demo-dynamic-package',
      ecosystem: 'npm',
      version: '1.0.0', 
      registry_url: 'https://www.npmjs.com/package/demo-dynamic-package',
      published_at: new Date().toISOString(),
      source_file: 'test-demo-imports.js',
      repository: 'jvlax/vibehat'
    },
    {
      name: 'super_awesome_helper',
      ecosystem: 'pypi',
      version: '1.0.0',
      registry_url: 'https://pypi.org/project/super_awesome_helper/',
      published_at: new Date().toISOString(),
      source_file: 'backend/main.py',
      repository: 'jvlax/vibehat'
    },
    {
      name: 'magical_utils',
      ecosystem: 'pypi',
      version: '1.0.0',
      registry_url: 'https://pypi.org/project/magical_utils/',
      published_at: new Date().toISOString(),
      source_file: 'backend/main.py',
      repository: 'jvlax/vibehat'
    },
    {
      name: 'demo_package_for_testing',
      ecosystem: 'pypi',
      version: '1.0.0',
      registry_url: 'https://pypi.org/project/demo_package_for_testing/',
      published_at: new Date().toISOString(),
      source_file: 'backend/main.py',
      repository: 'jvlax/vibehat'
    }
  ]

  const mockRecentScans = [
    {
      id: 1,
      repository_owner: 'jvlax',
      repository_name: 'vibehat',
      created_at: new Date().toISOString(),
      vibed_packages: 6,
      published_packages: mockPublishedPackages
    },
    {
      id: 2,
      repository_owner: 'example',
      repository_name: 'secure-app',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      vibed_packages: 0,
      published_packages: []
    }
  ]

  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="bg-black/40 backdrop-blur-sm rounded-lg p-8 border border-white/20">
        <div className="text-center">
          <div className="text-4xl font-bold text-white mb-2">{mockPublishedPackages.length}</div>
          <div className="text-gray-300">Packages Published</div>
        </div>
      </div>

      {/* Recent Scans */}
      <div className="bg-black/40 backdrop-blur-sm rounded-lg p-8 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6">Recent Scans</h2>
        
        <div className="space-y-4">
          {mockRecentScans.map((scan) => (
            <div
              key={scan.id}
              onClick={() => setSelectedScan(selectedScan?.id === scan.id ? null : scan)}
              className="bg-black/20 rounded-lg p-4 border border-white/10 cursor-pointer hover:bg-black/30 transition-all"
            >
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-white font-medium">
                    {scan.repository_owner}/{scan.repository_name}
                  </div>
                  <div className="text-gray-400 text-sm">
                    {formatDistanceToNow(new Date(scan.created_at), { addSuffix: true })}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-white">{scan.vibed_packages}</div>
                  <div className="text-gray-400 text-xs">Vibed</div>
                </div>
              </div>

              {/* Expanded Details */}
              {selectedScan?.id === scan.id && (
                <div className="mt-6 pt-4 border-t border-white/10">
                  {scan.published_packages.length > 0 ? (
                    <div className="space-y-3">
                      <div className="text-white font-medium mb-3">Published Packages:</div>
                      {scan.published_packages.map((pkg, index) => (
                        <div key={index} className="bg-black/20 rounded p-3 border border-white/10">
                          <div className="flex justify-between items-center">
                            <div>
                              <div className="text-white font-mono">{pkg.name}</div>
                              <div className="text-gray-400 text-sm">{pkg.source_file}</div>
                              <div className="text-gray-500 text-xs">{pkg.ecosystem}</div>
                            </div>
                            <a
                              href={pkg.registry_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-400 hover:text-blue-300 text-sm"
                              onClick={(e) => e.stopPropagation()}
                            >
                              View Package
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-400 text-center py-4">
                      No packages to publish - repository is secure
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 