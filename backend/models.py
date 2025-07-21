from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_url = Column(String, nullable=False)
    repository_owner = Column(String, nullable=False)
    repository_name = Column(String, nullable=False)
    total_dependencies = Column(Integer, default=0)
    missing_dependencies = Column(Integer, default=0)
    scan_data = Column(Text)  # JSON string of missing packages
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ExploitPackage(Base):
    __tablename__ = "exploit_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, nullable=False, unique=True)
    ecosystem = Column(String, nullable=False)  # npm, pypi, etc.
    version = Column(String, default="1.0.0")
    published = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 