from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Dependency(BaseModel):
    name: str
    version: Optional[str] = None
    ecosystem: str  # npm, pypi, cargo, etc.
    file_path: str  # where it was found

class ScanRequest(BaseModel):
    repository_url: str

class ScanResult(BaseModel):
    id: int
    repository_url: str
    repository_owner: str
    repository_name: str
    total_dependencies: int
    missing_dependencies: int
    missing_packages: List[Dependency]
    created_at: datetime

class ExploitRequest(BaseModel):
    package_name: str
    ecosystem: str
    version: Optional[str] = "1.0.0" 