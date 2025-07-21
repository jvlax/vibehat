import httpx
import re
import json
from typing import List, Dict, Any
from schemas import Dependency
import github3

class GitHubScanner:
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.github = github3.login(token=github_token) if github_token else None
        
    async def scan_repository(self, owner: str, repo: str) -> List[Dependency]:
        """Scan a GitHub repository for dependencies"""
        dependencies = []
        
        if not self.github:
            raise Exception("GitHub token required for repository scanning")
        
        try:
            repository = self.github.repository(owner, repo)
            
            # Scan different dependency files
            dependency_files = [
                ('package.json', 'npm'),
                ('requirements.txt', 'pypi'),
                ('Cargo.toml', 'cargo'),
                ('go.mod', 'go'),
                ('composer.json', 'packagist'),
                ('Gemfile', 'rubygems'),
            ]
            
            for filename, ecosystem in dependency_files:
                try:
                    file_content = repository.file_contents(filename)
                    if file_content:
                        deps = self._parse_dependency_file(
                            file_content.decoded.decode('utf-8'),
                            filename,
                            ecosystem
                        )
                        dependencies.extend(deps)
                except:
                    # File doesn't exist, continue
                    continue
                    
            return dependencies
            
        except Exception as e:
            raise Exception(f"Error scanning repository: {str(e)}")
    
    def _parse_dependency_file(self, content: str, filename: str, ecosystem: str) -> List[Dependency]:
        """Parse different types of dependency files"""
        dependencies = []
        
        if filename == 'package.json':
            dependencies.extend(self._parse_package_json(content, ecosystem))
        elif filename == 'requirements.txt':
            dependencies.extend(self._parse_requirements_txt(content, ecosystem))
        elif filename == 'Cargo.toml':
            dependencies.extend(self._parse_cargo_toml(content, ecosystem))
        # Add more parsers as needed
        
        return dependencies
    
    def _parse_package_json(self, content: str, ecosystem: str) -> List[Dependency]:
        """Parse package.json for npm dependencies"""
        dependencies = []
        try:
            data = json.loads(content)
            
            # Parse dependencies and devDependencies
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        dependencies.append(Dependency(
                            name=name,
                            version=version,
                            ecosystem=ecosystem,
                            file_path='package.json'
                        ))
        except:
            pass
            
        return dependencies
    
    def _parse_requirements_txt(self, content: str, ecosystem: str) -> List[Dependency]:
        """Parse requirements.txt for Python dependencies"""
        dependencies = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle different requirement formats
                name_match = re.match(r'^([a-zA-Z0-9\-_\.]+)', line)
                if name_match:
                    name = name_match.group(1)
                    version = None
                    
                    # Extract version if present
                    version_match = re.search(r'[><=!~]+([0-9\.]+)', line)
                    if version_match:
                        version = version_match.group(1)
                    
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        ecosystem=ecosystem,
                        file_path='requirements.txt'
                    ))
        
        return dependencies
    
    def _parse_cargo_toml(self, content: str, ecosystem: str) -> List[Dependency]:
        """Parse Cargo.toml for Rust dependencies"""
        dependencies = []
        
        # Basic TOML parsing for dependencies section
        in_dependencies = False
        for line in content.split('\n'):
            line = line.strip()
            
            if line == '[dependencies]':
                in_dependencies = True
                continue
            elif line.startswith('[') and line != '[dependencies]':
                in_dependencies = False
                continue
                
            if in_dependencies and '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    version_part = parts[1].strip().strip('"\'')
                    
                    dependencies.append(Dependency(
                        name=name,
                        version=version_part,
                        ecosystem=ecosystem,
                        file_path='Cargo.toml'
                    ))
        
        return dependencies 