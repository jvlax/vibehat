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

    setLoading(true)
    setError('')

    try {
      const response = await axios.post(`${API_URL}/scan/repository`, {
        repository_url: repositoryUrl
      })
      
      onScanComplete(response.data)
      setRepositoryUrl('')
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error scanning repository')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">
        Scan Repository
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="repository-url" className="block text-sm font-medium text-gray-700">
            GitHub Repository URL
          </label>
          <input
            type="url"
            id="repository-url"
            value={repositoryUrl}
            onChange={(e) => setRepositoryUrl(e.target.value)}
            placeholder="https://github.com/owner/repository"
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          Scan Repository
        </button>
      </form>
    </div>
  )
} 