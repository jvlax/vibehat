export interface Dependency {
  name: string
  version?: string
  ecosystem: string
  file_path: string
}

export interface PublishedPackage {
  name: string
  ecosystem: string
  version: string
  registry_url: string
  published_at: string
  source_file?: string
}

export interface ScanResult {
  id: number
  repository_url: string
  repository_owner: string
  repository_name: string
  total_dependencies: number
  missing_dependencies: number
  missing_packages: Dependency[]
  published_packages?: PublishedPackage[]
  created_at: string
}

export interface ScanRequest {
  repository_url: string
}

export interface PublishRequest {
  package_name: string
  ecosystem: string
  source_file?: string
}

export interface DashboardStats {
  total_scans: number
  total_published_packages: number
  vulnerable_repos: number
  recent_scans: ScanResult[]
  recent_published: PublishedPackage[]
} 