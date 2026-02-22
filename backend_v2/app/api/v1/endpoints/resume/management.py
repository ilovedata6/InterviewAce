from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone
import os

from app.db.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeList,
    ResumeStatus
)
from app.schemas.base import PaginatedResponse
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

@router.get(
    "/",
    response_model=PaginatedResponse[ResumeResponse],
    summary="List resumes",
    response_description="Paginated list of resumes owned by the authenticated user.",
)
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    status_filter: Optional[ResumeStatus] = Query(None, alias="status"),
    search: Optional[str] = None,
):
    """List all resumes for the current user with pagination and optional filtering.

    Filter by `status` (PENDING, COMPLETED, FAILED) or full-text `search` on title/description.
    """
    stmt = select(Resume).where(Resume.user_id == current_user.id)
    count_stmt = select(func.count()).select_from(Resume).where(Resume.user_id == current_user.id)
    
    if status_filter:
        stmt = stmt.where(Resume.status == status_filter)
        count_stmt = count_stmt.where(Resume.status == status_filter)
    
    if search:
        search_term = f"%{search}%"
        search_cond = (Resume.title.ilike(search_term)) | (Resume.description.ilike(search_term))
        stmt = stmt.where(search_cond)
        count_stmt = count_stmt.where(search_cond)
    
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()
    
    result = await db.execute(
        stmt.order_by(Resume.created_at.desc()).offset(skip).limit(limit)
    )
    resumes = result.scalars().all()
    
    return PaginatedResponse(
        items=resumes,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )

@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get a resume",
    response_description="Resume details.",
)
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific resume by ID.

    Raises:
        404: Resume not found or not owned by the user.
    """
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume

@router.put(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Update resume metadata",
    response_description="Updated resume details.",
)
async def update_resume(
    resume_id: str,
    resume_update: ResumeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update resume metadata (title, description).

    Raises:
        404: Resume not found or not owned by the user.
    """
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update fields
    for field, value in resume_update.dict(exclude_unset=True).items():
        setattr(resume, field, value)
    
    resume.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(resume)
    
    return resume

@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume",
    response_description="No content.",
)
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume and its associated file from disk.

    Raises:
        404: Resume not found or not owned by the user.
    """
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete the file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete the database record
    await db.delete(resume)
    await db.commit()