from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import shutil
import os

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeVersion, ResumeVersionList, ResumeResponse
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

@router.get("/{resume_id}/versions", response_model=ResumeVersionList)
async def list_resume_versions(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all versions of a resume."""
    # Get the latest version of the resume
    latest_resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not latest_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get all versions by following the parent_version_id chain
    versions = []
    current = latest_resume
    
    while current:
        versions.append(ResumeVersion(
            version=current.version,
            created_at=current.created_at,
            changes=current.analysis.get("changes", []) if current.analysis else [],
            parent_version_id=str(current.parent_version_id) if current.parent_version_id else None
        ))
        if current.parent_version_id:
            current = db.query(Resume).filter(Resume.id == current.parent_version_id).first()
        else:
            current = None
    
    return ResumeVersionList(
        versions=versions,
        current_version=latest_resume.version
    )

@router.post("/{resume_id}/create-version", response_model=ResumeResponse)
async def create_resume_version(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new version of a resume."""
    # Get the current version
    current_resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not current_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Create a copy of the file
    new_filename = f"{current_resume.file_name}_v{current_resume.version + 1}"
    new_file_path = os.path.join(settings.UPLOAD_DIR, new_filename)
    shutil.copy2(current_resume.file_path, new_file_path)
    
    # Create new version record
    new_version = Resume(
        user_id=current_user.id,
        title=current_resume.title,
        description=current_resume.description,
        file_path=new_file_path,
        file_name=new_filename,
        file_size=current_resume.file_size,
        file_type=current_resume.file_type,
        status=current_resume.status,
        analysis=current_resume.analysis,
        version=current_resume.version + 1,
        parent_version_id=current_resume.id
    )
    
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    
    return new_version

@router.get("/{resume_id}/version/{version_number}", response_model=ResumeResponse)
async def get_resume_version(
    resume_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific version of a resume."""
    # Get the latest version
    latest_resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not latest_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Find the requested version by following the parent_version_id chain
    current = latest_resume
    while current and current.version != version_number:
        if current.parent_version_id:
            current = db.query(Resume).filter(Resume.id == current.parent_version_id).first()
        else:
            current = None
    
    if not current:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found"
        )
    
    return current

@router.delete("/{resume_id}/version/{version_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_version(
    resume_id: str,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific version of a resume."""
    # Get the version to delete
    version = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.version == version_number
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found"
        )
    
    # Check if this is the latest version
    latest_version = db.query(Resume).filter(
        Resume.parent_version_id == resume_id
    ).first()
    
    if latest_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a version that has newer versions"
        )
    
    # Delete the file
    if os.path.exists(version.file_path):
        os.remove(version.file_path)
    
    # Delete the database record
    db.delete(version)
    db.commit()