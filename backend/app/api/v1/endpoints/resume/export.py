from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import tempfile
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.api.deps import get_current_user
from app.core.config import settings
from app.services.resume_exporter import (
    export_to_pdf,
    export_to_docx,
    export_to_json,
    export_to_txt
)

router = APIRouter()

@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    format: str = "original",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a resume in the specified format."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if format == "original":
        # Return the original file
        if not os.path.exists(resume.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original file not found"
            )
        return FileResponse(
            resume.file_path,
            filename=resume.file_name,
            media_type=resume.file_type
        )
    
    # Create a temporary directory for the export
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, f"resume_export_{resume.id}")
        
        if format == "pdf":
            file_path = await export_to_pdf(resume, export_path)
            media_type = "application/pdf"
        elif format == "docx":
            file_path = await export_to_docx(resume, export_path)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif format == "json":
            file_path = await export_to_json(resume, export_path)
            media_type = "application/json"
        elif format == "txt":
            file_path = await export_to_txt(resume, export_path)
            media_type = "text/plain"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}"
            )
        
        return FileResponse(
            file_path,
            filename=f"resume_export_{resume.id}.{format}",
            media_type=media_type
        )

@router.get("/{resume_id}/preview")
async def preview_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a preview of the resume content."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if not resume.analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume analysis not available"
        )
    
    # Return a simplified version of the resume content
    preview = {
        "title": resume.title,
        "summary": resume.analysis.get("summary", ""),
        "skills": resume.analysis.get("skills", [])[:5],  # Top 5 skills
        "experience": [
            {
                "company": exp.get("company", ""),
                "position": exp.get("position", ""),
                "duration": f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
            }
            for exp in resume.analysis.get("experience", [])[:3]  # Last 3 experiences
        ],
        "education": [
            {
                "institution": edu.get("institution", ""),
                "degree": edu.get("degree", ""),
                "field": edu.get("field_of_study", "")
            }
            for edu in resume.analysis.get("education", [])[:2]  # Last 2 education entries
        ]
    }
    
    return preview 