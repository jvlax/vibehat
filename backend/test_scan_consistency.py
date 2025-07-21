"""
Test to verify VibeHat scanner consistency and detect if test packages have been published.

This test ensures:
1. Our scanner finds the expected number of fake packages
2. Our test packages remain unpublished (for testing integrity)
3. We detect if someone has published our test package names
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
try:
    from github_scanner import GitHubScanner
    from package_checker import PackageChecker
except ImportError as e:
    print(f"Import error: {e}")
    # For running in Docker context
    import sys
    sys.path.append('/app')
    from github_scanner import GitHubScanner
    from package_checker import PackageChecker
import os

class ScanConsistencyTest:
    def __init__(self):
        # Try different path resolutions for Docker vs local
        possible_paths = [
            Path(__file__).parent.parent / "test-data" / "FAKE_PACKAGES_MANIFEST.json",  # Local
            Path("/app/../test-data/FAKE_PACKAGES_MANIFEST.json"),  # Docker
            Path("/app/test-data/FAKE_PACKAGES_MANIFEST.json"),     # Docker alt
            Path("./test-data/FAKE_PACKAGES_MANIFEST.json")         # Relative
        ]
        
        self.manifest_path = None
        for path in possible_paths:
            if path.exists():
                self.manifest_path = path
                break
        
        if not self.manifest_path:
            raise Exception(f"Could not find manifest file. Tried: {[str(p) for p in possible_paths]}")
        self.github_scanner = GitHubScanner(os.getenv("GITHUB_TOKEN"))
        self.package_checker = PackageChecker()
        self.expected_manifest = self._load_expected_manifest()
    
    def _load_expected_manifest(self) -> Dict[str, Any]:
        """Load the expected package manifest"""
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Could not load manifest from {self.manifest_path}: {e}")
    
    async def run_scan_consistency_test(self) -> Dict[str, Any]:
        """Run the full consistency test"""
        print("🔍 Running VibeHat Scan Consistency Test...")
        
        results = {
            "test_passed": True,
            "timestamp": "2025-01-21",
            "expected_counts": self.expected_manifest["expected_counts"],
            "actual_counts": {},
            "package_existence_check": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # 1. Scan our own repository
            print("📋 Scanning vibehat repository...")
            dependencies = await self.github_scanner.scan_repository("jvlax", "vibehat")
            
            # 2. Check which packages don't exist (our core functionality)
            missing_packages = []
            for dep in dependencies:
                exists = await self.package_checker.check_package_exists(dep.name, dep.ecosystem)
                if not exists:
                    missing_packages.append(dep)
            
            # 3. Categorize the results
            actual_counts = self._categorize_dependencies(missing_packages)
            results["actual_counts"] = actual_counts
            
            # 4. Compare with expected counts
            count_comparison = self._compare_counts(results["expected_counts"], actual_counts)
            results.update(count_comparison)
            
            # 5. Check if any test packages have been published (integrity check)
            existence_check = await self._check_test_package_existence()
            results["package_existence_check"] = existence_check
            
            # 6. Overall test result
            if count_comparison["counts_match"] and not existence_check["packages_published"]:
                print("✅ All tests passed! Scanner is consistent.")
            else:
                print("⚠️  Test issues detected!")
                results["test_passed"] = False
            
        except Exception as e:
            results["test_passed"] = False
            results["errors"].append(f"Test failed with error: {str(e)}")
            print(f"❌ Test failed: {e}")
        
        return results
    
    def _categorize_dependencies(self, dependencies: List) -> Dict[str, int]:
        """Categorize dependencies by ecosystem and type"""
        counts = {
            "npm_total": 0,
            "pypi_total": 0,
            "npm_declared": 0,
            "npm_undeclared": 0,
            "pypi_declared": 0,
            "pypi_undeclared": 0,
            "total_missing": len(dependencies)
        }
        
        for dep in dependencies:
            if dep.ecosystem == "npm":
                counts["npm_total"] += 1
                if dep.file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    counts["npm_undeclared"] += 1
                else:
                    counts["npm_declared"] += 1
            elif dep.ecosystem == "pypi":
                counts["pypi_total"] += 1
                if dep.file_path.endswith('.py'):
                    counts["pypi_undeclared"] += 1
                else:
                    counts["pypi_declared"] += 1
        
        return counts
    
    def _compare_counts(self, expected: Dict[str, int], actual: Dict[str, int]) -> Dict[str, Any]:
        """Compare expected vs actual counts"""
        comparison = {
            "counts_match": True,
            "count_differences": {},
            "summary": {}
        }
        
        # Compare each expected count
        for key, expected_value in expected.items():
            actual_value = actual.get(key, 0)
            if expected_value != actual_value:
                comparison["counts_match"] = False
                comparison["count_differences"][key] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "difference": actual_value - expected_value
                }
        
        comparison["summary"] = {
            "total_expected": expected.get("total_fake_packages", 0),
            "total_actual": actual.get("total_missing", 0),
            "difference": actual.get("total_missing", 0) - expected.get("total_fake_packages", 0)
        }
        
        return comparison
    
    async def _check_test_package_existence(self) -> Dict[str, Any]:
        """Check if any of our test packages have been published"""
        print("🛡️  Checking test package integrity...")
        
        result = {
            "packages_published": False,
            "published_packages": [],
            "checked_packages": 0,
            "total_test_packages": 0
        }
        
        fake_packages = self.expected_manifest.get("fake_packages", {})
        
        for ecosystem, package_types in fake_packages.items():
            for package_type, package_list in package_types.items():
                for package_name in package_list:
                    result["total_test_packages"] += 1
                    result["checked_packages"] += 1
                    
                    # Check if package exists in registry
                    try:
                        exists = await self.package_checker.check_package_exists(package_name, ecosystem)
                        if exists:
                            result["packages_published"] = True
                            result["published_packages"].append({
                                "name": package_name,
                                "ecosystem": ecosystem,
                                "type": package_type,
                                "warning": "Test package has been published!"
                            })
                    except Exception as e:
                        print(f"Error checking {package_name}: {e}")
        
        return result
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable report"""
        report = ["=" * 50]
        report.append("📊 VIBEHAT SCAN CONSISTENCY REPORT")
        report.append("=" * 50)
        report.append(f"Test Status: {'✅ PASSED' if results['test_passed'] else '❌ FAILED'}")
        report.append(f"Timestamp: {results['timestamp']}")
        report.append("")
        
        # Expected vs Actual Counts
        report.append("📈 PACKAGE COUNTS:")
        expected = results["expected_counts"]
        actual = results["actual_counts"]
        
        report.append(f"  Total Expected: {expected.get('total_fake_packages', 0)}")
        report.append(f"  Total Found:    {actual.get('total_missing', 0)}")
        report.append(f"  Difference:     {actual.get('total_missing', 0) - expected.get('total_fake_packages', 0)}")
        report.append("")
        
        # Detailed breakdown
        for ecosystem in ["npm", "pypi"]:
            report.append(f"  {ecosystem.upper()}:")
            for count_type in ["declared", "undeclared", "total"]:
                key = f"{ecosystem}_{count_type}"
                exp = expected.get(key, 0)
                act = actual.get(key.replace('total', f'{ecosystem}_total'), 0)
                status = "✅" if exp == act else "⚠️"
                report.append(f"    {count_type:12}: {exp:3} expected, {act:3} actual {status}")
            report.append("")
        
        # Count differences
        if results.get("count_differences"):
            report.append("⚠️  COUNT DIFFERENCES:")
            for key, diff in results["count_differences"].items():
                report.append(f"  {key}: expected {diff['expected']}, got {diff['actual']} (diff: {diff['difference']})")
            report.append("")
        
        # Package existence check
        existence = results["package_existence_check"]
        report.append("🛡️  TEST PACKAGE INTEGRITY:")
        report.append(f"  Total test packages: {existence['total_test_packages']}")
        report.append(f"  Packages checked:    {existence['checked_packages']}")
        report.append(f"  Published packages:  {len(existence['published_packages'])}")
        
        if existence["published_packages"]:
            report.append("  ⚠️  ALERT: These test packages have been published:")
            for pkg in existence["published_packages"]:
                report.append(f"    - {pkg['name']} ({pkg['ecosystem']}) - {pkg['type']}")
        else:
            report.append("  ✅ All test packages remain unpublished")
        
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)

async def main():
    """Run the scan consistency test"""
    test = ScanConsistencyTest()
    results = await test.run_scan_consistency_test()
    
    # Generate and print report
    report = test.generate_report(results)
    print(report)
    
    # Save results to file
    results_path = Path(__file__).parent / "test_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_path}")
    
    # Exit with error code if test failed
    if not results["test_passed"]:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 