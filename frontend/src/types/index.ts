export interface Dependency {
  name: string
  version?: string
  ecosystem: string
  file_path: string
}

export interface ScanResult {
  id: number
  repository_url: string
  repository_owner: string
  repository_name: string
  total_dependencies: number
  missing_dependencies: number
  missing_packages: Dependency[]
  created_at: string
}

export interface ScanRequest {
  repository_url: string
}

export interface ExploitRequest {
  package_name: string
  ecosystem: string
  version?: string
} 