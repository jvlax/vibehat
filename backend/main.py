from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx
import os
from typing import List, Optional
import re
import json

from database import get_db, engine
import models
import schemas
from github_scanner import GitHubScanner
from package_checker import PackageChecker
from package_publisher import PackagePublisher
from test_scan_consistency import ScanConsistencyTest

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VibeHat - AI Dependency Exploit Scanner")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
github_scanner = GitHubScanner(os.getenv("GITHUB_TOKEN"))
package_checker = PackageChecker()
package_publisher = PackagePublisher()

@app.get("/")
async def root():
    return {"message": "VibeHat API - Scanning for AI dependency exploits"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/scan/repository", response_model=schemas.ScanResult)
async def scan_repository(
    scan_request: schemas.ScanRequest,
    db: Session = Depends(get_db)
):
    """Scan a GitHub repository for missing dependencies"""
    try:
        # Parse repository URL
        repo_match = re.match(r'https://github\.com/([^/]+)/([^/]+)', scan_request.repository_url)
        if not repo_match:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")
        
        owner, repo = repo_match.groups()
        
        # Scan repository for dependencies
        dependencies = await github_scanner.scan_repository(owner, repo)
        
        # Check which packages don't exist
        missing_packages = []
        for dep in dependencies:
            exists = await package_checker.check_package_exists(dep.name, dep.ecosystem)
            if not exists:
                missing_packages.append(dep)
        
        # Save scan result to database
        scan_result = models.ScanResult(
            repository_url=scan_request.repository_url,
            repository_owner=owner,
            repository_name=repo,
            total_dependencies=len(dependencies),
            missing_dependencies=len(missing_packages),
            scan_data=json.dumps([dep.dict() for dep in missing_packages])
        )
        
        db.add(scan_result)
        db.commit()
        db.refresh(scan_result)
        
        return schemas.ScanResult(
            id=scan_result.id,
            repository_url=scan_result.repository_url,
            repository_owner=scan_result.repository_owner,
            repository_name=scan_result.repository_name,
            total_dependencies=scan_result.total_dependencies,
            missing_dependencies=scan_result.missing_dependencies,
            missing_packages=missing_packages,
            created_at=scan_result.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans", response_model=List[schemas.ScanResult])
async def get_scan_results(db: Session = Depends(get_db)):
    """Get all scan results"""
    results = db.query(models.ScanResult).order_by(models.ScanResult.created_at.desc()).all()
    
    scan_results = []
    for result in results:
        missing_packages = json.loads(result.scan_data) if result.scan_data else []
        scan_results.append(schemas.ScanResult(
            id=result.id,
            repository_url=result.repository_url,
            repository_owner=result.repository_owner,
            repository_name=result.repository_name,
            total_dependencies=result.total_dependencies,
            missing_dependencies=result.missing_dependencies,
            missing_packages=[schemas.Dependency(**pkg) for pkg in missing_packages],
            created_at=result.created_at
        ))
    
    return scan_results

@app.post("/exploit/generate")
async def generate_exploit_package(exploit_request: schemas.ExploitRequest):
    """Generate a proof-of-concept exploit package"""
    # This will create the actual malicious package
    # For now, just return the package structure
    return {
        "package_name": exploit_request.package_name,
        "ecosystem": exploit_request.ecosystem,
        "message": f"Exploit package '{exploit_request.package_name}' structure generated",
        "warning": "This is a proof-of-concept demonstration of dependency confusion vulnerability"
    }

@app.post("/publish/warning-package", response_model=schemas.PublishResult)
async def publish_warning_package(
    publish_request: schemas.PublishRequest,
    db: Session = Depends(get_db)
):
    """Publish a warning package to prevent dependency confusion attacks"""
    try:
        # Check if we can publish this package (doesn't already exist)
        can_publish = await package_publisher.check_if_can_publish(
            publish_request.package_name, 
            publish_request.ecosystem
        )
        
        if not can_publish:
            return schemas.PublishResult(
                success=False,
                package=publish_request.package_name,
                ecosystem=publish_request.ecosystem,
                message="Package already exists",
                error="Cannot publish: package already exists in registry"
            )
        
        # Publish the warning package
        result = await package_publisher.publish_warning_package(
            publish_request.package_name,
            publish_request.ecosystem,
            publish_request.source_file
        )
        
        # Save publication record to database
        if result.get("success"):
            exploit_package = models.ExploitPackage(
                package_name=publish_request.package_name,
                ecosystem=publish_request.ecosystem,
                version=result.get("version", "1.0.0"),
                published=True
            )
            db.add(exploit_package)
            db.commit()
        
        return schemas.PublishResult(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publish/batch-missing")
async def publish_batch_missing_packages(
    scan_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Publish warning packages for all missing dependencies from a scan"""
    try:
        # Get scan result
        scan_result = db.query(models.ScanResult).filter(models.ScanResult.id == scan_id).first()
        if not scan_result:
            raise HTTPException(status_code=404, detail="Scan result not found")
        
        missing_packages = json.loads(scan_result.scan_data) if scan_result.scan_data else []
        
        # Limit the number of packages we publish at once
        packages_to_publish = missing_packages[:limit]
        
        published_results = []
        for pkg_data in packages_to_publish:
            # Check if already published
            existing = db.query(models.ExploitPackage).filter(
                models.ExploitPackage.package_name == pkg_data["name"],
                models.ExploitPackage.ecosystem == pkg_data["ecosystem"]
            ).first()
            
            if existing:
                published_results.append({
                    "package": pkg_data["name"],
                    "ecosystem": pkg_data["ecosystem"],
                    "status": "already_published",
                    "success": True
                })
                continue
            
            # Publish warning package
            try:
                result = await package_publisher.publish_warning_package(
                    pkg_data["name"],
                    pkg_data["ecosystem"],
                    pkg_data.get("file_path", "Unknown")
                )
                
                if result.get("success"):
                    exploit_package = models.ExploitPackage(
                        package_name=pkg_data["name"],
                        ecosystem=pkg_data["ecosystem"],
                        version=result.get("version", "1.0.0"),
                        published=True
                    )
                    db.add(exploit_package)
                
                published_results.append({
                    "package": pkg_data["name"],
                    "ecosystem": pkg_data["ecosystem"],
                    "status": "published" if result.get("success") else "failed",
                    "success": result.get("success", False),
                    "error": result.get("error"),
                    "url": result.get("npm_url") or result.get("pypi_url")
                })
                
            except Exception as e:
                published_results.append({
                    "package": pkg_data["name"],
                    "ecosystem": pkg_data["ecosystem"],
                    "status": "error",
                    "success": False,
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "scan_id": scan_id,
            "total_missing": len(missing_packages),
            "attempted": len(packages_to_publish),
            "results": published_results,
            "summary": {
                "published": len([r for r in published_results if r["status"] == "published"]),
                "already_published": len([r for r in published_results if r["status"] == "already_published"]),
                "failed": len([r for r in published_results if r["status"] in ["failed", "error"]])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/scan-consistency")
async def run_scan_consistency_test():
    """Run scan consistency test to verify expected package counts and test integrity"""
    try:
        test = ScanConsistencyTest()
        results = await test.run_scan_consistency_test()
        
        # Add formatted report to the response
        report = test.generate_report(results)
        results["formatted_report"] = report
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/package-protection")
async def test_package_protection():
    """Test that our package protection system works correctly"""
    try:
        # Try to publish a test package (should be blocked)
        test_result = await package_publisher.publish_warning_package(
            "ai-super-helper",  # This is a test package from our manifest
            "npm",
            "test-protection-system"
        )
        
        return {
            "protection_test": "attempted_to_publish_test_package",
            "package_name": "ai-super-helper",
            "ecosystem": "npm", 
            "result": test_result,
            "expected_result": "should_be_blocked",
            "test_passed": not test_result.get("success", True)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 