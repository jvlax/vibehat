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