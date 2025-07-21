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
            
            # Scan root level files
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
            
            # Also scan subdirectories recursively
            sub_deps = self._scan_subdirectories(repository, dependency_files)
            dependencies.extend(sub_deps)
                    
            return dependencies
            
        except Exception as e:
            raise Exception(f"Error scanning repository: {str(e)}")
    
    def _scan_subdirectories(self, repository, dependency_files, path="", max_depth=3, current_depth=0):
        """Recursively scan subdirectories for dependency files"""
        dependencies = []
        
        if current_depth >= max_depth:
            return dependencies
            
        try:
            # Get directory contents
            contents = list(repository.directory_contents(path))
            
            for item in contents:
                # Handle tuple structure from github3.py directory_contents
                if isinstance(item, tuple) and len(item) == 2:
                    item_name, content_obj = item
                    item_type = content_obj.type
                    item_path = content_obj.path
                else:
                    # Fallback for object structure
                    item_name = item.name
                    item_type = item.type
                    item_path = item.path
                
                if item_type == 'dir':
                    # Recursively scan subdirectories
                    sub_deps = self._scan_subdirectories(
                        repository, 
                        dependency_files, 
                        item_path, 
                        max_depth, 
                        current_depth + 1
                    )
                    dependencies.extend(sub_deps)
                elif item_type == 'file':
                    # Check if this file is a dependency file
                    filename = item_name
                    for dep_filename, ecosystem in dependency_files:
                        if filename == dep_filename:
                            try:
                                file_content = repository.file_contents(item_path)
                                if file_content:
                                    deps = self._parse_dependency_file(
                                        file_content.decoded.decode('utf-8'),
                                        item_path,
                                        ecosystem
                                    )
                                    dependencies.extend(deps)
                            except Exception as e:
                                continue
                            break
        except Exception as e:
            # Directory doesn't exist or can't be accessed
            pass
            
        return dependencies
    
    def _parse_dependency_file(self, content: str, filename: str, ecosystem: str) -> List[Dependency]:
        """Parse different types of dependency files"""
        dependencies = []
        
        if filename.endswith('package.json'):
            dependencies.extend(self._parse_package_json(content, ecosystem))
        elif filename.endswith('requirements.txt'):
            dependencies.extend(self._parse_requirements_txt(content, ecosystem))
        elif filename.endswith('Cargo.toml'):
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