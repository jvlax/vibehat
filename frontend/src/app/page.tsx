'use client'

import { useState, useEffect } from 'react'
import { ScanForm } from '@/components/ScanForm'
import { ScanResults } from '@/components/ScanResults'
import { ScanResult } from '@/types'
import axios from 'axios'

// Made-up npm packages that don't exist and aren't in our test manifest
// import superReactHelper from 'super-react-helper';  // Fake package for testing
// const awesomeUtils = require('awesome-frontend-utils');  // Another fake package
// import('demo-dynamic-package');  // Dynamic import of fake package

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [scanResults, setScanResults] = useState<ScanResult[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchRecentScans()
  }, [])

  const fetchRecentScans = async () => {
    try {
      const response = await axios.get(`${API_URL}/scans`)
      setScanResults(response.data)
    } catch (error) {
      console.error('Error fetching scans:', error)
    }
  }

  const handleScanComplete = (result: ScanResult) => {
    setScanResults([result, ...scanResults.slice(0, 9)]) // Keep only 10 most recent
  }

  return (
  const [scanResults, setScanResults] = useState<ScanResult[]>([])
  const [loading, setLoading] = useState(false)

  const fetchScanResults = async () => {
    try {
      const response = await axios.get(`${API_URL}/scans`)
      setScanResults(response.data)
    } catch (error) {
      console.error('Error fetching scan results:', error)
    }
  }

  useEffect(() => {
    fetchScanResults()
  }, [])

  const handleScanComplete = (newResult: ScanResult) => {
    setScanResults(prev => [newResult, ...prev])
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
            VibeHat
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            AI Dependency Exploit Scanner
          </p>
          <p className="mt-2 text-gray-500">
            Scan GitHub repositories for missing dependencies that AI might hallucinate
          </p>
        </div>

        <div className="mt-12">
          <ScanForm onScanComplete={handleScanComplete} setLoading={setLoading} />
        </div>

        <div className="mt-12">
          <ScanResults results={scanResults} loading={loading} />
        </div>
      </div>
    </div>
  )
} 