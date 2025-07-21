import os
import json
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Optional, Set
from pathlib import Path
import httpx

class PackagePublisher:
    def __init__(self):
        self.npm_token = os.getenv("NPM_TOKEN")
        self.pypi_token = os.getenv("PYPI_TOKEN")
        self.warning_website = os.getenv("WARNING_WEBSITE", "https://vibehat.dev/dependency-confusion")
    
    def _is_test_package(self, package_name: str, ecosystem: str) -> bool:
        """Check if a package is in our test data manifest and should not be published"""
        try:
            # Simple approach: check manifest file each time
            manifest_path = Path(__file__).parent.parent / "test-data" / "FAKE_PACKAGES_MANIFEST.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                fake_packages = manifest.get("fake_packages", {}).get(ecosystem, {})
                all_test_packages = (
                    fake_packages.get("declared_dependencies", []) + 
                    fake_packages.get("undeclared_imports", [])
                )
                return package_name in all_test_packages
        except Exception as e:
            print(f"Warning: Could not check test packages manifest: {e}")
        
        return False
        
    async def publish_warning_package(self, package_name: str, ecosystem: str, source_file: str = None) -> Dict[str, Any]:
        """Publish a warning package to the specified ecosystem"""
        
        # PROTECTION: Never publish test packages
        if self._is_test_package(package_name, ecosystem):
            return {
                "success": False,
                "package": package_name,
                "ecosystem": ecosystem,
                "message": f"PROTECTION: Refused to publish test package '{package_name}' from test data",
                "error": "Test packages are protected from accidental publication"
            }
        
        if ecosystem == 'npm':
            return await self._publish_npm_package(package_name, source_file)
        elif ecosystem == 'pypi':
            return await self._publish_pypi_package(package_name, source_file)
        else:
            raise ValueError(f"Unsupported ecosystem: {ecosystem}")
    
    async def _publish_npm_package(self, package_name: str, source_file: str = None) -> Dict[str, Any]:
        """Publish warning package to npm"""
        
        if not self.npm_token:
            raise ValueError("NPM_TOKEN environment variable not set")
        
        # Create temporary directory for package
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / package_name
            package_dir.mkdir()
            
            # Create package.json
            package_json = {
                "name": package_name,
                "version": "1.0.0",
                "description": f"⚠️ SECURITY WARNING: This package was auto-generated to prevent dependency confusion attacks",
                "main": "index.js",
                "keywords": [
                    "security",
                    "dependency-confusion",
                    "vulnerability-research",
                    "vibehat"
                ],
                "author": "VibeHat Security Research",
                "license": "MIT",
                "repository": {
                    "type": "git",
                    "url": "https://github.com/jvlax/vibehat"
                },
                "homepage": self.warning_website
            }
            
            with open(package_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)
            
            # Create warning index.js
            warning_js = f'''
console.warn("\\n🚨 DEPENDENCY CONFUSION VULNERABILITY DETECTED 🚨\\n");
console.warn("Package: {package_name}");
console.warn("You installed a package that didn't exist until now!\\n");
console.warn("This could have been a malicious package installed by an attacker.");
console.warn("This educational package was created by VibeHat security research.\\n");
console.warn("Learn more: {self.warning_website}");
console.warn("Source file that referenced this: {source_file or 'Unknown'}\\n");

module.exports = {{
    warning: "This package was created to demonstrate dependency confusion vulnerability",
    package: "{package_name}",
    learnMore: "{self.warning_website}",
    sourceFile: "{source_file or 'Unknown'}"
}};
'''
            
            with open(package_dir / "index.js", "w") as f:
                f.write(warning_js)
            
            # Create README
            readme = f'''# ⚠️ Security Warning: {package_name}

## 🚨 Dependency Confusion Vulnerability Detected

This package was **automatically created** by VibeHat security research to prevent potential dependency confusion attacks.

### What happened?
- Your code referenced a package called `{package_name}` 
- This package didn't exist in the npm registry
- An attacker could have published a malicious package with this name
- We published this educational warning package to protect you

### Source
This package was referenced in: `{source_file or 'Unknown file'}`

### What should you do?
1. **Review your code** - Make sure `{package_name}` is the correct package name
2. **Check for typos** - This might be a misspelled legitimate package
3. **Use scoped packages** - Consider using `@yourcompany/{package_name}` instead
4. **Contact us** if this is a legitimate internal package name

### Learn More
Visit [{self.warning_website}]({self.warning_website}) to understand dependency confusion vulnerabilities.

### Package Ownership
If you are the rightful owner of this package name, please contact us through our website.

---
*This package was created by VibeHat Security Research to demonstrate and prevent dependency confusion vulnerabilities.*
'''
            
            with open(package_dir / "README.md", "w") as f:
                f.write(readme)
            
            # Setup npm auth
            npmrc_content = f"//registry.npmjs.org/:_authToken={self.npm_token}"
            with open(package_dir / ".npmrc", "w") as f:
                f.write(npmrc_content)
            
            # Publish package
            try:
                result = subprocess.run(
                    ["npm", "publish", "--access", "public"],
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "package": package_name,
                        "ecosystem": "npm",
                        "version": "1.0.0",
                        "message": "Warning package published successfully",
                        "npm_url": f"https://www.npmjs.com/package/{package_name}"
                    }
                else:
                    return {
                        "success": False,
                        "package": package_name,
                        "ecosystem": "npm",
                        "error": result.stderr,
                        "stdout": result.stdout
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "package": package_name,
                    "ecosystem": "npm",
                    "error": str(e)
                }
    
    async def _publish_pypi_package(self, package_name: str, source_file: str = None) -> Dict[str, Any]:
        """Publish warning package to PyPI"""
        
        if not self.pypi_token:
            raise ValueError("PYPI_TOKEN environment variable not set")
        
        # Create temporary directory for package
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / package_name.replace("-", "_")
            package_dir.mkdir()
            
            # Create setup.py
            setup_py = f'''
from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="1.0.0",
    description="⚠️ SECURITY WARNING: This package was auto-generated to prevent dependency confusion attacks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="VibeHat Security Research",
    author_email="security@vibehat.dev",
    url="{self.warning_website}",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="security dependency-confusion vulnerability-research vibehat",
    python_requires=">=3.6",
)
'''
            
            with open(package_dir / "setup.py", "w") as f:
                f.write(setup_py)
            
            # Create package directory
            pkg_dir = package_dir / package_name.replace("-", "_")
            pkg_dir.mkdir()
            
            # Create __init__.py with warning
            init_py = f'''
"""
🚨 DEPENDENCY CONFUSION VULNERABILITY DETECTED 🚨

Package: {package_name}
You imported a package that didn't exist until now!

This could have been a malicious package installed by an attacker.
This educational package was created by VibeHat security research.

Learn more: {self.warning_website}
Source file that referenced this: {source_file or 'Unknown'}
"""

import warnings

warnings.warn(
    f"\\n🚨 DEPENDENCY CONFUSION VULNERABILITY DETECTED 🚨\\n"
    f"Package: {package_name}\\n"
    f"You imported a package that didn't exist until now!\\n"
    f"This could have been a malicious package by an attacker.\\n"
    f"Learn more: {self.warning_website}\\n"
    f"Source: {source_file or 'Unknown'}",
    UserWarning,
    stacklevel=2
)

def get_warning_info():
    return {{
        "warning": "This package was created to demonstrate dependency confusion vulnerability",
        "package": "{package_name}",
        "learnMore": "{self.warning_website}",
        "sourceFile": "{source_file or 'Unknown'}"
    }}

__version__ = "1.0.0"
__all__ = ["get_warning_info"]
'''
            
            with open(pkg_dir / "__init__.py", "w") as f:
                f.write(init_py)
            
            # Create README
            readme = f'''# ⚠️ Security Warning: {package_name}

## 🚨 Dependency Confusion Vulnerability Detected

This package was **automatically created** by VibeHat security research to prevent potential dependency confusion attacks.

### What happened?
- Your code referenced a package called `{package_name}` 
- This package didn't exist in the PyPI registry
- An attacker could have published a malicious package with this name
- We published this educational warning package to protect you

### Source
This package was referenced in: `{source_file or 'Unknown file'}`

### What should you do?
1. **Review your code** - Make sure `{package_name}` is the correct package name
2. **Check for typos** - This might be a misspelled legitimate package
3. **Use private indexes** - Consider using private PyPI indexes for internal packages
4. **Contact us** if this is a legitimate internal package name

### Learn More
Visit [{self.warning_website}]({self.warning_website}) to understand dependency confusion vulnerabilities.

### Package Ownership
If you are the rightful owner of this package name, please contact us through our website.

---
*This package was created by VibeHat Security Research to demonstrate and prevent dependency confusion vulnerabilities.*
'''
            
            with open(package_dir / "README.md", "w") as f:
                f.write(readme)
            
            # Create .pypirc for authentication
            pypirc_content = f'''
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = {self.pypi_token}
'''
            
            pypirc_path = Path.home() / ".pypirc"
            with open(pypirc_path, "w") as f:
                f.write(pypirc_content)
            
            try:
                # Build the package
                subprocess.run(
                    ["python", "setup.py", "sdist", "bdist_wheel"],
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Upload to PyPI
                result = subprocess.run(
                    ["python", "-m", "twine", "upload", "dist/*"],
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "package": package_name,
                        "ecosystem": "pypi",
                        "version": "1.0.0",
                        "message": "Warning package published successfully",
                        "pypi_url": f"https://pypi.org/project/{package_name}/"
                    }
                else:
                    return {
                        "success": False,
                        "package": package_name,
                        "ecosystem": "pypi",
                        "error": result.stderr,
                        "stdout": result.stdout
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "package": package_name,
                    "ecosystem": "pypi",
                    "error": str(e)
                }
            finally:
                # Clean up .pypirc
                if pypirc_path.exists():
                    pypirc_path.unlink()
    
    async def check_if_can_publish(self, package_name: str, ecosystem: str) -> bool:
        """Check if we can publish a package (i.e., it doesn't already exist)"""
        
        if ecosystem == 'npm':
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://registry.npmjs.org/{package_name}")
                return response.status_code == 404
                
        elif ecosystem == 'pypi':
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://pypi.org/pypi/{package_name}/json")
                return response.status_code == 404
                
        return False 