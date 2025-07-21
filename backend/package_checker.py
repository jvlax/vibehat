import httpx
from typing import Dict, Any, Optional

class PackageChecker:
    def __init__(self):
        self.registries = {
            'npm': 'https://registry.npmjs.org',
            'pypi': 'https://pypi.org/pypi',
            'cargo': 'https://crates.io/api/v1/crates',
            'go': 'https://proxy.golang.org',
            'packagist': 'https://packagist.org/packages',
            'rubygems': 'https://rubygems.org/api/v1/gems'
        }
    
    async def check_package_exists(self, package_name: str, ecosystem: str) -> bool:
        """Check if a package exists in the given ecosystem"""
        
        if ecosystem not in self.registries:
            return True  # Assume it exists if we don't know the ecosystem
        
        try:
            async with httpx.AsyncClient() as client:
                if ecosystem == 'npm':
                    return await self._check_npm(client, package_name)
                elif ecosystem == 'pypi':
                    return await self._check_pypi(client, package_name)
                elif ecosystem == 'cargo':
                    return await self._check_cargo(client, package_name)
                elif ecosystem == 'go':
                    return await self._check_go(client, package_name)
                elif ecosystem == 'packagist':
                    return await self._check_packagist(client, package_name)
                elif ecosystem == 'rubygems':
                    return await self._check_rubygems(client, package_name)
                    
        except Exception as e:
            print(f"Error checking package {package_name} in {ecosystem}: {e}")
            return True  # Assume it exists on error to avoid false positives
        
        return True
    
    async def _check_npm(self, client: httpx.AsyncClient, package_name: str) -> bool:
        """Check if npm package exists"""
        url = f"{self.registries['npm']}/{package_name}"
        response = await client.get(url)
        
        if response.status_code != 200:
            return False
            
        # Check if package is unpublished
        try:
            data = response.json()
            # If the package has an "unpublished" field, it means it was deleted
            if "time" in data and "unpublished" in data["time"]:
                return False
            return True
        except:
            # If we can't parse JSON, assume it exists if status was 200
            return True
    
    async def _check_pypi(self, client: httpx.AsyncClient, package_name: str) -> bool:
        """Check if PyPI package exists"""
        url = f"{self.registries['pypi']}/{package_name}/json"
        response = await client.get(url)
        return response.status_code == 200
    
    async def _check_cargo(self, client: httpx.AsyncClient, package_name: str) -> bool:
        """Check if Cargo/crates.io package exists"""
        url = f"{self.registries['cargo']}/{package_name}"
        response = await client.get(url)
        return response.status_code == 200
    
    async def _check_go(self, client: httpx.AsyncClient, package_name: str) -> bool:
        """Check if Go module exists"""
        # Go modules are more complex, this is a simplified check
        url = f"{self.registries['go']}/{package_name}/@v/list"
        response = await client.get(url)
        return response.status_code == 200
    
    async def _check_packagist(self, client: httpx.AsyncClient, package_name: str) -> bool:
        """Check if Packagist (Composer) package exists"""
        url = f"{self.registries['packagist']}/{package_name}.json"
        response = await client.get(url)
        return response.status_code == 200
    
    async def _check_rubygems(self, client: httpx.AsyncClient, package_name: str) -> bool:
        """Check if RubyGems package exists"""
        url = f"{self.registries['rubygems']}/{package_name}.json"
        response = await client.get(url)
        return response.status_code == 200 