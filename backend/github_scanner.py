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
            
            # NEW: Scan source code files for import statements
            source_deps = self._scan_source_files(repository)
            dependencies.extend(source_deps)
            
            # Deduplicate dependencies by name and ecosystem
            seen = set()
            unique_dependencies = []
            for dep in dependencies:
                key = (dep.name, dep.ecosystem)
                if key not in seen:
                    seen.add(key)
                    unique_dependencies.append(dep)
                    
            return unique_dependencies
            
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
    
    def _scan_source_files(self, repository, path="", max_depth=3, current_depth=0):
        """Scan source code files for import statements"""
        dependencies = []
        
        if current_depth >= max_depth:
            return dependencies
            
        # Source file extensions to scan
        source_extensions = {
            '.js': 'npm',
            '.jsx': 'npm', 
            '.ts': 'npm',
            '.tsx': 'npm',
            '.py': 'pypi',
            '.go': 'go',
            '.rs': 'cargo',
            '.php': 'packagist',
            '.rb': 'rubygems'
        }
        
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
                    # Skip common directories that don't contain source code
                    if item_name not in ['node_modules', '.git', '__pycache__', 'target', 'vendor', 'dist', 'build']:
                        # Recursively scan subdirectories
                        sub_deps = self._scan_source_files(
                            repository, 
                            item_path, 
                            max_depth, 
                            current_depth + 1
                        )
                        dependencies.extend(sub_deps)
                elif item_type == 'file':
                    # Check if this is a source file we can parse
                    file_ext = None
                    for ext in source_extensions:
                        if item_name.endswith(ext):
                            file_ext = ext
                            break
                    
                    if file_ext:
                        try:
                            file_content = repository.file_contents(item_path)
                            if file_content:
                                deps = self._parse_source_file(
                                    file_content.decoded.decode('utf-8'),
                                    item_path,
                                    source_extensions[file_ext]
                                )
                                dependencies.extend(deps)
                        except Exception as e:
                            # Skip files that can't be read
                            continue
        except Exception as e:
            # Directory doesn't exist or can't be accessed
            pass
            
        return dependencies
    
    def _parse_source_file(self, content: str, file_path: str, ecosystem: str) -> List[Dependency]:
        """Parse source code files for import statements"""
        dependencies = []
        
        if ecosystem == 'npm':
            dependencies.extend(self._parse_javascript_imports(content, file_path, ecosystem))
        elif ecosystem == 'pypi':
            dependencies.extend(self._parse_python_imports(content, file_path, ecosystem))
        # Add more parsers for other ecosystems as needed
        
        return dependencies
    
    def _parse_javascript_imports(self, content: str, file_path: str, ecosystem: str) -> List[Dependency]:
        """Parse JavaScript/TypeScript imports and requires"""
        dependencies = []
        
        # Patterns for different import styles
        patterns = [
            # require('package')
            r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            # import ... from 'package'
            r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",
            # import 'package'
            r"import\s+['\"]([^'\"]+)['\"]",
            # import('package') - dynamic imports
            r"import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                package_name = match.group(1)
                
                # Filter out relative imports and built-in modules
                if not self._is_external_package(package_name, ecosystem):
                    continue
                
                # Normalize the package name for registry checking
                normalized_name = self._normalize_package_name(package_name, ecosystem)
                
                dependencies.append(Dependency(
                    name=normalized_name,
                    version=None,
                    ecosystem=ecosystem,
                    file_path=file_path
                ))
        
        return dependencies
    
    def _parse_python_imports(self, content: str, file_path: str, ecosystem: str) -> List[Dependency]:
        """Parse Python import statements"""
        dependencies = []
        
        # Patterns for different import styles
        patterns = [
            # import package
            r"^import\s+([a-zA-Z0-9_][a-zA-Z0-9_\.]*)",
            # from package import ...
            r"^from\s+([a-zA-Z0-9_][a-zA-Z0-9_\.]*)\s+import",
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments
            if line.startswith('#'):
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    package_name = match.group(1)
                    
                    # Get the top-level package name
                    top_level = package_name.split('.')[0]
                    
                    # Filter out relative imports and built-in modules
                    if not self._is_external_package(top_level, ecosystem):
                        continue
                    
                    # Normalize the package name for registry checking
                    normalized_name = self._normalize_package_name(top_level, ecosystem)
                    
                    dependencies.append(Dependency(
                        name=normalized_name,
                        version=None,
                        ecosystem=ecosystem,
                        file_path=file_path
                    ))
                    break
        
        return dependencies
    
    def _is_external_package(self, package_name: str, ecosystem: str) -> bool:
        """Check if a package name refers to an external package (not relative/built-in)"""
        
        # Skip relative imports
        if package_name.startswith('.'):
            return False
            
        # Skip local modules (simple heuristic: if it matches common local file patterns)
        local_patterns = [
            'github_scanner', 'package_checker', 'models', 'schemas', 'database',
            'main', 'config', 'utils', 'helpers', 'constants'
        ]
        if package_name in local_patterns:
            return False
            
        if ecosystem == 'npm':
            # Skip Node.js built-in modules
            node_builtins = {
                'fs', 'path', 'http', 'https', 'url', 'crypto', 'os', 'util', 
                'events', 'stream', 'buffer', 'child_process', 'cluster', 
                'dgram', 'dns', 'net', 'querystring', 'readline', 'repl',
                'string_decoder', 'tls', 'tty', 'vm', 'zlib', 'assert',
                'console', 'constants', 'domain', 'punycode', 'timers'
            }
            return package_name not in node_builtins
            
        elif ecosystem == 'pypi':
            # Skip Python standard library modules
            python_builtins = {
                'os', 'sys', 'json', 're', 'time', 'datetime', 'math', 'random',
                'collections', 'itertools', 'functools', 'operator', 'pathlib',
                'urllib', 'http', 'email', 'html', 'xml', 'sqlite3', 'csv',
                'configparser', 'logging', 'unittest', 'doctest', 'pdb',
                'profile', 'timeit', 'trace', 'gc', 'weakref', 'copy',
                'pickle', 'copyreg', 'shelve', 'marshal', 'dbm', 'sqlite3',
                'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile'
            }
            return package_name not in python_builtins
            
        return True
    
    def _normalize_package_name(self, import_name: str, ecosystem: str) -> str:
        """Normalize import names to actual package names"""
        
        if ecosystem == 'pypi':
            # Common Python package name mappings
            mappings = {
                'github3': 'github3.py',
                'PIL': 'Pillow',
                'cv2': 'opencv-python',
                'sklearn': 'scikit-learn',
                'yaml': 'PyYAML',
                'dateutil': 'python-dateutil'
            }
            return mappings.get(import_name, import_name)
            
        elif ecosystem == 'npm':
            # Common npm package name mappings could go here
            return import_name
            
        return import_name 